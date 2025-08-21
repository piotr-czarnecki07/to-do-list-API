from django.urls import path
from toDoListAPIViews import views

urlpatterns = [
    path('user/signup/', views.signup),
    path('user/login/', views.login),

    path('operation/createList/', views.createList),
    path('operation/addItemToList/', views.addItemToList),
    path('operation/updateItemFromList/', views.updateItemFromList),
    path('operation/markItemDoneFromList/', views.markItemDoneFromList),
    path('operation/deleteItemFromList/', views.deleteItemFromList),
    path('operation/deleteList/', views.deleteList),
    path('operation/getListsIDs/', views.getListsIDs),
    path('operation/getItemsFromList/', views.getItemsFromList)
]
