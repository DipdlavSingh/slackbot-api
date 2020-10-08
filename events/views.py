from os import stat
from django.shortcuts import render

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
                return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)

class Channels(APIView):
    def get(self, request):
        # print(Client.conversations_list(types="public_channel"))
        return Response(Client.conversations_list(types="public_channel")['channels'])

class Message(APIView):
    def post(self, request):
        channel = request.data.get('channel')
        message = request.data.get('message')
        response = Client.chat_postMessage(channel=channel, text=message, as_user=True)
        assert response["message"]["text"] == message
        return Response(status=status.HTTP_200_OK)

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
            "access_token": response["access_token"],
            "scope": response["scope"],
            "team_name": response["team_name"],
            "team_id": response["team_id"],
            "incoming_webhook": response["incoming_webhook"],
            "bot":response["bot"]
        }
        print("Check", response)
        return Response(response_data)
