from rest_framework.response import Response
from rest_framework import status
from db_model.models import User
from toDoListAPIViews.hashes import HASH_TABLE, DEHASH_TABLE

import random

# hash password before save it to database to prevent data leaks
def hash_password(password: str) -> str:
    hashed_pw = ''

    try:
        for i in password:
            hashed_pw += HASH_TABLE.get(i)
    except KeyError:
        return Response({'error': 'Forbidden symbol during hashing, use only a-z, A-Z, 0-9, !@#$%^&*()'}, status=status.HTTP_400_BAD_REQUEST)

    return hashed_pw

def dehash_password(password: str) -> str:
    dehashed_pw = ''

    for i in password:
        dehashed_pw += DEHASH_TABLE.get(i)

    return dehashed_pw

# user token generator
def generate_token() -> str:
    # create token
    token = ''

    for _ in range(49): # limit is 50
        token += random.choice(list(HASH_TABLE.keys()))

    # check if it's unique
    if User.objects.filter(token=token).first() is not None:
        return generate_token()

    return token

# checks if id provided by user belongs to them
# it means, if user provided list ID 1, check if "user_lists" list has element, that is equal to 1
# furthermore, if provided task ID 4, check if list on ID 1 (checked before) has task ID equal to 4
def check_if_item_belogs_to_list(item_id: int, list_obj: list) -> bool:
    start = 0
    end = len(list_obj) - 1
    found = False

    while start <= end:
        mid = (start + end) // 2

        if list_obj[mid] == item_id:
            found = True
            break
        elif list_obj[mid] < item_id:
            start = mid + 1
        else:
            end = mid - 1

    return found