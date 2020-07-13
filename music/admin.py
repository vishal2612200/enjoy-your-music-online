from django.contrib import admin
from .models import Song, Playlist, Follow

admin.site.register(Song)
admin.site.register(Playlist)
admin.site.register(Follow)
