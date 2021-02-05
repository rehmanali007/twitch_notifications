from twitchAPI.twitch import Twitch
from twitchAPI.webhook import TwitchWebHook
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
twitch.authenticate_app([])

user_info = twitch.get_users(logins=['my_twitch_user'])
print(user_info)
user_id = user_info['data'][0]['id']
# basic setup

sslContext = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
hook = TwitchWebHook(my_public_url, app_id, public_port)
hook.authenticate(twitch)
hook.start()

print('[+] Subscribing to hook ...')
success, uuid = hook.subscribe_stream_changed(user_id, callback_stream_changed)
pprint(success)
pprint(twitch.get_webhook_subscriptions())
# the webhook is now running and you are subscribed to the topic you want to listen to. lets idle a bit...
input('[+] Press "Enter" to shut down...\n')
hook.stop()
print('[+] Done!')
