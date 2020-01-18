from django.http import HttpResponse
from django.http import Http404
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.db.models import Count
from .models import *
import json
#from django.db import transaction
from . import UtilityOps as UtilityOps
from urllib.parse import urlparse
import hashlib
import requests

def hash_my_data(url):
	url = url.encode("utf-8")
	hash_object = hashlib.sha256(url)
	hex_dig = hash_object.hexdigest()
	return hex_dig


def findUnconfidentPuzzlePieces():
	import random
	#result = PuzzlePiece.objects.all()
	result = PuzzlePiece.objects.raw('SELECT * FROM collector_puzzlepiece WHERE id NOT IN (SELECT puzzlePiece_id FROM collector_confidentsolution) ' + \
					'AND id NOT IN (SELECT puzzlePiece_id FROM collector_badimage)')
	# Want less than a certain confidence.
	# X or more "bad image" records will disqualify from showing up again.
	#print(result.query)
	if len(result) > 0:
		index = random.randint(0, len(result)-1)
		# Add an isAmage that we'll reference in the template, this allows us to handle generic links
		if result[index].url.endswith(".jpg") or result[index].url.endswith(".png"):
			result[index].isImage = True
		else:
			result[index].isImage = False
		return result[index]
	return None


def index(request):
	template = loader.get_template("collector/index.html")
	return HttpResponse(template.render(None, request))


def puzzlepieceSubmit(request):
	responseMessage = None

	try:
		if request.method == "POST":
			url = request.POST["url"]
			host = urlparse(url).hostname
			if host in ["tjl.co","gamerdvr.com","dropbox.com","www.gamerdvr.com","www.dropbox.com"]:
				raise ValueError('We cannot accept images from gamerdvr or dropbox or tjl.co - try another host please, Discord works great!')
			res = requests.get(url)
			if res.status_code != 200:
				raise ValueError(url + ' -- That URL does not seem to exist. Please verify and try again.')

			newPiece = PuzzlePiece()
			newPiece.url = url
			newPiece.hash = hash_my_data(url)
			newPiece.ip_address = UtilityOps.UtilityOps.GetClientIP(request)
			newPiece.save()
			responseMessage = "Puzzle Piece image submitted successfully!"
	except KeyError as ex:
		responseMessage = "There was an issue with your request. Please try again?"
	except ValueError as ex:
		responseMessage = str(ex)
	except Exception as ex:
		if "unique" in str(ex).lower() or "duplicate" in str(ex).lower():
			responseMessage = "Looks like that puzzle piece image has already been submitted. Thanks for submitting!"
		else:
			responseMessage = "Something went wrong..." + str(ex)

	template = loader.get_template("collector/submit_piece.html")
	context = {
		"error_message": responseMessage
	}
	return HttpResponse(template.render(context, request))


class PuzzlepieceIndex(generic.ListView):
	template_name = 'collector/latest.html'
	context_object_name = 'latest'

	def get_queryset(self):
		return PuzzlePiece.objects.order_by("-submitted_date")[:50]


def puzzlepieceView(request, image_id):
	piece = get_object_or_404(PuzzlePiece, pk=image_id)
	if len(piece.hash) == 0 or "empty" == str(piece.hash).lower():
		piece.hash = hash_my_data(piece.url)
		piece.save()

	#transcriptions = TranscriptionData.objects.filter(puzzlePiece_id=image_id)

	context = {
		"puzzlepiece": piece,

	}
	#"transcriptions": transcriptions
	return render(request, 'collector/puzzlepieceDetail.html', context)


class TranscribeIndex(generic.ListView):
	template_name = 'collector/transcribe.html'
	context_object_name = 'puzzlepiece'

	def get_queryset(self):
		return findUnconfidentPuzzlePieces()


def processTranscription(request, puzzlepiece_id):
	data = None
	errors = None
	transcriptData = None

	if request.method == "POST":
		if "bad_image" in request.POST:
			bad_image = request.POST["bad_image"]
		else:
			bad_image = False
		data = request.POST["data"]
		try:
			data = json.loads(data)
		except Exception:
			data = None

		puzzlePiece = get_object_or_404(PuzzlePiece, pk=puzzlepiece_id)
		client_ip_address = UtilityOps.UtilityOps.GetClientIP(request)
		errors, transcriptData = processTransscriptionData(data, bad_image, puzzlePiece, client_ip_address)
		determineConfidence(puzzlepiece_id)

	context = {
		"data": data,
		"errors": errors,
		"transcript": transcriptData
	}
	return render(request, "collector/transcribeResults.html", context=context)



def processTransscriptionData(rawData, bad_image, puzzlePiece, client_ip_address):
	if bad_image and bool(bad_image) == True:
		transcriptData = TranscriptionData()
		transcriptData.ip_address = client_ip_address
		transcriptData.puzzlePiece = puzzlePiece
		transcriptData.bad_image = True
		transcriptData.datahash = "badimage"

		transcriptData.center = ""
		transcriptData.wall1 = False
		transcriptData.wall2 = False
		transcriptData.wall3 = False
		transcriptData.wall4 = False
		transcriptData.wall5 = False
		transcriptData.wall6 = False
		transcriptData.link1 = ""
		transcriptData.link2 = ""
		transcriptData.link3 = ""
		transcriptData.link4 = ""
		transcriptData.link5 = ""
		transcriptData.link6 = ""

		transcriptData.save()
		return [], transcriptData

	center = UtilityOps.UtilityOps.GetDictValues(rawData, "center", None)
	walls = UtilityOps.UtilityOps.GetDictValues(rawData, "walls", None)
	edges = UtilityOps.UtilityOps.GetDictValues(rawData, "nodes", None)

	errors = []
	if not center:
		errors.append("No center value was found in the JSON. This is required.")
	if walls and len(walls) != 6:
		errors.append("There should be 6 walls in the JSON. {} were found.".format(len(walls)))
	if edges and len(edges) != 6:
		errors.append("There should be 6 edges/nodes in the JSON. {} were found.".format(len(edges)))

	transcriptData = None
	if len(errors) == 0:
		# Prepare the Transcription Data
		transcriptData = TranscriptionData()
		transcriptData.bad_image = False
		transcriptData.ip_address = client_ip_address
		transcriptData.puzzlePiece = puzzlePiece
		transcriptData.center = center

		transcriptData.datahash = hash_my_data(str(rawData))

		transcriptData.wall1 = walls[0]
		transcriptData.wall2 = walls[1]
		transcriptData.wall3 = walls[2]
		transcriptData.wall4 = walls[3]
		transcriptData.wall5 = walls[4]
		transcriptData.wall6 = walls[5]

		linkJoiner = ""
		transcriptData.link1 = linkJoiner.join(edges[0])
		transcriptData.link2 = linkJoiner.join(edges[1])
		transcriptData.link3 = linkJoiner.join(edges[2])
		transcriptData.link4 = linkJoiner.join(edges[3])
		transcriptData.link5 = linkJoiner.join(edges[4])
		transcriptData.link6 = linkJoiner.join(edges[5])

		transcriptData.save()

	return errors, transcriptData


class TranscriptionsIndex(generic.ListView):
	template_name = 'collector/transcriptions.html'
	context_object_name = 'latest'

	def get_queryset(self):
		return TranscriptionData.objects.order_by("-submitted_date")[:50]


def transcriptionsDetail(request, transcription_id):
	transcription = get_object_or_404(TranscriptionData, pk=transcription_id)

	if not transcription.datahash:
		pass

	context = {
		"transcription": transcription,
		"puzzlepiece": transcription.puzzlePiece
	}
	return render(request, 'collector/transcriptionDetail.html', context)


class ConfidenceIndex(generic.ListView):
	model = ConfidenceTracking
	template_name = 'collector/confidenceIndex.html'
	context_object_name = 'latest'

def confidenceDetail(request, confidence_id):
	confidence = get_object_or_404(ConfidenceTracking, pk=confidence_id)

	if request.method == "POST":
		if "rerun" in request.POST:
			print("rerun")
			determineConfidence(confidence.puzzlePiece.id)
			confidence = get_object_or_404(ConfidenceTracking, pk=confidence_id)

	context = {
		"confidence": confidence,
	}
	return render(request, 'collector/confidenceDetail.html', context)


def determineConfidence(puzzlepieceId):
	data = TranscriptionData.objects.filter(puzzlePiece_id=puzzlepieceId)

	hashes = {}
	confidenceRatio = 70
	totalCount = len(data)
	badCount = 0
	badThreshold = 3

	# Is there enough data to determine a confidence level?
	# If no, create or update a tracker entry.
	if totalCount < 5:
		tracker = setOrUpdateConfidenceTracking(puzzlepieceId, totalCount)
		return

	for d in data:
		# Skip "bad image" flags.
		if d.bad_image:
			totalCount -= 1
			badCount += 1
			continue
		if d.datahash not in hashes:
			hashes[d.datahash] = 0
		hashes[d.datahash] = hashes[d.datahash] + 1
	if badCount >= badThreshold:
		setOrUpdateBadImage(puzzlepieceId, badCount)
		return
	# solution threshold count is...
	threshold = ((totalCount * confidenceRatio) / 100) - 5

	biggest = 0
	biggesthash = None
	if hashes:
		for hash, count in hashes.items():
			if count > biggest:
				biggest = count
				biggesthash = hash

		confidence = (biggest / totalCount) * 100
		# Update the confidence...
		tracker = setOrUpdateConfidenceTracking(puzzlepieceId, confidence)

		if biggest >= threshold:
			# find the first transcription data object with the hash...
			for d in data:
				if d.datahash == biggesthash:
					setOrUpdateConfidenceSolution(puzzlepieceId, confidence, d.id)
					break


def setOrUpdateBadImage(puzzlepieceId, badCount):
	try:
		bad = BadImage.objects.get(puzzlePiece_id=puzzlepieceId)
		bad = ConfidenceTracking.objects.filter(id=bad.id).update(badCount=badCount)
		return bad
	except Exception as ex:
		bad = None

	bad = BadImage()
	bad.puzzlePiece = get_object_or_404(PuzzlePiece, pk=puzzlepieceId)
	bad.badCount = badCount
	bad.save()
	return bad

def setOrUpdateConfidenceTracking(puzzlepieceId, confidence):
	try:
		tracker = ConfidenceTracking.objects.get(puzzlePiece_id=puzzlepieceId)
		tracker = ConfidenceTracking.objects.filter(id=tracker.id).update(confidence=confidence)
		return tracker
	except Exception as ex:
		tracker = None

	tracker = ConfidenceTracking()
	tracker.puzzlePiece = get_object_or_404(PuzzlePiece, pk=puzzlepieceId)
	tracker.confidence = confidence
	tracker.save()
	return tracker

def setOrUpdateConfidenceSolution(puzzlepieceId, confidence, transcriptiondataId):
	try:
		solution = ConfidentSolution.objects.get(puzzlePiece_id=puzzlepieceId)
		solution = ConfidentSolution.objects.filter(id=solution.id).update(
				confidence=confidence
		)
		return solution
	except Exception as ex:
		solution = None


	solution = ConfidentSolution()

	transcription = TranscriptionData.objects.get(id=transcriptiondataId)
	print("looking for {} and found {}".format(transcriptiondataId, transcription.id))
	solution.center = transcription.center
	solution.wall1 = transcription.wall1
	solution.wall2 = transcription.wall2
	solution.wall3 = transcription.wall3
	solution.wall4 = transcription.wall4
	solution.wall5 = transcription.wall5
	solution.wall6 = transcription.wall6

	solution.link1 = transcription.link1
	solution.link2 = transcription.link2
	solution.link3 = transcription.link3
	solution.link4 = transcription.link4
	solution.link5 = transcription.link5
	solution.link6 = transcription.link6

	solution.puzzlePiece = get_object_or_404(PuzzlePiece, pk=puzzlepieceId)

	solution.confidence = confidence
	solution.save()

	return solution

class ConfidenceSolutionIndex(generic.ListView):
	model = ConfidentSolution
	template_name = 'collector/confidenceSolutionIndex.html'
	context_object_name = "collection"


def confidenceSolutionDetail(request, solution_id):
	solution = get_object_or_404(ConfidentSolution, pk=solution_id)

	context = {
		"solution": solution,
	}
	return render(request, 'collector/confidenceSolutionDetail.html', context)
