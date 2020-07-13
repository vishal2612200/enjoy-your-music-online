from django import forms
from django.contrib.auth.models import User

from .models import Song, Playlist, Follow

class UserForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class SongForm(forms.ModelForm):

    class Meta:
        model = Song
        fields = ['song_title','audio_file','visibility','slug','artist']


class PlaylistForm(forms.ModelForm):

    class Meta:
        model = Playlist
        fields = ['visibility', 'playlist_title', 'genre', 'playlist_logo','slug']

class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ['following']

