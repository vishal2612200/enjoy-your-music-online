from django.urls import path, include
from .views import *


urlpatterns = [
    path('playlist/', PlaylistListView.as_view()),
    path('song/', SongListView.as_view())
]
