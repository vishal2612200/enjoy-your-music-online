from django.contrib.auth.models import Permission, User
from django.db import models

VISIBILITY_CHOICES = (
    ("Public", "Public"),
    ("Private", "Private"),
    ("Followers", "Followers"),
)

GENRE_CHOICES = (
    ("Unknown", "Unknown"),
    ("Movie", "Movie"),
    ("Pop", "Pop"),
    ("Rock", "Rock"),
    ("Alternative/Indie", "Alternative/Indie"),
    ("Remix", "Remix"),
    ("Instrumental", "Instrumental"),
    ("Folk", "Folk"),
    ("Electronic", "Electronic")
)

class Playlist(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,default=None, null=True,blank=True)
    visibility = models.CharField(max_length=100,
                             choices=VISIBILITY_CHOICES,
                             default=VISIBILITY_CHOICES[1][1])
    playlist_title = models.CharField(max_length=500)
    genre = models.CharField(max_length=100,
                             choices=GENRE_CHOICES,
                             default=GENRE_CHOICES[0][0])
    playlist_logo = models.FileField()
    is_favorite = models.BooleanField(default=False)
    slug = models.SlugField()

    def __str__(self):
        # changing the below line because for a playlist without user there will be no user_id
        # return self.playlist_title + '-' + str(self.user.id)
        try:
            return self.playlist_title + '-' + str(self.user.id)
        except:
            return self.playlist_title 


class Song(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE,blank=True, null=True,default='1')
    song_title = models.CharField(max_length=250)
    artist = models.CharField(max_length=250)
    audio_file = models.FileField(default='')
    is_favorite = models.BooleanField(default=False)
    visibility = models.CharField(max_length=100,
                             choices=VISIBILITY_CHOICES,
                             default=VISIBILITY_CHOICES[1][1])
    slug = models.SlugField()

    def __str__(self):
        return self.song_title

class Follow(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,unique=True,related_name='user')
    following = models.ManyToManyField(User)

    def __str__(self):
        return self.user.username

