from django.http import JsonResponse
from slack import WebClient

class AuthUser(object):
    # Check if client is authenticated
    def process_request(self, request):
        user_token = request.data.get('user_token',
            request.query_params.get('user_token',
                request.headers.get('user_token', None)))
        try:
            if WebClient(user_token).api_call('auth.test')['ok']:
                request.user_token = user_token
                return None
            else:
                return JsonResponse({"message":"not authorised"}, status=403) # If user is not allowed raise Error
        except Exception as e:
            return JsonResponse({"message":str(e)}, status=403) # If user is not allowed raise Error
        return None