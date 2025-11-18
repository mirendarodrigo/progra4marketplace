from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.timezone import localtime
from django.db.models import Count, Q
import os

from .models import Conversation, Message
from .forms import MessageForm

User = get_user_model()


def _get_or_create_conversation(user_a, user_b):
    convo = (
        Conversation.objects.filter(participants=user_a)
        .filter(participants=user_b)
        .first()
    )
    if not convo:
        convo = Conversation.objects.create()
        convo.participants.add(user_a, user_b)
    return convo


@login_required
def inbox(request):
    """Centro de conversaciones: si hay alguna, te lleva a la más reciente."""
    convo = (
        Conversation.objects.filter(participants=request.user)
        .order_by("-created_at")
        .first()
    )
    if convo:
        return redirect("chat:room", convo_id=convo.id)
    return render(request, "chat/inbox_empty.html")


@login_required
def start_chat(request, user_id):
    other = get_object_or_404(User, pk=user_id)
    convo = _get_or_create_conversation(request.user, other)

    title = (request.GET.get("title") or "").strip()
    price = (request.GET.get("price") or "").strip()
    brand = (request.GET.get("brand") or "").strip()

    if title or price or brand:
        initial_text = (
            f"Estoy interesado en '{title}' de valor ${price} de la marca {brand}".strip()
        )
        last = convo.messages.order_by("-id").first()
        if not last or last.text != initial_text or last.sender_id != request.user.id:
            Message.objects.create(
                conversation=convo,
                sender=request.user,
                text=initial_text,
            )

    return redirect("chat:room", convo_id=convo.id)


@login_required
def room(request, convo_id):
    convo = get_object_or_404(
        Conversation,
        pk=convo_id,
        participants=request.user,
    )

    # 👇 MARCAR COMO LEÍDOS LOS MENSAJES QUE NO SON MÍOS EN ESTA CONVERSACIÓN
    Message.objects.filter(
        conversation=convo,
        is_read=False,
    ).exclude(sender=request.user).update(is_read=True)

    if request.method == "POST":
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.conversation = convo
            msg.sender = request.user
            msg.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {"ok": True, "message": _serialize_message(msg, request.user.id)}
                )
            return redirect("chat:room", convo_id=convo.id)
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    else:
        form = MessageForm()

    user_convos = (
    Conversation.objects
    .filter(participants=request.user)
    .annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
        )
    )
    .order_by('-created_at')
    )
    msgs = convo.messages.select_related("sender").all()
    return render(
        request,
        "chat/room.html",
        {
            "conversation": convo,
            "messages": msgs,
            "form": form,
            "conversations": user_convos,
        },
    )


def _attachment_kind(url: str) -> str:
    if not url:
        return "file"
    ext = os.path.splitext(url.lower())[1]
    if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        return "image"
    if ext in [".mp4", ".webm", ".ogv", ".ogg"]:
        return "video"
    if ext in [".mp3", ".wav", ".m4a", ".ogg"]:
        return "audio"
    return "file"


def _serialize_message(m: Message, me_id: int) -> dict:
    url = m.attachment.url if m.attachment else None
    return {
        "id": m.id,
        "text": m.text or "",
        "attachment_url": url,
        "attachment_kind": _attachment_kind(url) if url else None,
        "created_at": localtime(m.created_at).strftime("%d/%m %H:%M"),
        "sender_id": m.sender_id,
        "sender_name": m.sender.get_full_name() or m.sender.username,
        "is_me": m.sender_id == me_id,
    }


@login_required
@require_GET
def messages_since(request, convo_id):
    convo = get_object_or_404(
        Conversation,
        pk=convo_id,
        participants=request.user,
    )
    try:
        after = int(request.GET.get("after", "0"))
    except ValueError:
        return HttpResponseBadRequest("param 'after' inválido")

    qs = (
        convo.messages.select_related("sender")
        .filter(id__gt=after)
        .order_by("id")
    )
    data = [_serialize_message(m, request.user.id) for m in qs]

    # 👇 lo que acabo de recibir y NO son míos, los marco como leídos
    qs.exclude(sender=request.user).update(is_read=True)

    return JsonResponse({"messages": data})


@login_required
@require_POST
def api_send(request, convo_id):
    convo = get_object_or_404(
        Conversation,
        pk=convo_id,
        participants=request.user,
    )
    form = MessageForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    msg = form.save(commit=False)
    msg.conversation = convo
    msg.sender = request.user
    msg.save()
    return JsonResponse(
        {"ok": True, "message": _serialize_message(msg, request.user.id)}
    )
