from twitchAPI.twitch import Twitch
from twitchAPI.webhook import TwitchWebHook
from twitchAPI.types import AuthScope
from pprint import pprint
import json
import ssl

config = json.load(open('config.json', 'r'))


def callback_stream_changed(uuid, data):
    print('Callback for UUID ' + str(uuid))
    pprint(data)


app_id = config.get('APP_ID')
app_secret = config.get('APP_SECRET')
public_addr = config.get('PUBLIC_ADDR')
public_port = config.get('PUBLIC_PORT')

my_public_url = f'https://{public_addr}:{public_port}'

twitch = Twitch(app_id, app_secret)
authentication_scope = [
    AuthScope.BITS_READ,
    AuthScope.USER_EDIT,
    AuthScope.USER_READ_BROADCAST,
    AuthScope.USER_READ_EMAIL
]
twitch.authenticate_app(authentication_scope)

user_info = twitch.get_users()
print(user_info)
user_id = user_info['data'][0]['id']
# basic setup

sslContext = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
hook = TwitchWebHook(my_public_url, app_id, public_port)
hook.authenticate(twitch)
hook.start()

print('[+] Subscribing to hook ...')
success, uuid = hook.subscribe_stream_changed(user_id, callback_stream_changed)
if not success:
    print('Could not subscribe to webhook ...')
    hook.stop()
pprint(twitch.get_webhook_subscriptions())
# the webhook is now running and you are subscribed to the topic you want to listen to. lets idle a bit...
input('[+] Press "Enter" to shut down...\n')
hook.stop()
print('[+] Done!')
