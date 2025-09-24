from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import ChatRoom, Message

@login_required
def chat_list(request):
    """Lista de chats del usuario"""
    rooms = request.user.chatrooms.all()
    return render(request, 'chat/chat_list.html', {'rooms': rooms})

@login_required
def chat_room(request, user_id):
    """Chat entre el usuario actual y otro"""
    other_user = get_object_or_404(User, pk=user_id)
    room_qs = ChatRoom.objects.filter(participants=request.user).filter(participants=other_user)
    
    if room_qs.exists():
        room = room_qs.first()
    else:
        room = ChatRoom.objects.create()
        room.participants.add(request.user, other_user)

    messages = room.messages.all()
    return render(request, 'chat/chat_room.html', {
        'room': room,
        'messages': messages,
        'other_user': other_user
    })

@login_required
def send_message(request):
    """Enviar mensaje vía AJAX"""
    if request.method == "POST":
        room_id = request.POST.get('room_id')
        content = request.POST.get('content')
        room = get_object_or_404(ChatRoom, id=room_id)
        message = Message.objects.create(room=room, sender=request.user, content=content)
        return JsonResponse({
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime("%H:%M")
        })
    return JsonResponse({'error': 'Invalid request'})
