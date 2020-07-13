from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.db.models import Q
from .models import Playlist, Song
from .forms import PlaylistForm, SongForm, UserForm, FollowForm
from django.core.files import File
import os
import requests

AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def index(request):
    create_default_playlist()
    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        playlists = Playlist.objects.filter(~Q(visibility ='Private')| Q(visibility = 'Private', user=request.user))
        song_results = Song.objects.all()
        query = request.GET.get("q")
        if query:
            playlists = playlists.filter(
                Q(playlist_title__icontains=query) |
                Q(user__icontains=query)
            ).distinct()
            song_results = song_results.filter(
                Q(song_title__icontains=query)
            ).distinct()
            return render(request, 'music/index.html', {
                'playlists': playlists,
                'songs': song_results,
            })
        else:
            return render(request, 'music/index.html', {'playlists': playlists})


def login_user(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
          if user.is_active:
              login(request, user)
              playlists = Playlist.objects.filter(user=request.user)
              return render(request,'music/index.html',{'playlists': playlists})
          else:
              return render(request, 'music/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'music/login.html', {'error_message': 'Invalid login'})
    return render(request, 'music/login.html')


def detail(request, playlist_id):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        user = request.user
        playlist = get_object_or_404(Playlist, pk=playlist_id)
        return render(request, 'music/detail.html', {'playlist': playlist, 'user': user})


def favorite(request, song_id):

    song = get_object_or_404(Song, pk=song_id)
    try:
        if song.is_favorite:
            song.is_favorite = False
        else:
            song.is_favorite = True
        song.save()
    except (KeyError, Song.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def favorite_playlist(request, playlist_id):

    playlist = get_object_or_404(Playlist, pk=playlist_id)
    try:
        if playlist.is_favorite:
            playlist.is_favorite = False
        else:
            playlist.is_favorite = True
        playlist.save()
    except (KeyError, Playlist.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def songs(request, filter_by):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        try:
            song_ids = []
            song_title_list = []
            songs_list = Song.objects.filter(~Q(visibility ='Private')| Q(visibility = 'Private', user=request.user)).order_by('visibility')
            for song in songs_list:
                if song not in song_title_list:
                    song_ids.append(song.pk)
                    song_title_list.append(song.song_title)
            """
            for song in Song.objects.filter(~Q(visibility ='Private')| Q(visibility = 'Private', user=request.user)):
                if song_title.count(song.song_title) !=0 in song_title and song.playlist.playlist_title != 'all_songs':           
                    song_ids.append(song.pk)
                    song_title.append(song.song_title)"""
            users_songs = Song.objects.filter(pk__in=song_ids)
            if filter_by == 'favorites':
                users_songs = users_songs.filter(is_favorite=True)
        except Playlist.DoesNotExist:
            users_songs = []
        return render(request, 'music/songs.html', {
            'song_list': users_songs,
            'filter_by': filter_by,
        })


def logout_user(request):

    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'music/login.html', context)


def register(request):

    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                playlists = Playlist.objects.filter(user=request.user)
                return render(request, 'music/index.html', {'playlists': playlists})
    context = {
        "form": form,
    }
    return render(request, 'music/register.html', context)


def create_playlist(request):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        form = PlaylistForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.playlist_logo = request.FILES['playlist_logo']
            file_type = playlist.playlist_logo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'playlist': playlist,
                    'form': form,
                    'error_message': 'The image must be PNG, JPG or JPEG'
                }
                return render(request, 'music/create_playlist.html', context)
            playlist.save()
            return render(request,'music/detail.html',{'playlist': playlist})
        context = {
            "form": form
        }
        return render(request, 'music/create_playlist.html', context)



def copy_song(request):
    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        form = SongForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            song = form.save(commit=False)
            song.user = request.user
            song.audio_file = request.FILES['audio_file']
            
            file_type = song.audio_file.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in AUDIO_FILE_TYPES:
                context = {
                    'form': form,
                    'error_message': 'Audio file must be WAV, MP3, or OGG',
                }
                return render(request, 'music/copy_song.html', context)
            song.save()
            return redirect("music:songs",filter_by='all')

        context = {
        'form': form,
        }
        return render(request, 'music/copy_song.html', context)




def create_song(request,playlist_id):

    form = SongForm(request.POST or None, request.FILES or None)
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    if form.is_valid():
        playlists_songs = playlist.song_set.all()
        for s in playlists_songs:
            if s.song_title == form.cleaned_data.get("song_title"):
                context = {
                    'playlist': playlist,
                    'form': form,
                    'error_message': 'You already added that song',
                }
                return render(request, 'music/create_song.html', context)
        song = form.save(commit=False)
        song.playlist = playlist
        song.user = request.user
        song.audio_file = request.FILES['audio_file']
        file_type = song.audio_file.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in AUDIO_FILE_TYPES:
            context = {
                'playlist': playlist,
                'form': form,
                'error_message': 'Audio file must be WAV, MP3, or OGG',
            }
            return render(request, 'music/create_song.html', context)

        song.save()
        return render(request, 'music/detail.html', {'playlist': playlist})
    context = {
        'playlist': playlist,
        'form': form,
    }
    return render(request, 'music/create_song.html', context)


def delete_playlist(request, playlist_id):

    playlist = Playlist.objects.get(pk=playlist_id)
    playlist.delete()
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'music/index.html', {'playlists': playlists})


def delete_song(request, playlist_id, song_id):

    playlist = get_object_or_404(Playlist, pk=playlist_id)
    song = Song.objects.get(pk=song_id)
    song.delete()
    return render(request, 'music/detail.html', {'playlist': playlist})



def follow(request):
    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        form = FollowForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            try:
                follow = Follow.objects.filter(user = request.user)
                print(follow)
            except:
                follow = form.save(commit=False)
                follow.user = request.user
                follow.save()
            print(form.cleaned_data)
            for i in form.cleaned_data['following']:
                follow.following.add(i)
            follow.following.add(request.user)
            return redirect("music:songs",filter_by='all')
        context = {
        'form': form,
        }
        return render(request, 'music/add_follow.html', context)


def transfer(request, playlist_id):
    all_songs = Song.objects.all()
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    if request.method == 'GET':
        return render(request, 'music/transfer.html', {
            "songs":all_songs,
            'playlist': playlist,
        })
    else:
        lst = request.POST.getlist("songs")
        print(lst)
        for song in lst:
            obj = Song.objects.get(pk=song)
            add = Song(
                playlist   = playlist,
                song_title = obj.song_title,
                artist     = obj.artist,
                audio_file = obj.audio_file,
                visibility = playlist.visibility,
                user   = request.user,
                slug       = obj.slug
                )
            add.save()
        return render(request, 'music/detail.html', {'playlist': playlist})

def create_default_playlist():
    try:
        Playlist.objects.filter(playlist_title='all_songs')[0]
    except:
        url = 'https://multifiles.pressherald.com/uploads/sites/10/2020/03/Music-Between-Us.jpg'
        r = requests.get(url)
        with open('default.jpg','wb') as f:
            f.write(r.content)
        f = File(open('default.jpg','rb'))
        obj = Playlist()
        obj.playlist_title = 'all_songs'
        obj.playlist_logo.save('default.jpg',f,save=True)
        obj.slug = 'all'
        obj.save()




