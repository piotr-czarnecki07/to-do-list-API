from rest_framework.response import Response
from rest_framework import status
from functools import wraps

from db_model.models import User
from toDoListAPI.settings import env
from toDoListAPIViews.utilities import hash_password

import json

# check input data from request body
def check_signup_post_data(view):
    @wraps(view)
    def wrapper(request):
        # check parameters
        for param in ('username', 'email', 'password'):
            if param not in request.data: # email and password fields were checked with decorators
                return Response({'error', 'username, email or password is missing'}, status=status.HTTP_400_BAD_REQUEST)

        # check if email is unique
        if User.objects.filter(email=request.data.get('email')).first() is not None:
            return Response({'error', 'This email is already taken'}, status=status.HTTP_400_BAD_REQUEST)
        
        # validate password
        if len(request.data.get('password')) > 50: # check length to not slow down the program with a for loop
            return Response({'error', 'Password is too long'}, status=status.HTTP_400_BAD_REQUEST)

        for i in request.data.get('password'):
            if i not in json.loads(env('HASH_TABLE')).keys():
                return Response({'error', 'Password contains forbidden symbols. Available symbols: a-z A-Z 0-9 !@#$%^&*()'}, status=status.HTTP_400_BAD_REQUEST)

        return view(request)

    return wrapper

# if requset body (data from API user) is wrapped in _content field, retrive it and assign to request.data
def get_post_data(view):
    @wraps(view)
    def wrapper(request):
        try:
            if isinstance(request.data, dict):
                if '_content' in request.data:
                    request.data = json.loads(request.data['_content'])
            else:
                return Response({'error': 'Data is not a valid JSON'}, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError):
            return Response({'error': 'Data was not sent'}, status=status.HTTP_400_BAD_REQUEST)

        return view(request)

    return wrapper

# checks request token, retrieves user record and assigns it to request.user
def check_token(view):
    @wraps(view)
    def wrapper(request):
        if request.data.get('token') is None:
            return Response({'error': 'Token was not sent'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(token=hash_password(request.data['token'])).first()

        if user is None:
            return Response({'error': 'User with this token was not found, maybe try loggin in.'}, status=status.HTTP_404_NOT_FOUND)
        
        request.user = user
        return view(request)

    return wrapper