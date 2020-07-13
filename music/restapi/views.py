from .serializers import *
from music.models import *
from rest_framework.generics import ListAPIView, RetrieveAPIView

"""
class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class PlaylistListView(ListAPIView):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
"""
class PlaylistListView(ListAPIView):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

class SongListView(ListAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

