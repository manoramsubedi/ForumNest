from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from django.db.models import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

# rooms = [
#     {'id':1, 'name': 'Learn Python'},
#     {'id':2, 'name': 'Learn Java'},
#     {'id':3, 'name': 'Learn C++'},
# ]

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')


    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')


        try: #if user exist
            user = User.objects.get(email=email)
        except: #if user doesn't exist
            messages.add_message(request, messages.INFO, "User Not Found!")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.add_message(request, messages.INFO, "Username or Password doesnot exist!")



    context = {'page':page}
    return render(request, "base/login_register.html", context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    #page = 'register'
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.add_message(request, messages.INFO, "An error occured during registration")

    context = {'form':form}
    return render(request, 'base/login_register.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()

    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, "base/home.html", context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body') #body is from the comment form
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room':room, 'room_messages':room_messages, 'participants':participants}
    return render(request, "base/room.html",context)

@login_required(login_url='/login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name) #if there's no user inputted topic, it creates one

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        #form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit = False)
        #     room.host = request.user # setting host who ever is logged in / who ever trying to create room
        #     room.save()

        return redirect('home')

    context = {'form':form, 'topics': topics}
    return render(request, "base/room_form.html", context)

@login_required(login_url='/login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    form = RoomForm(instance=room) #pre-fill form

    if request.user != room.host:
        return HttpResponse('You are not authorized to perform this action!!')

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')


    context = {'form': form, 'topics':topics, 'room':room}
    return render(request, "base/room_form.html",context)

@login_required(login_url='/login')
def delete_room(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not authorized to perform this action!!')


    if request.method=="POST":
        room.delete()
        return redirect('home')

    context = {'obj':room}
    return render(request, "base/delete.html", context)


@login_required(login_url='/login')
def delete_message(request,pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not authorized to perform this action!!')


    if request.method=="POST":
        message.delete()
        return redirect('home')

    context = {'obj':message.body}
    return render(request, "base/delete.html", context)


@login_required(login_url='/login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES ,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form':form}
    return render(request, 'base/update_user.html', context)

def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics':topics}
    return render(request, 'base/topics.html', context)


def activity(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)