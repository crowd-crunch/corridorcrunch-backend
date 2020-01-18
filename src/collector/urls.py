from django.urls import path

from . import views

urlpatterns = [
	path("", views.index, name="index"),
	path("puzzlepieces/submit", views.puzzlepieceSubmit, name="puzzlepieceSubmit"),
	path("puzzlepieces/", views.PuzzlepieceIndex.as_view(), name="puzzlepieceIndex"),
	path("puzzlepieces/<int:image_id>/", views.puzzlepieceView, name="puzzlepieceView"),
	path("transcriptions", views.TranscriptionsIndex.as_view(), name="transcriptions"),
	path("transcriptions/<int:transcription_id>", views.transcriptionsDetail, name="transcriptionsDetail"),
	path("transcribe", views.TranscribeIndex.as_view(), name="transcribe"),
	path("transcribe/<int:puzzlepiece_id>", views.processTranscription, name="transcribeResults"),
	path("confidence", views.ConfidenceIndex.as_view(), name="confidenceIndex"),
	path("confidence/<int:confidence_id>", views.confidenceDetail, name="confidenceDetail"),
	path("solutions", views.ConfidenceSolutionIndex.as_view(), name="confidenceSolutionIndex"),
	path("solutions/<int:solution_id>", views.confidenceSolutionDetail, name="confidenceSolutionDetail"),
]
