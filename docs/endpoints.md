# Endpoints

## User-action based

- `/user/signup/` - creates an accoun and generates token for user.\
Email must be unique for each user.

**JSON example**

```json
{
    "username": "",
    "email": "",
    "password": ""
}
```

**Response**

```json
{
    "token": "A string of 49 characters"
}
```

- `/user/login/` - generates new token when user is not logged in

**JSON example**

```json
{
    "email": "",
    "password": ""
}
```

**Response**

```json
{
    "token": ""
}
```

- `/user/remindToken/` - sends token that is currently assigned to user

**JSON example**

```json
{
    "email": "",
    "password": ""
}
```

**Response**

```json
{
    "token": ""
}
```

- `/user/logout/` - sets token for user as "logged_out", makes previous token outdated.\
User must log in to create new token.

**JSON example**

```json
{
    "token": ""
}
```

**Response**

```json
{
    "message": "Successfully logged out"
}
```

### Operation based

- `/operation/createList/` - creates new list and adds it's ID to `lists` field of User table

**JSON example**

```json
{
    "list_name": "",
    "token": ""
}
```

**Response**

List object

- `/operation/addItemToList/` - creates new task and adds it's ID to `tasks` filed of List table

**JSON example**

```json
{
    "list_id": int,
    "title": "",
    "token": ""
}
```

**Response**

Task object

- `/operation/updateItem/` - changes task's title

**JSON example**

```json
{
    "list_id": int,
    "task_id": int,
    "token": ""
}
```

**Response**

Task object

- `/operation/markItemDone/` - Changes task's status from "to-do" to "done"

**JSON example**

```json
{
    "list_id": int,
    "task_id": int,
    "token": ""
}
```

**Response**

Task object

- `/operation/deleteItem/` - deletes task

**JSON example**

```json
{
    "list_id": int,
    "task_id": int,
    "token": ""
}
```

**Response**

Task object, without ID

- `/operation/deleteList/` - deletes to-do list

**JSON example**

```json
{
    "list_id": int,
    "token": ""
}
```

**Response**

List object, without ID

- `/operation/getListsIDs/` - returns a list of IDs and names of lists that belog to user.

**JSON example**

```json
{
    "token": ""
}
```

**Response**

Array of objects like:
`{list_name: list_id}`

- `/operation/getItemsFromList/` - returns a list of task IDs that belong to a list

**JSON example**

```json
{
    "list_id": int,
    "token": ""
}
```

**Response**

Array of integers, that corresponds to the task IDs