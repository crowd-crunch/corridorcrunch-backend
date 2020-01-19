from rest_framework import serializers
from . import models

class TranscriptionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TranscriptionData
        fields = [
            'puzzlePiece', 'bad_image', 'orientation', 'center',
            'wall1', 'wall2', 'wall3', 'wall4', 'wall5', 'wall6',
            'link1', 'link2', 'link3', 'link4', 'link5', 'link6',
        ]


class PuzzlePieceSerializer(serializers.ModelSerializer):
    badimages = serializers.SerializerMethodField(read_only=True)
    isImage = serializers.SerializerMethodField('check_if_image')

    class Meta:
        model = models.PuzzlePiece
        fields = [
            'id', 'url', 'approved',
            'confidences', 'confidentsolutions',
            'badimages', 'rotatedimages',
            'transCount', 'isImage'
        ]

    def get_badimages(self, piece):
        # check if queryset was annotated
        if hasattr(piece, 'badimage_count'):
            return piece.badimage_count

        # queryset wasn't annotated, do the slow thing
        if piece.badimages.count() > 0:
            return piece.badimages.first().badCount

        return 0
    
    def check_if_image(self, instance):
        normalised_url = instance.url.lower()
        # Very naïve check for direct image links.
        # If extending this, be _very_ careful about complexity, because
        # this computation is done on GET request for each PuzzlePiece
        # individually.
        if normalised_url.endswith(".jpg") or normalised_url.endswith(".png"):
            return True
        return False


class BadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BadImage
        fields = ['puzzlePiece', 'badCount']


class ConfidentSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PuzzlePiece
        fields = ['url', 'approved']
