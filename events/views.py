from os import stat
from django.http import request
from django.shortcuts import render
import datetime

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from slack import WebClient

SLACK_CLIENT_ID = getattr(settings, 'SLACK_CLIENT_ID', None)
SLACK_CLIENT_SECRET = getattr(settings, 'SLACK_CLIENT_SECRET', None)

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings,'SLACK_BOT_USER_TOKEN', None)                                     #
Client = WebClient(SLACK_BOT_USER_TOKEN) 

class Events(APIView):
    def post(self, request, *args, **kwargs):
        slack_message = request.data
        
        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # verification challenge
        # if slack_message.get('type') == 'url_verification':
        #     return Response(data=slack_message,
        #                     status=status.HTTP_200_OK)

        

        if 'event' in slack_message:
            event_message = slack_message.get('event')
            print(event_message)
            
            # ignore bot's own message
            if event_message.get('bot_id', None):
                return Response(status=status.HTTP_200_OK)

            # process user's message
            user = event_message.get('user')
            text = event_message.get('text')
            channel = event_message.get('channel')
            bot_text = 'Hello <@{}> :wave:'.format(user)
            if 'hi' in text.lower():
                response = Client.chat_postMessage(channel=channel,text=bot_text)
                assert response["message"]["text"] == bot_text
                # Client.api_call(method='chat.postMessage',
                #                 channel=channel,
                #                 text=bot_text)
                return Response(status=status.HTTP_200_OK, headers={"X-Slack-No-Retry": 1})

        return Response(status=status.HTTP_200_OK, headers={"X-Slack-No-Retry": 1})

class Channels(APIView):
    def post(self, request):
        name = request.data.get('name', None)
        if not name:
            return Response({"message":"no name provided"}, status = status.HTTP_400_BAD_REQUEST)
        res = Client.conversations_create(name=name)
        print(res)
        if res['ok']:
            return Response({"channels":Client.conversations_list(types="public_channel")['channels']}, status = status.HTTP_200_OK)
        return Response({"message":"Some error"}, status = status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # print(Client.conversations_list(types="public_channel"))
        return Response(Client.conversations_list(types="public_channel")['channels'])

class Message(APIView):
    def post(self, request):
        channel = request.data.get('channel', 'general')
        message = request.data.get('message', '')
        user_token = request.data.get('user_token', None)
        time_str = request.data.get('time', None)
        accept = request.data.get('accept', 'bot')
        if not WebClient(user_token).api_call('auth.test')['ok']:
            return Response({'message':'auth_failed'}, status=status.HTTP_400_BAD_REQUEST)
        token = ''
        if accept == 'bot':
            token = SLACK_BOT_USER_TOKEN
        else:
            token = user_token
        Client = WebClient(token) 
        response = {}
        if time_str:
            dt = datetime.datetime.strptime(time_str, '%d-%m-%Y %H:%M:%S')
            dt = dt - datetime.timedelta(hours=5,minutes=30)
            print(dt)
            unix_time = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            response = Client.chat_scheduleMessage(channel=channel, text=message, post_at=unix_time)
            print(response)
            messages = getScheduledMessages()
            return Response({"messages": messages}, status=status.HTTP_200_OK)
        else:
            response = Client.chat_postMessage(channel=channel, text=message)
            assert response["message"]["text"] == message
        return Response(status=status.HTTP_200_OK)


    def get(self, request):
        user_token = request.query_params.get('user_token', None)
        client = WebClient(user_token)
        if not client.api_call('auth.test')['ok']:
            return Response({'message':'auth_failed'}, status=status.HTTP_400_BAD_REQUEST)
        res = WebClient(SLACK_BOT_USER_TOKEN).api_call('chat.scheduledMessages.list')
        messages = getScheduledMessages()
        return Response(messages)

class DelMessage(APIView):
    def post(self, request):
        user_token = request.data.get('user_token', None)
        id = request.data.get('id',None)
        channel_id = request.data.get('channel_id', None)
        client = WebClient(user_token)
        if not client.api_call('auth.test')['ok']:
            return Response({'message':'auth_failed'}, status=status.HTTP_400_BAD_REQUEST)
        res = Client.chat_deleteScheduledMessage(channel=channel_id,scheduled_message_id=id)
        if res['ok']:
            messages = getScheduledMessages()
            return Response({"messages": messages}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class Auth(APIView):
    def post(self, request):
        code = request.data.get('code', None)
        redirect_uri = request.data.get('redirect_uri', 'https://chatterbot-self.vercel.app/main')
        client = WebClient()
        response = client.oauth_v2_access(
            client_id=SLACK_CLIENT_ID,
            client_secret=SLACK_CLIENT_SECRET,
            code=code,
            redirect_uri=redirect_uri
            )
        channels = Client.conversations_list(types="public_channel")['channels']
        res = WebClient(response['authed_user']["access_token"]).api_call('users.profile.get')
        messages = getScheduledMessages()
        response_obj = {
            "code": response['authed_user']["access_token"],
            "channels": channels,
            "user_info": res['profile'],
            "messages": messages
        }
        return Response(response_obj)

class Login(APIView):
    def get(self, request):
        code = request.query_params.get('code')
        client = WebClient()
        response = client.oauth_v2_access(
            client_id=SLACK_CLIENT_ID,
            client_secret=SLACK_CLIENT_SECRET,
            code=code
            )
        response_data = {
            "user_id": response['authed_user']["id"],
            "access_token": response['authed_user']["access_token"],
            "scope": response['authed_user']["scope"],
            "team_id": response["team"]["id"],
        }
        print("Check", response)
        return Response(response_data)

def getScheduledMessages():
    channels = Client.conversations_list(types="public_channel")['channels']
    schd = Client.api_call('chat.scheduledMessages.list')
    messages = []
    print(schd)
    if schd['ok']:
        messages = schd["scheduled_messages"]
        for message in messages:
            message['name'] = list(filter(lambda x: x['id'] == message['channel_id'], channels))[0]['name']
            message['post_at'] = (datetime.datetime.utcfromtimestamp(message['post_at'])+ datetime.timedelta(hours=5,minutes=30)).strftime('%d-%m-%Y %H:%M:%S')
    return messages