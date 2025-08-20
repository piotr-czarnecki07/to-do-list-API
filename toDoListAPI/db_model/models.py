from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=50)

    lists = models.JSONField(default=list)

class List(models.Model):
    list_name = models.CharField(max_length=50, unique=True)
    tasks = models.JSONField(default=list)

class Task(models.Model):
    title = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20)