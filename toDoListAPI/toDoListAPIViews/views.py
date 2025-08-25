from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from db_model.models import User, List, Task
from toDoListAPIViews.serializers import ListSerializer, TaskSerializer
from toDoListAPIViews.decorators import get_post_data, check_signup_post_data, check_token
from utilities import hash_password, dehash_password, generate_token, check_if_item_belogs_to_list

from django.core.exceptions import ValidationError
from django.db import DatabaseError

@api_view(['POST'])
@check_signup_post_data
@get_post_data
def signup(request):
    hashed_password = hash_password(request.data['password'])
    token = generate_token()
    hashed_token = hash_password(token)

    try:
        user = User(username=request.data['username'], email=request.data['email'], password=hashed_password, token=hashed_token)
        user.save()

    except ValidationError:
        return Response({'error', 'Name or email is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError as e:
        return Response({'error', f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except (KeyError, ValueError):
        return Response({'error', 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'token': token}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@get_post_data
def login(request):
    for param in ('email', 'password'):
        if request.data.get(param) is None:
            return Response({'error': 'Email or password was not provided'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=request.data['email']).first()
    hashed_pw = hash_password(request.data['password'])

    if user.password != hashed_pw:
        return Response({'error': 'Password is incorrect'}, status=status.HTTP_403_FORBIDDEN)
    
    token = generate_token()
    hashed_token = hash_password(token)

    try:
        user.token = hashed_token
        user.save()

    except DatabaseError as e:
        return Response({'error', f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'token': token}, status=status.HTTP_200_OK)


@api_view(['POST'])
@check_token
@get_post_data
def logout(request):
    request.user.token = 'logged_out'
    request.user.save()

    return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

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

    except DatabaseError as e:
        return Response({'error', f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        request.data['list_id'] = int(request.data['list_id'])

        if not check_if_item_belogs_to_list(request.data['list_id'], request.user.lists):
            return Response({'error': 'List with this ID does not belog to this user'}, status=status.HTTP_403_FORBIDDEN)

        user_list = List.objects.filter(id=request.data['list_id']).first() # if we got to this point, this list must exists, becouse if statement before would go off

        new_task = Task(title=request.data['title'], status='to-do')
        new_task.save()

        user_list.tasks.append(new_task.id)
        user_list.save()

        serializer = TaskSerializer(new_task)

    except ValidationError:
        return Response({'error', 'Task name is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError as e:
        return Response({'error', f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error', 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@check_token
@get_post_data
def updateItem(request):
    for param in ('task_id', 'title', 'list_id'):
        if param not in request.data:
            return Response({'error': 'Task ID was not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        request.data['list_id'] = int(request.data['list_id'])
        request.data['task_id'] = int(request.data['task_id'])

        if not check_if_item_belogs_to_list(request.data['list_id'], request.user.lists):
            return Response({'error': 'List with this ID does not belog to this user'}, status=status.HTTP_403_FORBIDDEN)
        
        user_list = List.objects.filter(id=request.data['list_id']).first()
        
        if not check_if_item_belogs_to_list(request.data['task_id'], user_list.tasks):
            return Response({'error': 'Task with this ID does not belog to this list'}, status=status.HTTP_403_FORBIDDEN)

        task = Task.objects.filter(id=request.data['task_id']).first() # at the point, this task must exists, because if statement before would go off
        
        task.title = request.data['title']
        task.save()

        serializer = TaskSerializer(task)

    except ValidationError:
        return Response({'error', 'Task name is too long'}, status=status.HTTP_400_BAD_REQUEST)

    except DatabaseError as e:
        return Response({'error', f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error', 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        return Response({'error', f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error', 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        return Response({'error', f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error', 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


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
        return Response({'error', f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error', 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@check_token
def getListsIDs(request):
    try:
        user_lists = request.user.lists

    except DatabaseError as e:
        return Response({'error', f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error': 'Unable to retrieve lists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(user_lists, status=status.HTTP_200_OK)

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
        return Response({'error', f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (KeyError, ValueError):
        return Response({'error', 'Invalid request body'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(serializer.data, status=status.HTTP_200_OK)
