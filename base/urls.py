from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutUser, name="logout"),

    path('',views.home, name="home"),
    path('room/<int:pk>', views.room, name="room"),
    path('create-room/', views.create_room, name="create-room"),
    path('update-room/<str:pk>', views.update_room, name="update-room"),
    path('delete-room/<str:pk>', views.delete_room, name="delete-room"),
    path('delete-message/<str:pk>', views.delete_message, name="delete-message"),

]
