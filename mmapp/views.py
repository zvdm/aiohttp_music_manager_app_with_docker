import datetime
import os
import aiohttp_jinja2
from aiohttp import web
from pathlib import Path

from .db import *
from .forms import validate_user_form, validate_track_form

routes = web.RouteTableDef()
BASE_DIR = Path(__file__).parent.parent
upload_path = BASE_DIR / 'mmapp' / 'uploads'


@routes.view('/')
class Index(web.View):
    async def get(self):
        return web.HTTPPermanentRedirect('/user')


@routes.view('/user')
class User(web.View):
    @aiohttp_jinja2.template('user_detail.html')
    async def get(self):
        api_key = self.request.cookies['api_key']
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, api_key)
        # Get user's albums by user's id
        albums = await get_user_albums_by_api_key(self.request, user[0])
        # Get user's tracks by user's id
        tracks = await get_user_tracks_by_api_key(self.request, user[0])
        print('albums for user page', albums)
        print('tracks for user page', tracks)
        return {
            'user':
                {
                    'info': user,
                    'albums': albums,
                    'tracks': tracks
                }
        }

    async def post(self):
        data = await self.request.post()
        # Check if marker is delete user
        if 'delete' in data:
            result = await delete_user(self.request)
            print('DELETE USER', result)
            return web.HTTPSeeOther('/')
        # Else update information about user
        result = await validate_user_form(self.request, data)
        print(result)
        return web.HTTPSeeOther('/user')


@routes.view('/albums')
class Albums(web.View):
    @aiohttp_jinja2.template('album_detail.html')
    async def get(self):
        api_key = self.request.cookies['api_key']
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, api_key)
        # Get user's albums by user's id
        albums = await get_user_albums_by_api_key(self.request, user[0])
        # Get user's tracks by user's id
        tracks = await get_user_tracks_by_api_key(self.request, user[0])
        return {
            'user': user[1],
            'albums': albums,
            'tracks': tracks
        }

    async def post(self):
        data = await self.request.post()
        user = await get_user_by_api_key(self.request, self.request.cookies['api_key'])

        # Check if marker is delete album
        if 'delete' in data:
            # Get all tracks id by album id
            result_tr = await delete_tracks_by_album_id(self.request, int(data['delete']), user['id'])
            result_alb = await delete_album(self.request, int(data['delete']), user['id'])
            for track in result_tr:
                os.remove(track[1])
            print('DELETE ALBUM', result_alb)
            print('DELETE TRACKS', result_tr)
            return web.HTTPSeeOther('/albums')

        # Create new album
        title = data['title']
        list_of_tracks = list(data.values())
        del(list_of_tracks[0])
        # Create new album in db
        row_alb = await create_album(self.request, title, datetime.datetime.now(), user['id'])
        # Add album id (foreign key) to appropriate tracks
        await update_add_track_item_to_album(self.request, row_alb[0], list_of_tracks, user['id'])

        return web.HTTPSeeOther('/albums')


@routes.view(r'/album/{title:\w+}')
class AlbumItem(web.View):
    @aiohttp_jinja2.template('album_item_detail.html')
    async def get(self):
        api_key = self.request.cookies['api_key']
        # Get track name from url
        title = self.request.match_info['title']
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, api_key)
        # Check that this track exists in db
        album = await get_user_album_by_title_and_api_key(self.request, title, user['id'])
        # Get all tracks included in album
        tracks_in_album = await get_user_tracks_by_album_id_and_api_key(self.request, album['id'], user['id'], 'in')
        # Get all another tracks
        tracks_not_in_album = await get_user_tracks_by_album_id_and_api_key(self.request, album['id'], user['id'], 'out')

        print(tracks_in_album)
        print(tracks_not_in_album)

        return {
            'title': album['title'],
            'tracks_in_album': tracks_in_album,
            'tracks_not_in_album': tracks_not_in_album
        }

    async def post(self):
        data = await self.request.post()
        print(data)
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, self.request.cookies['api_key'])
        old_title = self.request.match_info['title']

        if 'delete' in data:
            result = await delete_track_from_album(self.request, int(data['delete']), user['id'])
            print('DELETE TRACK FROM ALBUM', result)
            return web.HTTPSeeOther(f'/album/{self.request.match_info["title"]}')
        if 'checked' in data:
            list_of_tracks = list(data.values())
            print(list_of_tracks)
            # Add album id (foreign key) to appropriate tracks
            row = await get_user_album_by_title_and_api_key(self.request, old_title, user['id'])
            await update_add_track_item_to_album(self.request, row[0], list_of_tracks, user['id'])
            return web.HTTPSeeOther(f'/album/{self.request.match_info["title"]}')

        # Update album title
        row = await update_album_name(self.request, data['title'], old_title, user['id'])
        return web.HTTPSeeOther(f'/album/{data["title"]}')


@routes.view('/tracks')
class Tracks(web.View):
    @aiohttp_jinja2.template('track_detail.html')
    async def get(self):
        api_key = self.request.cookies['api_key']
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, api_key)
        # Get user's tracks by user's id
        tracks = await get_user_tracks_by_api_key(self.request, user[0])
        return {
            'user': user[1],
            'tracks': tracks,
        }

    async def post(self):
        data = await self.request.post()
        # Check if marker is delete track
        if 'delete' in data:
            user = await get_user_by_api_key(self.request, self.request.cookies['api_key'])
            result = await delete_track(self.request, int(data['delete']), user['id'])
            print(result)
            os.remove(result[1])
            print('DELETE TRACK', result)
            return web.HTTPSeeOther('/tracks')


@routes.view(r'/track/{title:\w+.mp3}')
class TrackItem(web.View):
    @aiohttp_jinja2.template('track_item_detail.html')
    async def get(self):
        api_key = self.request.cookies['api_key']
        # Get track name from url
        title = self.request.match_info['title']
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, api_key)
        # Check that this track exists in db
        track = await get_track_item(self.request, title, user['id'])
        albums = await get_user_album_by_id_and_api_key(self.request, track['album_id'], user['id'])
        return {
            'title': track['title'],
            'albums': albums
        }

    async def post(self):
        data = await self.request.post()
        old_title = self.request.match_info['title']

        # Update track title
        row = await validate_track_form(self.request, data['title'], old_title, upload_path)
        return web.HTTPSeeOther(f'/track/{data["title"]}')


@routes.post('/track/upload')
async def track_upload(request):
    reader = await request.multipart()
    field = await reader.next()
    assert field.name == 'mp3'
    filename = field.filename
    if not filename.endswith('.mp3'):
        return web.HTTPSeeOther('/track')

    user = await get_user_by_api_key(request, request.cookies['api_key'])

    # Check if file with this title exists
    row = await get_user_track_by_title_and_api_key(request, filename, user['id'])
    if row:
        return web.HTTPSeeOther('/tracks')

    size = 0
    filename_for_dir = f'{user["id"]}-{filename}'
    saved_dir = os.path.join(upload_path, filename_for_dir)
    with open(saved_dir, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)

    date_time = datetime.datetime.now()
    result = await create_track(request, filename, date_time, saved_dir, user[0])
    return web.HTTPSeeOther('/tracks')
