from django.urls import include, path
from rest_framework import routers

from . import views

api_router = routers.DefaultRouter()
api_router.register(r'pieces', views.PuzzlePieceViewSet)
api_router.register(r'transcriptions', views.TranscriptionDataViewSet)

urlpatterns = [
	path("", views.index, name="index"),
        path('api/', include(api_router.urls)),
	path("puzzlepieces/submit", views.puzzlepieceSubmit, name="puzzlepieceSubmit"),
	path("puzzlepieces/", views.PuzzlepieceIndex.as_view(), name="puzzlepieceIndex"),
	path("puzzlepieces/<int:image_id>/", views.puzzlepieceView, name="puzzlepieceView"),
	path("transcriptions", views.TranscriptionsIndex.as_view(), name="transcriptions"),
	path("transcriptions/<int:transcription_id>", views.transcriptionsDetail, name="transcriptionsDetail"),
	path("transcriptions/guide", views.transcriptionGuide, name="transcriptionGuide"),
	path("transcribe", views.TranscribeIndex.as_view(), name="transcribe"),
	path("transcribe/<int:puzzlepiece_id>", views.processTranscription, name="transcribeResults"),
	path("confidence", views.ConfidenceIndex.as_view(), name="confidenceIndex"),
	path("confidence/<int:confidence_id>", views.confidenceDetail, name="confidenceDetail"),
	path("solutions", views.ConfidenceSolutionIndex.as_view(), name="confidenceSolutionIndex"),
	path("solutions/<int:solution_id>", views.confidenceSolutionDetail, name="confidenceSolutionDetail"),
	path("export/verified/csv", views.exportVerifiedCSV, name="exportVerifiedCSV"),
	path("export/pieces/csv", views.exportPiecesCSV, name="exportPiecesCSV"),
	path("export/transcriptions/csv", views.exportTranscriptionsCSV, name="exportTranscriptionsCSV"),
]
