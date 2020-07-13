from rest_framework import serializers
from music.models import *

"""
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
       model = Category
       fields = ('id', 'category_type', 'slug')

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ('id', 'playlist', 'is_display', 'slug')
"""
class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ('user', 'playlist_title', 'visibility', 'genre', 'playlist_logo', 'is_favorite')

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ( 'playlist', 'song_title', 'audio_file','is_favorite')




