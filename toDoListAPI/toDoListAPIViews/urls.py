from django.urls import path
from toDoListAPIViews import views

urlpatterns = [
    path('/user/signup/', views.signup),
    path('/user/login/', views.login),

    path('/operation/createList/', views.createList),
    path('/operation/addToList/', views.addToList),
    path('/operation/updateItemFromList/', views.updateItemFromList),
    path('/operation/markDoneFromList/', views.markDoneFromList),
    path('/operation/deleteFromList/', views.deleteFromList),
    path('/operation/deleteList/', views.deleteList),
    path('/operation/getItemsFromList/', views.getItemsFromList),
]
