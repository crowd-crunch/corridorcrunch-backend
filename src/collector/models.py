from django.db import models


class PuzzlePiece(models.Model):
	url = models.URLField(verbose_name="image url")
	hash = models.CharField(max_length=64, unique=True, default="empty", verbose_name="sha256 hash of the url")
	ip_address = models.CharField(max_length=64, default="?.?.?.?", verbose_name="hash of submitter ip address")
	submitted_date = models.DateTimeField(verbose_name="submitted date", auto_now_add=True)
	last_modified = models.DateTimeField(verbose_name="last modified date", auto_now=True)
	approved = models.NullBooleanField(verbose_name="is image approved for verification")
	transCount = models.PositiveIntegerField(default=0,verbose_name="Number of transcriptions received for this image")

	def __str__(self):
		data = []
		data.append("URL: {}".format(self.url))
		data.append("ip_address: {}".format(self.ip_address))
		data.append("submitted_date: {}".format(self.submitted_date))
		data.append("last_modified: {}".format(self.last_modified))
		data.append("hash: {}".format(self.hash))
		data.append("transCount: {}".format(self.transCount))

		result = ""
		for d in data:
			result += "<li>{}</li>".format(d)
		result = "<ul>" + result + "</ul>"
		return result


class TranscriptionData(models.Model):
	puzzlePiece = models.ForeignKey(PuzzlePiece, on_delete=models.CASCADE, related_name="transcriptions")
	ip_address = models.CharField(max_length=64, default="?.?.?.?", verbose_name="hash of submitter ip address")
	submitted_date = models.DateTimeField(verbose_name="submitted date", auto_now=True)

	bad_image = models.BooleanField(verbose_name="image is bad or hard to read")
	orientation = models.CharField(max_length=10, default="", verbose_name="orientation direction from image")
	rawdata = models.TextField(default="", verbose_name="Raw JSON taken in for later debugging.")
	datahash = models.CharField(max_length=64, default="", verbose_name="sha256 hash for easier comparisons")

	center = models.CharField(max_length=20, verbose_name="center")

	wall1 = models.BooleanField(verbose_name="wall 1 (top)")
	wall2 = models.BooleanField(verbose_name="wall 2 (top-right)")
	wall3 = models.BooleanField(verbose_name="wall 3 (bottom-right)")
	wall4 = models.BooleanField(verbose_name="wall 4 (bottom)")
	wall5 = models.BooleanField(verbose_name="wall 5 (bottom-left)")
	wall6 = models.BooleanField(verbose_name="wall 6 (top-left)")

	link1 = models.CharField(max_length=7, verbose_name="link 1 (top)")
	link2 = models.CharField(max_length=7, verbose_name="link 2 (top-right)")
	link3 = models.CharField(max_length=7, verbose_name="link 3 (bottom-right)")
	link4 = models.CharField(max_length=7, verbose_name="link 4 (bottom)")
	link5 = models.CharField(max_length=7, verbose_name="link 5 (bottom-left)")
	link6 = models.CharField(max_length=7, verbose_name="link 6 (top-left)")

	def __str__(self):
		return "{} {} {}".format(self.center, self.wall1, self.link1)


class BadImage(models.Model):
	puzzlePiece = models.ForeignKey(PuzzlePiece, on_delete=models.CASCADE, related_name="badimages")
	last_modified = models.DateTimeField(verbose_name="last modified date", auto_now=True)
	badCount = models.PositiveIntegerField(default=0,verbose_name="how often this image was reported as bad")

	class Meta:
		unique_together = ('id', 'puzzlePiece',)

class RotatedImage(models.Model):
	puzzlePiece = models.ForeignKey(PuzzlePiece, on_delete=models.CASCADE, related_name="rotatedimages")
	last_modified = models.DateTimeField(verbose_name="last modified date", auto_now=True)
	rotatedCount = models.PositiveIntegerField(default=0,verbose_name="how often this image was reported as incorrectly rotated")

	class Meta:
		unique_together = ('id', 'puzzlePiece',)

class ConfidenceTracking(models.Model):
	puzzlePiece = models.ForeignKey(PuzzlePiece, on_delete=models.CASCADE, related_name="confidences")
	last_modified = models.DateTimeField(verbose_name="last modified date", auto_now=True)
	confidence = models.PositiveIntegerField(default=0,verbose_name="how confident are we in this image, 0 to 100")

	class Meta:
		unique_together = ('id', 'puzzlePiece',)


class ConfidentSolution(models.Model):
	puzzlePiece = models.ForeignKey(PuzzlePiece, on_delete=models.CASCADE, related_name="confidentsolutions")
	last_modified = models.DateTimeField(verbose_name="last modified date", auto_now=True)
	confidence = models.PositiveIntegerField(default=0,verbose_name="how confident are we in this image, 0 to 100")

	center = models.CharField(max_length=20, verbose_name="center")

	wall1 = models.BooleanField(verbose_name="wall 1 (top)")
	wall2 = models.BooleanField(verbose_name="wall 2 (top-right)")
	wall3 = models.BooleanField(verbose_name="wall 3 (bottom-right)")
	wall4 = models.BooleanField(verbose_name="wall 4 (bottom)")
	wall5 = models.BooleanField(verbose_name="wall 5 (bottom-left)")
	wall6 = models.BooleanField(verbose_name="wall 6 (top-left)")

	link1 = models.CharField(max_length=7, verbose_name="link 1 (top)")
	link2 = models.CharField(max_length=7, verbose_name="link 2 (top-right)")
	link3 = models.CharField(max_length=7, verbose_name="link 3 (bottom-right)")
	link4 = models.CharField(max_length=7, verbose_name="link 4 (bottom)")
	link5 = models.CharField(max_length=7, verbose_name="link 5 (bottom-left)")
	link6 = models.CharField(max_length=7, verbose_name="link 6 (top-left)")

	def copyFromTranscription(self, transcription):
		self.puzzlePiece = transcription.puzzlePiece
		self.center = transcription.center
		self.wall1 = transcription.wall1
		self.wall2 = transcription.wall2
		self.wall3 = transcription.wall3
		self.wall4 = transcription.wall4
		self.wall5 = transcription.wall5
		self.wall6 = transcription.wall6

		self.link1 = transcription.link1
		self.link2 = transcription.link2
		self.link3 = transcription.link3
		self.link4 = transcription.link4
		self.link5 = transcription.link5
		self.link6 = transcription.link6
