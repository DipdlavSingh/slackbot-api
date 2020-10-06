from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)

class Events(APIView):
    def post(self, request, *args, **kwargs):
        slack_message = request.data
        
        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # verification challenge
        if slack_message.get('type') == 'url_verification':        #
            return Response(data=slack_message,                    #
                            status=status.HTTP_200_OK)             #

        return Response(status=status.HTTP_200_OK)