from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from db_model.models import User, List, Task
from toDoListAPIViews.serializers import ListSerializer, TaskSerializer
from toDoListAPIViews.decorators import get_post_data, check_signup_post_data, check_token
from toDoListAPIViews.utilities import hash_password, dehash_password, generate_token, check_if_item_belogs_to_list

from django.core.exceptions import ValidationError
from django.db import DatabaseError

# create account for user
@api_view(['POST'])
@check_signup_post_data # user sends data necessary for creating account
@get_post_data
def signup(request):
    hashed_password = hash_password(request.data['password']) # before saving password to db, hash it
    token = generate_token() # generate token that will be used to access API views
    hashed_token = hash_password(token) # before saving token to db, hash it

    try:
        user = User(username=request.data['username'], email=request.data['email'], password=hashed_password, token=hashed_token)
        user.save()

    except ValidationError:
        return Response({'error': 'Name or email is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except (KeyError, ValueError):
        return Response({'error': 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'token': token}, status=status.HTTP_201_CREATED)

# generates new token for user after logging out and assigns it to their account in db
@api_view(['POST'])
@get_post_data
def login(request):
    for param in ('email', 'password'): # check for parameters in request's body
        if request.data.get(param) is None:
            return Response({'error': 'Email or password was not provided'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=request.data['email']).first() # get user record from db
    if user is None:
        return Response({'error': 'User with this email was not found'}, status=status.HTTP_404_NOT_FOUND)

    hashed_pw = hash_password(request.data['password']) # get password and hash it
    if user.password != hashed_pw: # check if sent password is the same as the one in the db
        return Response({'error': 'Password is incorrect'}, status=status.HTTP_403_FORBIDDEN)
    
    if user.token != 'logged_out': # check if user isn't logged in already
        return Response({'message': 'User is already logged in'}, status=status.HTTP_200_OK)

    token = generate_token() # generate new token
    hashed_token = hash_password(token)

    try:
        user.token = hashed_token # assign new token
        user.save()

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'token': token}, status=status.HTTP_200_OK)

# marks user as logged_out
@api_view(['POST'])
@check_token
@get_post_data
def logout(request):
    request.user.token = 'logged_out'
    request.user.save()

    return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

# resends token after veryfing user
@api_view(['POST'])
@get_post_data
def remindToken(request):
    for param in ('email', 'password'):
        if param not in request.data:
            return Response({'error': 'Email or password was not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.filter(email=request.data['email']).first()

        if user is None:
            return Response({'error': 'User with this email was not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.password != hash_password(request.data['password']):
            return Response({'error': 'Password is incorrect'}, status=status.HTTP_403_FORBIDDEN)
        
        if user.token is not None and user.token != 'logged_out':
            dehashed_token = dehash_password(user.token)
        else:
            return Response({'message': 'User is not logged in'}, status=status.HTTP_204_NO_CONTENT)

    except ValidationError:
        return Response({'error': 'Email or password that was sent is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response({'token': dehashed_token}, status=status.HTTP_200_OK)

# create new lists for Task objects
@api_view(['POST'])
@check_token
@get_post_data
def createList(request):
    if 'list_name' not in request.data:
        return Response({'error': 'List name was not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if List.objects.filter(list_name=request.data['list_name']).first() is not None:
            return Response({'error': 'List with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        new_list = List(list_name=request.data['list_name'], tasks=[])
        new_list.save()

        request.user.lists.append(new_list.id) # add another to-do list to user account
        request.user.save()

        serializer = ListSerializer(new_list)

    except ValidationError:
        return Response({'error': 'List name is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error': 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# adds new task to list
@api_view(['POST'])
@check_token
@get_post_data
def addItemToList(request):
    for param in ('list_id', 'title'): # check parameters sent by the user
        if param not in request.data:
            return Response({'error': 'List ID or task title was not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        request.data['list_id'] = int(request.data['list_id']) # convert list_id parameter to int

        if not check_if_item_belogs_to_list(request.data['list_id'], request.user.lists): # check if list with this ID belongs to this user
            return Response({'error': 'List with this ID does not belog to this user'}, status=status.HTTP_403_FORBIDDEN)

        user_list = List.objects.filter(id=request.data['list_id']).first() # if we got to this point, this list must exists, becouse if statement before would go off

        new_task = Task(title=request.data['title'], status='to-do') # create new task
        new_task.save()

        user_list.tasks.append(new_task.id) # add this task to specified list
        user_list.save()

        serializer = TaskSerializer(new_task)

    except ValidationError:
        return Response({'error': 'Task name is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error': 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# change item's title from selected list
@api_view(['POST'])
@check_token
@get_post_data
def updateItem(request):
    for param in ('task_id', 'title', 'list_id'):
        if param not in request.data:
            return Response({'error': 'Task ID, list ID or task title was not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        request.data['list_id'] = int(request.data['list_id']) # convert ids to int
        request.data['task_id'] = int(request.data['task_id'])

        if not check_if_item_belogs_to_list(request.data['list_id'], request.user.lists): # check if list belongs to user
            return Response({'error': 'List with this ID does not belog to this user'}, status=status.HTTP_403_FORBIDDEN)
        
        user_list = List.objects.filter(id=request.data['list_id']).first() # get list
        
        if not check_if_item_belogs_to_list(request.data['task_id'], user_list.tasks): # check if task (with this id) belongs to selected list (at this point we know, that the list is users)
            return Response({'error': 'Task with this ID does not belog to this list'}, status=status.HTTP_403_FORBIDDEN)

        task = Task.objects.filter(id=request.data['task_id']).first() # at the point, this task must exists, because if statement before would go off
        
        task.title = request.data['title']
        task.save()

        serializer = TaskSerializer(task)

    except ValidationError:
        return Response({'error': 'Task name is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error': 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_200_OK)

# change 'status' field to "done"
@api_view(['POST'])
@check_token
@get_post_data
def markItemDone(request):
    for param in ('task_id', 'list_id'):
        if param not in request.data:
            return Response({'error': 'Task or list ID was not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        request.data['list_id'] = int(request.data['list_id'])
        request.data['task_id'] = int(request.data['task_id'])

        if not check_if_item_belogs_to_list(request.data['list_id'], request.user.lists):
            return Response({'error': 'List with this ID does not belog to this user'}, status=status.HTTP_403_FORBIDDEN)

        user_list = List.objects.filter(id=request.data['list_id']).first()
        
        if not check_if_item_belogs_to_list(request.data['task_id'], user_list.tasks):
            return Response({'error': 'Task with this ID does not belog to this list'}, status=status.HTTP_403_FORBIDDEN)

        task = Task.objects.filter(id=request.data['task_id']).first()

        task.status = 'done'
        task.save()

        serializer = TaskSerializer(task)

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error': 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_200_OK)

# deletes task from list, checks if this task and list belongs to user
@api_view(['POST'])
@check_token
@get_post_data
def deleteItem(request):
    for param in ('task_id', 'list_id'):
        if param not in request.data:
            return Response({'error': 'Task or list ID was not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        request.data['list_id'] = int(request.data['list_id'])
        request.data['task_id'] = int(request.data['task_id'])

        if not check_if_item_belogs_to_list(request.data['list_id'], request.user.lists):
            return Response({'error': 'List with this ID does not belog to this user'}, status=status.HTTP_403_FORBIDDEN)

        user_list = List.objects.filter(id=request.data['list_id']).first()
        
        if not check_if_item_belogs_to_list(request.data['task_id'], user_list.tasks):
            return Response({'error': 'Task with this ID does not belog to this list'}, status=status.HTTP_403_FORBIDDEN)

        task = Task.objects.filter(id=request.data['task_id']).first()
        serializer = TaskSerializer(task)

        task.delete()

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error': 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

# deletes list from user account
@api_view(['POST'])
@check_token
@get_post_data
def deleteList(request):
    if 'list_id' not in request.data:
        return Response({'error': 'List ID was not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        request.data['list_id'] = int(request.data['list_id'])

        if not check_if_item_belogs_to_list(request.data['list_id'], request.user.lists):
            return Response({'error': 'List with this ID does not belog to this user'}, status=status.HTTP_403_FORBIDDEN)

        user_list = List.objects.filter(id=request.data['list_id']).first()
        serializer = ListSerializer(user_list)
        
        user_list.delete()

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error': 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

# returns a list of all Lists IDs that user has
@api_view(['POST'])
@check_token
def getListsIDs(request):
    try:
        user_lists = []

        for list_id in request.user.lists:
            list_name = List.objects.get(id=list_id).list_name
            user_lists.append({list_name: list_id})

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error': 'Unable to retrieve lists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(user_lists, status=status.HTTP_200_OK)

# returns a list of Task objects from selected list
@api_view(['POST'])
@check_token
def getItemsFromList(request):
    if 'list_id' not in request.data:
        return Response({'error': 'List ID was not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        request.data['list_id'] = int(request.data['list_id'])

        if not check_if_item_belogs_to_list(request.data['list_id'], request.user.lists):
            return Response({'error': 'List with this ID does not belog to this user'}, status=status.HTTP_403_FORBIDDEN)
        
        user_list = List.objects.filter(id=request.data['list_id']).first()
        if user_list.tasks == []:
            return Response([], status=status.HTTP_200_OK)

        tasks = Task.objects.filter(id__in=user_list.tasks)
        serializer = TaskSerializer(tasks, many=True)

    except DatabaseError as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error': 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_200_OK)
