from django.http import HttpResponse
from django.http import Http404
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.views.decorators.cache import cache_page
from django.db.models import Count, F, Max
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import *
from .serializers import (
    PuzzlePieceSerializer,
    TranscriptionDataSerializer,
    BadImageSerializer,
    ConfidentSolutionSerializer,
)
import json
#from django.db import transaction
from . import UtilityOps as UtilityOps
from urllib.parse import urlparse
from random import randint
import csv
import hashlib
import hmac
import requests
import re
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins, status, viewsets

# Regex pattern for text submissions
textSubmissionPattern = re.compile(r"^\s*(?P<center>(Blank|Plus|Clover|Hex|Snake|Diamond|Cauldron|B|P|C|H|S|D|T))\s*(?P<sides>([1-6])(\s*,\s*[1-6]){0,5})(?P<links>(\s*[BPCHSDT]{7}){6})\s*$", re.IGNORECASE)

def hash_my_data(url):
	url = url.encode("utf-8")
	hash_object = hashlib.sha256(url)
	hex_dig = hash_object.hexdigest()
	return hex_dig

# When exporting data, we shouldn't really make hash(ip) public because it's
# too easy to reverse. Use HMAC with SECRET_KEY as a keyed hash, to prevent
# reversing while still being usable as a unique identifier within a single
# exported set of data
def secretly_hash_my_data(data):
	key = settings.SECRET_KEY.encode("utf-8")
	data = data.encode("utf-8")
	hash_object = hmac.new(key, data, hashlib.sha256)
	hex_dig = hash_object.hexdigest()
	return hex_dig

def findImage(url):
	host = urlparse(url).hostname
	if host in ["imgur.com"]:
	# Can we be clever and figure out an Imgur URL on the fly?
		turl = "https://i.imgur.com" + urlparse(url).path + ".png"
		res = requests.head(turl)
		if res.status_code == 200:
			return turl
		turl = "https://i.imgur.com" + urlparse(url).path + ".jpg"
		res = requests.head(turl)
		if res.status_code == 200:
			return turl
		turl = "https://i.imgur.com" + urlparse(url).path + ".jpeg"
		res = requests.head(turl)
		if res.status_code == 200:
			return turl
		return None
	elif host in ["gyazo.com"]:
		turl = "https://i.gyazo.com" + urlparse(url).path + ".png"
		res = requests.head(turl)
		if res.status_code == 200:
			return turl
		turl = "https://i.gyazo.com" + urlparse(url).path + ".jpg"
		res = requests.head(turl)
		if res.status_code == 200:
			return turl
		turl = "https://i.gyazo.com" + urlparse(url).path + ".jpeg"
		res = requests.head(turl)
		if res.status_code == 200:
			return turl
		return None
	else:
		return None

def findUnconfidentPuzzlePieces(self):
	import random
	imgPoolSize = 100

	# We want to order by transCount descending to get faster results. We do not show anything definitely flagged as bad; that already has been solved
	# Allow multiple transcriptions by one person - at the current load the database query is just to expensive
	result = PuzzlePiece.objects.raw('SELECT * FROM collector_puzzlepiece WHERE id NOT IN (SELECT puzzlePiece_id FROM collector_confidentsolution) ' + \
					'AND id NOT IN (SELECT puzzlePiece_id FROM collector_badimage) ORDER BY priority DESC, transCount DESC')
	# Want less than a certain confidence.
	# X or more "bad image" records will disqualify from showing up again.
	#print(result.query)
	if len(result) > 0:
		#index = random.randint(0, len(result)-1)
		#Randomly one of the top N, imgPoolSize above
		index = random.randint(0, min(len(result)-1, imgPoolSize-1))
		# Add an isImage that we'll reference in the template, this allows us to handle generic links
		parsedUrl = urlparse(result[index].url)
		if parsedUrl.path.lower().endswith(".jpg") or parsedUrl.path.lower().endswith(".png") or parsedUrl.path.lower().endswith(".jpeg"):
			result[index].isImage = True
		else:
			result[index].isImage = False
		# Warn if rotateod
		rotated = PuzzlePiece.objects.raw('SELECT id FROM collector_rotatedimage WHERE puzzlePiece_id = ' + str(result[index].id))
		if rotated:
			result[index].isRotated = True
		else:
			result[index].isRotated = False
		return result[index]
	return None


@cache_page(60 * 15)
def index(request):
	template = loader.get_template("collector/index.html")
	return HttpResponse(template.render(None, request))

@cache_page(60 * 15)
def transcriptionGuide(request):
	template = loader.get_template("collector/transcriptionGuide.html")
	return HttpResponse(template.render(None, request))

def puzzlepieceSubmit(request):
	responseMessage = None
	responseMessageSuccess = None
	# New submissions are first in queue, but behind specific streamer requests
	priority = 10

	try:
		if request.method == "POST":
			url = request.POST["url"].strip()
			if len(url) > 200:
				raise ValueError('You havin\' a laff, mate? A URL that long? Yeah no.')
			host = urlparse(url).hostname
			if host not in ["cdn.discordapp.com", "media.discordapp.net", "i.gyazo.com", "gyazo.com", "i.imgur.com", "imgur.com"]:
				raise ValueError('We only accept images from cdn.discordapp.com, media.discordapp.net, (i.)gyazo.com and (i.)imgur.com right now.')
			if host not in ["gyazo.com", "imgur.com"] and not (url.lower().endswith(".jpg") or url.lower().endswith(".png") or url.lower().endswith(".jpeg")):
				raise ValueError('Please make sure your link ends with .jpg or .jpeg or .png. Direct links to images work best with our current site.')
			if host in ["gyazo.com", "imgur.com"]:
				turl = findImage(url)
				if turl:
					url = turl
			if url.find("http",8,len(url)) != -1:
				raise ValueError('Found http in the middle of the URL - did you paste it twice?' + url)
			res = requests.head(url)
			if res.status_code != 200:
				raise ValueError(url + ' -- That URL does not seem to exist. Please verify and try again.')

			newPiece = PuzzlePiece()
			newPiece.url = url
			newPiece.hash = hash_my_data(url)
			# An IP is personal data as per GDPR, kid you not. Let's hash it, we just need something unique
			newPiece.ip_address = hash_my_data(UtilityOps.UtilityOps.GetClientIP(request))
			newPiece.priority = priority
			newPiece.save()
			responseMessageSuccess = "Puzzle Piece image submitted successfully!"
	except KeyError as ex:
		responseMessage = "There was an issue with your request. Please try again?"
	except ValueError as ex:
		responseMessage = str(ex)
	except Exception as ex:
		if "unique" in str(ex).lower() or "duplicate" in str(ex).lower():
			responseMessage = "We already had that. Try another!"
		else:
			responseMessage = "Something went wrong..." + str(ex)

	template = loader.get_template("collector/submit_piece.html")
	context = {
		"error_message": responseMessage,
		"success_message": responseMessageSuccess,
	}
	return HttpResponse(template.render(context, request))

@method_decorator(cache_page(15 * 60), name='dispatch')
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
		return findUnconfidentPuzzlePieces(self)


def processTranscription(request, puzzlepiece_id):
	data = None
	errors = None
	transcriptData = None

	if request.method == "POST":
		if "bad_image" in request.POST:
			bad_image = request.POST["bad_image"]
		else:
			bad_image = False
		if "rotated_image" in request.POST:
			rotated_image = request.POST["rotated_image"]
		else:
			rotated_image = False
		data = request.POST["data"]
		try:
			data = json.loads(data)
		except Exception:
			match = textSubmissionPattern.match(data)
			if match:
				data = parse_data_string(match)
			else:
				data = None

		puzzlePiece = get_object_or_404(PuzzlePiece, pk=puzzlepiece_id)
		# Hash IP bcs of GDPR
		client_ip_address = hash_my_data(UtilityOps.UtilityOps.GetClientIP(request))
		errors, transcriptData = processTransscriptionData(data, bad_image, rotated_image, puzzlePiece, client_ip_address)
		determineConfidence(puzzlepiece_id)

	context = {
		"data": data,
		"errors": errors,
		"transcript": transcriptData
	}
	return render(request, "collector/transcribeResults.html", context=context)



def parse_data_string(matchedData):
    data_dict = {}

    # Sometimes the center is fully written out. Other times it is not.
    # This allows for both.
    data_dict["center"] = "T" if matchedData.group('center') == "Cauldron" else matchedData.group('center').upper()[0]

    # Wall list of length 6. Default is wall true, since string contains list of
    # openings.
    data_dict["walls"] = [True] * 6
    for opening in matchedData.group('sides').split(","):
        data_dict["walls"][int(opening) - 1] = False

    # Node list. Split string into list of strings, then split each side
    # into a list of characters.
    data_dict["nodes"] = []
    side_list = matchedData.group('links').split()
    for side in side_list:
        data_dict["nodes"].append(list(side.upper()))

    return data_dict



def processTransscriptionData(rawData, bad_image, rotated_image, puzzlePiece, client_ip_address):
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
		if rotated_image and bool(rotated_image) == True:
			transcriptData.orientation = "wrong"

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

		hashStr = center + ' ' + str(1 if walls[0] == True else 0) + str(1 if walls[1] == True else 0) + str(1 if walls[3] == True else 0) + \
			str(1 if walls[4] == True else 0) + str(1 if walls[4] == True else 0) + str(1 if walls[5] == True else 0) + ' ' + \
			transcriptData.link1 + ' ' + transcriptData.link2 + ' ' + transcriptData.link3 + ' ' + \
			transcriptData.link4 + ' ' + transcriptData.link5 + ' ' + transcriptData.link6

		transcriptData.datahash = hash_my_data(hashStr.upper())
		if rotated_image and bool(rotated_image) == True:                                                                                                                                                                                                                           transcriptData.orientation = "wrong"

		transcriptData.save()

	return errors, transcriptData

@method_decorator(cache_page(15 * 60), name='dispatch')
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


@method_decorator(cache_page(15 * 60), name='dispatch')
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
	confidenceRatio = 80
	rotatedConfidenceRatio = 90
	confidenceThreshold = 0 # We set this programmatically later
	minSubmissions = 10
	rotatedMinSubmissions = 15
	badCount = 0
	badThreshold = 4
	rotationCount = 0
	totalCount = len(data)
	updateTransCount(puzzlepieceId,totalCount)

	# Track bad images
	for d in data:
		if d.bad_image:
			badCount += 1
			continue

	if badCount >= badThreshold:
		setOrUpdateBadImage(puzzlepieceId, badCount)
		return

	# Track rotated images
	for d in data:
		if d.orientation == "wrong":
			rotationCount += 1
			continue

	if rotationCount > 0:
		setOrUpdateRotatedImage(puzzlepieceId, rotationCount)

	# Adjust totalCount, we will exclude bad Image submissions
	for d in data:
		if d.bad_image:
			totalCount -= 1
			continue

	# Is there enough data to determine a confidence level?
	# If no, create or update a tracker entry.
	if not rotationCount and totalCount < minSubmissions:
		tracker = setOrUpdateConfidenceTracking(puzzlepieceId, totalCount)
		return
	elif rotationCount and totalCount < rotatedMinSubmissions:
		tracker = setOrUpdateConfidenceTracking(puzzlepieceId, totalCount)
		return

	for d in data:
		if d.datahash not in hashes:
			hashes[d.datahash] = 0
		hashes[d.datahash] = hashes[d.datahash] + 1
	# solution confidence threshold is...
	if not rotationCount:
		confidenceThreshold = confidenceRatio
	else:
		confidenceThreshold = rotatedConfidenceRatio

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

		if confidence >= confidenceThreshold:
			# find the first transcription data object with the hash...
			for d in data:
				if d.datahash == biggesthash:
					setOrUpdateConfidenceSolution(puzzlepieceId, confidence, d.id)
					break


def updateTransCount(puzzlepieceId, transCount):
	try:
		piece = PuzzlePiece.objects.get(id=puzzlepieceId)
		piece = PuzzlePiece.objects.filter(id=piece.id).update(transCount=transCount)
		return piece
	except Exception as ex:
		piece = None

def setOrUpdateBadImage(puzzlepieceId, badCount):
	try:
		bad = BadImage.objects.get(puzzlePiece_id=puzzlepieceId)
		bad = BadImage.objects.filter(id=bad.id).update(badCount=badCount)
		return bad
	except Exception as ex:
		bad = None

	bad = BadImage()
	bad.puzzlePiece = get_object_or_404(PuzzlePiece, pk=puzzlepieceId)
	bad.badCount = badCount
	bad.save()
	return bad

def setOrUpdateRotatedImage(puzzlepieceId, rotationCount):
	try:
		rotated = RotatedImage.objects.get(puzzlePiece_id=puzzlepieceId)
		rotated = RotatedImage.objects.filter(id=rotated.id).update(rotatedCount=rotationCount)
		return rotated
	except Exception as ex:
		rotated = None

	rotated = RotatedImage()
	rotated.puzzlePiece = get_object_or_404(PuzzlePiece, pk=puzzlepieceId)
	rotated.rotatedCount = rotationCount
	rotated.save()
	return rotated

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

	solution.datahash = transcription.datahash
	solution.puzzlePiece = get_object_or_404(PuzzlePiece, pk=puzzlepieceId)

	solution.confidence = confidence
	solution.save()

	return solution

@method_decorator(cache_page(15 * 60), name='dispatch')
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


class PuzzlePieceViewSet(viewsets.ReadOnlyModelViewSet):
    # annotate badimages count for serializer performance
    queryset = PuzzlePiece.objects.all().annotate(
        badimage_count=Max('badimages__badCount'),
    )
    serializer_class = PuzzlePieceSerializer

    @action(detail=False)
    def get_random(self, request):
        qs = PuzzlePiece.objects.annotate(
            transcription_count=Count('transcriptions'),
        ).filter(transcription_count__lt=5)
        count = qs.aggregate(count=Count('pk'))['count']
        print(count)
        if count < 1:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        random_index = randint(0, count - 1)
        rando = qs[random_index]
        serializer = self.get_serializer(rando)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def report(self, request, *args, **kwargs):
        piece = self.get_object()
        if piece.badimages.count() > 0:
            # atomic increment of the count on all existing BadImages
            piece.badimages.update(badCount=F('badCount')+1)
        else:
            # create a BadImage... might have a race condition :(
            bad = BadImage(puzzlePiece=piece, badCount=1)
            bad.save()

        # go ahead and return the updated piece
        piece = self.get_object()
        serializer = self.get_serializer(piece)
        return Response(serializer.data)


class TranscriptionDataViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = TranscriptionData.objects.all()
    serializer_class = TranscriptionDataSerializer

    # copied code from the mixin, but we need access to request here
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # TODO: ALSO MAKE HASH

        # ip_address in kwargs here *should* put it in?
        serializer.save(ip_address=ip)

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

@cache_page(60 * 15)
def exportVerifiedCSV(request):
	response = HttpResponse(content_type = 'text/csv')
	response['Content-Disposition'] = 'attachment; filename="verified.csv"'
	writer = csv.writer(response)

	writer.writerow([
		"Image",
		"Center",
		"Openings",
		"Link1",
		"Link2",
		"Link3",
		"Link4",
		"Link5",
		"Link6",
		"Confidence",
		"Transcription hash",
		"Transcription count",
		"Incorrect Rotation Flag"
	])

	for solution in ConfidentSolution.objects.all():
		walls = [solution.wall1, solution.wall2, solution.wall3, solution.wall4, solution.wall5, solution.wall6]
		openings = ",".join(str(i+1) for i in range(6) if not walls[i])

		rotated = PuzzlePiece.objects.raw('SELECT id FROM collector_rotatedimage WHERE puzzlePiece_id = ' + str(solution.puzzlePiece.id))
		if rotated:
			solution.rotated = True
		else:
			solution.rotated = False
		writer.writerow([
			solution.puzzlePiece.url,
			solution.center,
			openings,
			solution.link1,
			solution.link2,
			solution.link3,
			solution.link4,
			solution.link5,
			solution.link6,
			solution.confidence,
			solution.datahash,
			solution.puzzlePiece.transCount,
			solution.rotated
		])

	return response

@cache_page(60 * 30)
def exportPiecesCSV(request):
	response = HttpResponse(content_type = 'text/csv')
	response['Content-Disposition'] = 'attachment; filename="imgurls.csv"'
	writer = csv.writer(response)

	writer.writerow([
		"Image",
		"Submitter",
		"Submitted date",
		"Last modified",
		"Transcription count"
	])

	for piece in PuzzlePiece.objects.all():
		writer.writerow([
			piece.url,
			secretly_hash_my_data(piece.ip_address),
			piece.submitted_date,
			piece.last_modified,
			piece.transCount
		])

	return response

@cache_page(60 * 15)
def exportTranscriptionsCSV(request):
	response = HttpResponse(content_type = 'text/csv')
	response['Content-Disposition'] = 'attachment; filename="transcriptions.csv"'
	writer = csv.writer(response)

	writer.writerow([
		"Image",
		"Submitter",
		"Submitted date",
		"Bad image",
		"Orientation",
		"Center",
		"Openings",
		"Link1",
		"Link2",
		"Link3",
		"Link4",
		"Link5",
		"Link6",
		"Transcription hash"
	])

	for trans in TranscriptionData.objects.all():
		walls = [trans.wall1, trans.wall2, trans.wall3, trans.wall4, trans.wall5, trans.wall6]
		openings = ",".join(str(i+1) for i in range(6) if not walls[i])

		writer.writerow([
			trans.puzzlePiece.url,
			secretly_hash_my_data(trans.ip_address),
			trans.submitted_date,
			trans.bad_image,
			trans.orientation,
			trans.center,
			openings,
			trans.link1,
			trans.link2,
			trans.link3,
			trans.link4,
			trans.link5,
			trans.link6,
			trans.datahash
		])

	return response
