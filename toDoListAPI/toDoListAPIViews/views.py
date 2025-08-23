from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from db_model.models import User, List, Task
from toDoListAPIViews.serializers import ListSerializer, TaskSerializer
from toDoListAPIViews.decorators import get_post_data, check_signup_post_data, check_token
from toDoListAPI.settings import env

from django.core.exceptions import ValidationError
from django.db import DatabaseError

import json
import random

# hash password before save it to database to prevent data leaks
def hash_password(password: str) -> str:
    hash_table = json.loads(env('HASH_TABLE'))
    hashed_pw = ''

    for i in password:
        hashed_pw += hash_table.get(i)

    return hashed_pw

def dehash_password(password: str) -> str:
    dehash_table = json.loads(env('DEHASH_TABLE'))
    dehashed_pw = ''

    for i in password:
        dehashed_pw += dehash_table.get(i)

    return dehashed_pw

# user token generator
def generate_token() -> str:
    # create token
    token = ''
    hash_table = json.load(env('HASH_TABLE'))

    for _ in range(49): # limit is 50
        token += random.choice(hash_table.keys())

    # check if it's unique
    if User.objects.filter(token=token).first() is not None:
        return generate_token()

    return token


@api_view(['POST'])
@check_signup_post_data
@get_post_data
def signup(request):
    hashed_password = hash_password(request.data['password'])
    token = generate_token()
    hashed_token = hashed_password(token)

    try:
        user = User(username=request.data['username'], email=request.data['email'], password=hashed_password, token=hashed_token)
        user.save()

    except ValidationError:
        return Response({'error', 'Name or email is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError:
        return Response({'error', 'Database error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except (KeyError, ValueError):
        return Response({'error', 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'token': token}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@get_post_data
def login(request):
    for param in ('email', 'password'):
        if request.data.get(param) is None:
            return Response({'error': 'Email or was not provided'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=request.data['email']).first()
    hashed_pw = hash_password(request.data['password'])

    if user.password != hashed_pw:
        return Response({'error': 'Password is incorrect'}, status=status.HTTP_403_FORBIDDEN)
    
    token = dehash_password(user.token)

    return Response({'token': token}, status=status.HTTP_200_OK)


@api_view(['POST'])
@check_token
@get_post_data
def createList(request):
    if 'list_name' not in request.data:
        return Response({'error': 'List name was not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        new_list = List(list_name=request.data['list_name'], tasks=[])
        new_list.save()

        request.user.lists.append(new_list.id) # add another to-do list to user account
        request.user.save()

        serializer = ListSerializer(new_list)

    except ValidationError:
        return Response({'error', 'List name is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError:
        return Response({'error', 'Database error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error', 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@check_token
@get_post_data
def addItemToList(request):
    for param in ('list_id', 'title'):
        if param not in request.data:
            return Response({'error': 'List ID was not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        new_task = Task(title=request.data['title'], status='to-do')
        new_task.save()

        user_list = List.objects.filter(id=request.data['list_id']).first()
        if user_list is None:
            return Response({'error': 'List was not found'}, status=status.HTTP_404_NOT_FOUND)

        user_list.tasks.append(new_task)
        user_list.save()

        serializer = TaskSerializer(new_task)

    except ValidationError:
        return Response({'error', 'List name is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError:
        return Response({'error', 'Database error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error', 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
def getListsIDs(request):
    pass


@api_view(['GET'])
def getItemsFromList(request):
    pass
