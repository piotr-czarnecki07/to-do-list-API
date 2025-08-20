from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from db_model.models import User, List, Task
from serializers import UserSerializer, ListSerializer, TaskSerializer

from functools import wraps


@api_view(['POST'])
def signup(request):
    pass

@api_view(['POST'])
def login(request):
    pass

@api_view(['POST'])
def createList(request):
    pass

@api_view(['POST'])
def addToList(request):
    pass

@api_view(['POST'])
def updateItemFromList(request):
    pass

@api_view(['POST'])
def markDoneFromList(request):
    pass

@api_view(['POST'])
def deleteFromList(request):
    pass

@api_view(['POST'])
def deleteList(request):
    pass

@api_view(['GET'])
def getItemsFromList(request):
    pass