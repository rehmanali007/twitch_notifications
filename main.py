from twitchAPI import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.types import AuthScope
from twitchAPI.webhook import TwitchWebHook
from pprint import pprint
import json
import ssl
import logging
import os

config = json.load(open('config.json', 'r'))
IP_ADDRESS = config.get('PUBLIC_ADDR')
PORT = config.get('PUBLIC_PORT')
APP_ID = config.get('APP_ID')
APP_SECRET = config.get('APP_SECRET')
PUBLIC_ADDR = f'https://{IP_ADDRESS}:{PORT}'
print(f'Public address : {PUBLIC_ADDR}')

TOKEN = config.get("TOKEN")
REFRESH_TOKEN = config.get("REFRESH_TOKEN")


logger = logging.getLogger()
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
formator = logging.Formatter(
    '[%(asctime)s] - [%(name)s] - %(levelname)s - %(message)s')
consoleHandler.setFormatter(formator)
if not os.path.exists('./logs'):
    os.mkdir('logs')
fileHandler = logging.FileHandler('logs/app.log')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formator)
logger.addHandler(fileHandler)
logger.addHandler(consoleHandler)


def callback_stream_changed(uuid, data):
    print('Callback Stream changed for UUID ' + str(uuid))
    pprint(data)


def callback_user_changed(uuid, data):
    print('Callback User changed for UUID ' + str(uuid))
    pprint(data)


# basic twitch API authentication, this will yield a app token but not a user token
auth_scope = [
    AuthScope.BITS_READ,
    AuthScope.USER_EDIT,
    AuthScope.WHISPERS_READ,
    AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
    AuthScope.CHANNEL_READ_STREAM_KEY,
    AuthScope.ANALYTICS_READ_EXTENSION,
    AuthScope.ANALYTICS_READ_GAMES,
    AuthScope.CHANNEL_EDIT_COMMERCIAL,
    AuthScope.CHANNEL_READ_HYPE_TRAIN,
    AuthScope.CHANNEL_MANAGE_BROADCAST,
    AuthScope.CHANNEL_READ_REDEMPTIONS,
    AuthScope.CLIPS_EDIT,
    AuthScope.USER_EDIT_BROADCAST,
    AuthScope.USER_READ_BROADCAST,
    AuthScope.USER_READ_EMAIL,
    AuthScope.USER_EDIT_FOLLOWS,
    AuthScope.CHANNEL_MODERATE,
    AuthScope.CHAT_EDIT,
    AuthScope.CHAT_READ,
    AuthScope.WHISPERS_READ,
    AuthScope.WHISPERS_EDIT,
    AuthScope.MODERATION_READ,
    AuthScope.CHANNEL_SUBSCRIPTIONS
]
twitch = Twitch(APP_ID, APP_SECRET)
twitch.authenticate_app(auth_scope)
# since we want user information, we require a OAuth token, lets get one
# you dont need to generate a fresh user token every time, you can also refresh a old one or get one using a different online service
# for refreshing look here: https://github.com/Teekeks/pyTwitchAPI#user-authentication
# please note that you have to add http://localhost:17563 as a OAuth redirect URL for your app, see the above link for more information
# auth = UserAuthenticator(
#     twitch, auth_scope)
# token, refresh_token = auth.authenticate()  # this will open a webpage
# print(token, refresh_token)
# setting the user authentication so any api call will also use it
twitch.set_user_authentication(
    TOKEN, auth_scope, REFRESH_TOKEN)
# setting up the Webhook itself
sslContext = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
hook = TwitchWebHook(PUBLIC_ADDR,
                     APP_ID, PORT, ssl_context=sslContext)
# this will use the highest authentication set, which is the user authentication.
hook.authenticate(twitch)
# some hooks don't require any authentication, which would remove the requirement to set up a https reverse proxy
# if you don't require authentication just dont call authenticate()
hook.start()

user_info = twitch.get_users()
user_id = user_info['data'][0]['id']
print(f'User ID : {user_id}')


# the hook has to run before you subscribe to any events since the twitch api will do a handshake this this webhook as soon as you subscribe
success, uuid_stream = hook.subscribe_stream_changed(
    str(user_id), callback_stream_changed)
print(f'Was subscription successfull?: {success}')
success, uuid_user = hook.subscribe_user_changed(
    str(user_id), callback_user_changed)
print(f'Was subscription successfull?: {success}')

# now we are fully set up and listening to our webhooks, lets wait for a user imput to stop again:
input('[+] Press enter to stop...')

# lets unsubscribe again
success = hook.unsubscribe(uuid_user)
print(f'was unsubscription successfull?: {success}')
# since hook.unsubscribe_on_stop is true, we dont need to unsubscribe manually, so lets just stop
hook.stop()
