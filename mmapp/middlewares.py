import aiohttp_jinja2
import datetime
from aiohttp import web

from .db import get_user_by_api_key, user_login, user_signup


@web.middleware
async def check_api_key(request, handler):
    class SignUp(web.View):
        async def get(self, msg=None):
            return aiohttp_jinja2.render_template('signup.html', self, {'url': self.path, 'error': msg})

        async def post(self):
            data = await self.post()
            # Login existed user and return api_key as cookie
            if data.get('login', None) is not None \
                    and data.get('login', None) != '' \
                    and data.get('password', None) is not None \
                    and data.get('password', None) != '':
                try:
                    # async with self.app['db'].acquire() as conn:
                    row = await user_login(self.app['db'], data.get('login'), data.get('password'))
                    if row:
                        res = web.HTTPSeeOther(self.path)
                        res.cookies['api_key'] = row
                        return res
                except:
                    e = 'Incorrect username or password'
                    print(e)
                    return aiohttp_jinja2.render_template('signup.html', self, {'error_login': e, 'url': request.path})
            # Sign up new user and return api_key as cookie
            if data.get('username', None) is not None \
                    and data.get('username', None) != '' \
                    and data.get('new_password', None) is not None \
                    and data.get('new_password', None) != '':
                print(data.get('new_password') == '')
                date_time = datetime.datetime.now()
                # async with self.app['db'].acquire() as conn:
                row = await user_signup(self.app['db'], data.get('username'), data.get('new_password'), date_time, True)
                if not row:
                    e = 'This username is used yet. Please, try again'
                    print(e)
                    return aiohttp_jinja2.render_template('signup.html', self, {'error_signup': e, 'url': request.path})
                res = web.HTTPSeeOther(self.path)
                res.cookies['api_key'] = row
                return res
            print('ERROR')
            e = 'Perhaps some field is not filled'
            return aiohttp_jinja2.render_template('signup.html', self, {'error': e, 'url': request.path})

    # Retrieve cookie
    cookie = request.headers.get('Cookie', None)
    msg = ''
    # Check is cookie contains api_key
    if cookie is not None and 'api_key' in cookie:
        api_key = cookie.split('=')
        user = await get_user_by_api_key(request, api_key[1])
        # Check active_status of user
        try:
            if not user['active_status']:
                msg = 'Your api_key is for deleted or not existed user.'
        except:
            return web.Response(text='Error, perhaps, your cookie contains not existed api_key.')

    if cookie is None or 'api_key' not in cookie or msg != '':
        # No one cookie or not api_key or user's status is inactive
        if request.method == 'GET':
            print('GET', request.method)
            response = await SignUp.get(request, msg)
        else:
            print('POST', request.method)
            response = await SignUp.post(request)
        print('Middleware login/signup is success', response)
        return response
    api_key = cookie.split('=')
    # print('req_key', api_key[1])
    if msg == '' and user:
        # If cookie is in headers, user in db and user's status is active
        response = await handler(request)
        return response
    print('Unexpected error')
    return check_api_key
