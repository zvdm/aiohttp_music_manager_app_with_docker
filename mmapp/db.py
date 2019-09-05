import asyncpg
import hashlib
import uuid

salt = '3D4M'


# async def create_db():
#     conn = await asyncpg.connect('postgresql://mmapp@localhost/mmappdb', password='mmapp1234')
async def create_db():
        conn = await asyncpg.connect(host='mmappdb', user='mmapp', password='mmapp1234', database='mmappdb')
    # async with app['db'].acquire() as conn:
        await conn.execute('''
                    CREATE TABLE IF NOT EXISTS Users(
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL,
                        pwd TEXT NOT NULL,
                        email TEXT,
                        age INTEGER,
                        location TEXT,
                        api_key UUID UNIQUE NOT NULL,
                        created_date TIMESTAMP NOT NULL,
                        active_status BOOL NOT NULL
                    );
    
                    CREATE TABLE IF NOT EXISTS Albums(
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        created_date TIMESTAMP NOT NULL,
                        user_id INTEGER NOT NULL
                    );
    
                    CREATE TABLE IF NOT EXISTS Tracks(
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        created_date TIMESTAMP NOT NULL,
                        saved_dir TEXT,
                        album_id INTEGER,
                        user_id INTEGER NOT NULL
                    );
                ''')
        # await conn.close()


# USERS SECTION
async def user_signup(conn, new_user, clear_pwd, date_time, active_status):
    pwd = hashlib.sha256((clear_pwd + salt).encode()).hexdigest()
    row = await conn.execute('INSERT INTO Users'
                             '(name, pwd, api_key, created_date, active_status)'
                             'VALUES ($1,$2,$3,$4,$5)'
                             'ON CONFLICT (name) DO NOTHING',
                             new_user, pwd, uuid.uuid4(), date_time, active_status)
    result = [0]
    if int(row.split()[2]) > 0:
        result = await conn.fetchrow('SELECT api_key FROM Users WHERE name=$1', new_user)
    return result[0]


async def user_login(conn, username, clear_pwd):
    pwd = hashlib.sha256((clear_pwd + salt).encode()).hexdigest()
    result = await conn.fetchrow('SELECT api_key FROM Users WHERE name=$1 AND pwd=$2', username, pwd)
    return result[0]


async def get_user_by_api_key(request, api_key):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetchrow('SELECT id, name, email, age, location, active_status FROM Users WHERE api_key=$1', api_key)
        return row


async def get_user_by_name(request, name):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetchrow('SELECT id, api_key, location FROM Users WHERE name=$1', name)
        return row


async def update_user_info(request, info, api_key):
    count = 0
    if 'name' in info:
        # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].execute('UPDATE Users SET name=$1 WHERE api_key=$2', info['name'], api_key)
        count += int(row.split(' ')[1])
    if 'pwd' in info:
        info['pwd'] = hashlib.sha256((info['pwd'] + salt).encode()).hexdigest()
        # async with request.app['db'].aquire() as conn:
        row = await request.app['db'].execute('UPDATE Users SET pwd=$1 WHERE api_key=$2', info['pwd'], api_key)
        count += int(row.split(' ')[1])
    # async with request.app['db'].acquire() as conn:
    row = await request.app['db'].execute('UPDATE Users SET email=$1, age=$2, location=$3 WHERE api_key=$4',
                                 info['email'], info['age'], info['location'], api_key)
    count += int(row.split(' ')[1])
    return f'UPDATE {count}'


async def delete_user(request):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].execute('UPDATE Users SET active_status=false WHERE api_key=$1', request.cookies['api_key'])
        return row


# ALBUMS SECTION
async def create_album(request, title, date_time, user_id):
    # async with request.app['db'].acquire() as conn:
        await request.app['db'].execute('INSERT INTO Albums'
                           '(title, created_date, user_id)'
                           'VALUES ($1,$2,$3)',
                           title, date_time, user_id)
        row = await request.app['db'].fetchrow('SELECT id, title FROM Albums WHERE title=$1 AND user_id=$2', title, user_id)
        return row


async def get_user_albums_by_api_key(request, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetch('SELECT id, title FROM Albums WHERE user_id=$1', user_id)
        return row


async def get_user_album_by_id_and_api_key(request, id, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetchrow('SELECT id, title FROM Albums WHERE id=$1 AND user_id=$2', id, user_id)
        return row


async def get_user_album_by_title_and_api_key(request, title, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetchrow('SELECT id, title FROM Albums WHERE title=$1 AND user_id=$2', title, user_id)
        return row


async def update_album_name(request, new_title, old_title, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetchrow('UPDATE Albums SET title=$1 WHERE title=$2 AND user_id=$3',
                                  new_title, old_title, user_id)
        return row


async def delete_album(request, id, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].execute('DELETE FROM Albums WHERE id=$1 AND user_id=$2', id, user_id)
        return row


# TRACKS SECTION
async def create_track(request, filename, date_time, saved_dir, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].execute('INSERT INTO Tracks'
                                 '(title, created_date, saved_dir, user_id)'
                                 'VALUES ($1,$2,$3,$4)',
                                 filename, date_time, saved_dir, user_id)
        return row


async def get_user_tracks_by_api_key(request, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetch('SELECT id, title FROM Tracks WHERE user_id=$1', user_id)
        return row


async def get_user_tracks_by_album_id_and_api_key(request, album_id, user_id, in_out):
    # async with request.app['db'].acquire() as conn:
        if in_out == 'in':
            row = await request.app['db'].fetch('SELECT id, title FROM Tracks WHERE album_id=$1 AND user_id=$2', album_id, user_id)
        else:
            row = await request.app['db'].fetch('SELECT id, title FROM Tracks WHERE album_id IS DISTINCT FROM $1 AND user_id=$2', album_id, user_id)
        return row


async def get_user_track_by_title_and_api_key(request, title, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetchrow('SELECT id, title FROM Tracks WHERE title=$1 AND user_id=$2', title, user_id)
        return row


async def get_track_item(request, title, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetchrow('SELECT id, title, album_id, saved_dir FROM Tracks WHERE title=$1 AND user_id=$2', title, user_id)
        return row


async def update_track_item(request, new_title, old_title, new_saved_dir, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetchrow('UPDATE Tracks SET title=$1, saved_dir=$2 WHERE title=$3 AND user_id=$4',
                                  new_title, new_saved_dir, old_title, user_id)
        return row


async def update_add_track_item_to_album(request, album_id, list_of_track, user_id):
    # async with request.app['db'].acquire() as conn:
        for track in list_of_track:
            await request.app['db'].fetchrow('UPDATE Tracks SET album_id=$1 WHERE title=$2 AND user_id=$3',
                                album_id, track, user_id)


async def delete_track(request, id, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetchrow('SELECT id, saved_dir FROM Tracks WHERE id=$1 AND user_id=$2', id, user_id)
        await request.app['db'].execute('DELETE FROM Tracks WHERE id=$1 AND user_id=$2', id, user_id)
        return row


async def delete_tracks_by_album_id(request, album_id, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].fetch('SELECT id, saved_dir FROM Tracks WHERE album_id=$1 AND user_id=$2', album_id, user_id)
        await request.app['db'].execute('DELETE FROM Tracks WHERE album_id=$1 AND user_id=$2', album_id, user_id)
        return row


async def delete_track_from_album(request, id, user_id):
    # async with request.app['db'].acquire() as conn:
        row = await request.app['db'].execute('UPDATE Tracks SET album_id=NULL WHERE id=$1 AND user_id=$2', id, user_id)
        return row


# from sqlalchemy import (get_user_tracks_by_api_key
#     MetaData, Table, Column, ForeignKey,
#     Integer, String, DateTime, Boolean
# )
# from sqlalchemy.dialects.postgresql import UUID
#
#
# meta = MetaData()
#
# users = Table(
#     'users', meta,
#
#     Column('id', Integer, primary_key=True),
#     Column('name', String(50), nullable=False, unique=True),
#     Column('password', String(200), nullable=False),
#     Column('email', String(100)),
#     Column('location', String(50)),
#     Column('api_key', UUID, nullable=False),
#     Column('created_date', DateTime, nullable=False),
#     Column('active_status', Boolean, nullable=False)
# )
#
# albums = Table(
#     'albums', meta,
#
#     Column('id', Integer, primary_key=True),
#     Column('name', String(100), nullable=False),
#     Column('created_date', DateTime, nullable=False),
#     Column('user_id', Integer, ForeignKey('users.id', ondelete='SET NULL'))
# )
#
# tracks = Table(
#     'tracks', meta,
#
#     Column('id', Integer, primary_key=True),
#     Column('name', String(100), nullable=False),
#     Column('created_date', DateTime, nullable=False),
#     Column('url', String(200)),
#     Column('album_id', Integer, ForeignKey('albums.id', ondelete='CASCADE'))
#     Column('user_id', Integer, ForeignKey('albums.id', ondelete='CASCADE'))
# )
