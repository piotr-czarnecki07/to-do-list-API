from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from db_model.models import User, List, Task
from toDoListAPIViews.serializers import UserSerializer, ListSerializer, TaskSerializer
from toDoListAPIViews.decorators import get_post_data, check_signup_post_data
from toDoListAPI.settings import env

from django.core.exceptions import ValidationError
from django.db import DatabaseError

import json

# hash password before save it to database to prevent data leaks
def hash_password(password: str) -> str:
    hash_table = json.loads(env('HASH_TABLE'))
    hashed_pw = ''

    for i in password:
        hashed_pw += hash_table.get(i)

    return hashed_pw

@api_view(['POST'])
@check_signup_post_data
@get_post_data
def signup(request):
    hashed_password = hash_password(request.data['password'])

    try:
        user = User(username=request.data['username'], email=request.data['email'], password=hashed_password)
        user.save()

        serializer = UserSerializer(user)

    except ValidationError:
        return Response({'error', 'Name or email is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError:
        return Response({'error', 'Database error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@get_post_data
def login(request):
    pass


@api_view(['POST'])
@get_post_data
def createList(request):
    pass


@api_view(['POST'])
@get_post_data
def addItemToList(request):
    pass


@api_view(['POST'])
@get_post_data
def updateItemFromList(request):
    pass


@api_view(['POST'])
@get_post_data
def markItemDoneFromList(request):
    pass


@api_view(['POST'])
@get_post_data
def deleteItemFromList(request):
    pass


@api_view(['POST'])
@get_post_data
def deleteList(request):
    pass


@api_view(['GET'])
def getItemsFromList(request):
    pass
