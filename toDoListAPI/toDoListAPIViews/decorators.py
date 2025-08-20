from rest_framework.response import Response
from rest_framework import status

from functools import wraps
from db_model.models import User, List, Task

import json

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

# check if email is repeated
def validate_email(view):
    @wraps(view)
    def wrapper(request):
        if request.data.get('email') is None:
            return Response({'error': 'Email is missing'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=request.data.get('email')).first() is not None:
            return Response({'error': 'This email is taken'}, status=status.HTTP_400_BAD_REQUEST)

        return view(request)

    return wrapper