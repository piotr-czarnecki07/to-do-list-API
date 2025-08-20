from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from db_model.models import User, List, Task
from serializers import UserSerializer, ListSerializer, TaskSerializer

from decorators import get_post_data, validate_email


@api_view(['POST'])
@validate_email
@get_post_data
def signup(request):
    pass

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
def addToList(request):
    pass

@api_view(['POST'])
@get_post_data
def updateItemFromList(request):
    pass

@api_view(['POST'])
@get_post_data
def markDoneFromList(request):
    pass

@api_view(['POST'])
@get_post_data
def deleteFromList(request):
    pass

@api_view(['POST'])
@get_post_data
def deleteList(request):
    pass

@api_view(['GET'])
def getItemsFromList(request):
    pass