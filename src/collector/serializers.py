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
    class Meta:
        model = models.PuzzlePiece
        fields = ['id', 'url', 'approved', 'confidences', 'confidentsolutions', 'badimages', 'rotatedimages', 'transCount']


class BadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BadImage
        fields = ['puzzlePiece', 'badCount']


class ConfidentSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PuzzlePiece
        fields = ['url', 'approved']
