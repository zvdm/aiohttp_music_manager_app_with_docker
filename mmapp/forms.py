import os
from aiohttp import web

from .db import get_user_by_name, update_user_info, get_user_by_api_key, update_track_item, get_user_track_by_title_and_api_key


async def validate_user_form(request, form):
    username = form.get('name')
    update_data = dict()
    if username != '':
        row = await get_user_by_name(request, username)
        print('row', row)
        if row is None:
            update_data['name'] = username

    if form.get('password') is not None:
        update_data['pwd'] = form.get('password')
    update_data['email'] = form.get('email')

    # Check if retrieved value of age is digits
    try:
        age = int(form.get('age'))
    except:
        age = 0
    update_data['age'] = age

    update_data['location'] = form.get('location')

    print(update_data)

    if len(update_data):
        row = await update_user_info(request, update_data, request.cookies['api_key'])
        return row
    return 0


async def validate_track_form(request, new_title, old_title, upload_path):
    # Get user by api_key to retrieve user id
    user = await get_user_by_api_key(request, request.cookies['api_key'])

    # Define new filename in uploads dir
    filename_for_dir = f'{user["id"]}-{new_title}'
    new_saved_dir = os.path.join(upload_path, filename_for_dir)

    # Check if file with this title exists
    row = await get_user_track_by_title_and_api_key(request, new_title, user['id'])
    if row:
        return web.HTTPSeeOther(f'/track/{old_title}')

    # Update data about track in db
    row = await update_track_item(request, new_title, old_title, new_saved_dir, user['id'])

    # Rename track file in uploads dir
    os.rename(os.path.join(upload_path, f'{user["id"]}-{old_title}'), new_saved_dir)
    print('row', row)
    return row