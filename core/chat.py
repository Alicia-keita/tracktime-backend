from django.db import models
from django.contrib.auth import get_user_model
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

User = get_user_model()

class ChatMessage(models.Model):
    """Modèle pour stocker les messages du chat entre les employés/admins et les RH"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Message Chat"
        verbose_name_plural = "Messages Chat"
        ordering = ['timestamp']

    def __str__(self):
        sender_name = f"{self.sender.first_name} {self.sender.last_name}" if self.sender.first_name else self.sender.username
        receiver_name = f"{self.receiver.first_name} {self.receiver.last_name}" if self.receiver and self.receiver.first_name else (self.receiver.username if self.receiver else "RH (Général)")
        return f"De {sender_name} à {receiver_name} : {self.message[:30]} ({self.timestamp})"

    @property
    def sender_name(self):
        if self.sender.first_name or self.sender.last_name:
            return f"{self.sender.first_name} {self.sender.last_name}".strip()
        return self.sender.username

    @property
    def sender_role(self):
        return self.sender.role

    @property
    def receiver_name(self):
        if not self.receiver:
            return "RH (Général)"
        if self.receiver.first_name or self.receiver.last_name:
            return f"{self.receiver.first_name} {self.receiver.last_name}".strip()
        return self.receiver.username

    @property
    def receiver_role(self):
        return self.receiver.role if self.receiver else "rh"


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(read_only=True)
    sender_role = serializers.CharField(read_only=True)
    receiver_name = serializers.CharField(read_only=True)
    receiver_role = serializers.CharField(read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender', 'sender_name', 'sender_role',
            'receiver', 'receiver_name', 'receiver_role',
            'message', 'timestamp', 'is_read'
        ]
        read_only_fields = ['id', 'sender', 'timestamp', 'is_read']


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'rh':
            user_id = self.request.query_params.get('user_id')
            if user_id:
                # Thread of a specific user
                return ChatMessage.objects.filter(
                    models.Q(sender_id=user_id) | models.Q(receiver_id=user_id)
                ).order_by('timestamp')
            # RH sees their own direct messages or general ones
            return ChatMessage.objects.filter(
                models.Q(sender=user) | models.Q(receiver=user) | models.Q(receiver__isnull=True)
            ).order_by('timestamp')
        else:
            # Employee/Admin sees their own thread (messages sent by them, or received by them)
            return ChatMessage.objects.filter(
                models.Q(sender=user) | models.Q(receiver=user)
            ).order_by('timestamp')

    def perform_create(self, serializer):
        from django.core.cache import cache
        user = self.request.user
        if user.role == 'rh':
            receiver_id = self.request.data.get('receiver')
            if not receiver_id:
                raise serializers.ValidationError({"receiver": "Le destinataire est requis pour les RH."})
            try:
                receiver = User.objects.get(id=receiver_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({"receiver": "Destinataire introuvable."})
            serializer.save(sender=user, receiver=receiver)
            # Invalider le cache unread_count du destinataire (employé)
            cache.delete(f'chat:unread:{receiver.id}')
        else:
            # Employees and admins send messages to HR (receiver is None)
            serializer.save(sender=user, receiver=None)
            # Invalider le cache unread_count global des RH
            cache.delete('chat:unread:rh')

    @action(detail=False, methods=['get'])
    def contacts(self, request):
        user = request.user
        if user.role != 'rh':
            return Response({"error": "Accès réservé aux RH."}, status=status.HTTP_403_FORBIDDEN)

        # List all users with role 'employe' or 'admin'
        contacts = User.objects.filter(role__in=['employe', 'admin']).order_by('first_name', 'last_name')
        
        data = []
        for contact in contacts:
            # Get last message
            last_msg = ChatMessage.objects.filter(
                models.Q(sender=contact) | models.Q(receiver=contact)
            ).order_by('-timestamp').first()
            
            # Count unread messages (messages sent by contact, where is_read is False)
            unread_count = ChatMessage.objects.filter(
                sender=contact,
                is_read=False
            ).count()

            data.append({
                "id": contact.id,
                "username": contact.username,
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "role": contact.role,
                "service": contact.service,
                "last_message": last_msg.message if last_msg else None,
                "last_message_time": last_msg.timestamp if last_msg else None,
                "unread_count": unread_count
            })

        # Sorting logic: unread first, then by last_message_time desc, then alphabetically
        def sort_key(item):
            has_unread = item['unread_count'] > 0
            last_time = item['last_message_time']
            time_val = last_time.timestamp() if last_time else 0
            return (not has_unread, -time_val, item['first_name'], item['last_name'])

        data.sort(key=sort_key)
        return Response(data)

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        from django.core.cache import cache
        user = request.user
        if user.role == 'rh':
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({"error": "Le paramètre user_id est requis."}, status=status.HTTP_400_BAD_REQUEST)
            # Mark messages sent by the employee as read
            ChatMessage.objects.filter(sender_id=user_id, is_read=False).update(is_read=True)
            # Invalider le cache global des RH
            cache.delete('chat:unread:rh')
        else:
            # Mark messages received by this user from any HR user as read
            # Since sender is a HR user, we check sender__role='rh' and receiver=user
            ChatMessage.objects.filter(sender__role='rh', receiver=user, is_read=False).update(is_read=True)
            # Also cover case where receiver is null but sender is rh
            ChatMessage.objects.filter(receiver=user, is_read=False).update(is_read=True)
            # Invalider le cache de l'utilisateur
            cache.delete(f'chat:unread:{user.id}')

        return Response({"message": "Messages marqués comme lus."})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        from django.core.cache import cache
        user = request.user
        if user.role == 'rh':
            cache_key = 'chat:unread:rh'
            count = cache.get(cache_key)
            if count is None:
                count = ChatMessage.objects.filter(sender__role__in=['employe', 'admin'], is_read=False).count()
                cache.set(cache_key, count, timeout=300)
        else:
            cache_key = f'chat:unread:{user.id}'
            count = cache.get(cache_key)
            if count is None:
                count = ChatMessage.objects.filter(receiver=user, is_read=False).count()
                cache.set(cache_key, count, timeout=300)
        return Response({"unread_count": count})
