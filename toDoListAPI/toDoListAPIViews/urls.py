from django.urls import path
from toDoListAPIViews import views

urlpatterns = [
    path('user/signup/', views.signup),
    path('user/login/', views.login),
    path('user/logout/', views.logout),
    path('user/remindToken', views.remindToken),

    path('operation/createList/', views.createList),
    path('operation/addItemToList/', views.addItemToList),
    path('operation/updateItem/', views.updateItem),
    path('operation/markItemDone/', views.markItemDone),
    path('operation/deleteItem/', views.deleteItem),
    path('operation/deleteList/', views.deleteList),
    path('operation/getListsIDs/', views.getListsIDs),
    path('operation/getItemsFromList/', views.getItemsFromList)
]
