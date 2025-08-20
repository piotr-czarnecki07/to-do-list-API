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

def validate_email(view):
    @wraps(view)
    def wrapper(request):
        pass

    return wrapper