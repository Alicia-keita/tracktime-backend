"""
Consommateurs WebSocket Django Channels pour TrackTime.

- ChatConsumer     : Chat temps réel entre employés et RH
- NotificationConsumer : Notifications push (pointages RFID, alertes)
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


# ─── Authentification JWT via WebSocket ────────────────────────────────────────

async def get_user_from_token(token: str):
    """
    Vérifie un token JWT passé en query param (?token=...)
    et retourne l'utilisateur Django correspondant ou None.
    """
    try:
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from jwt import decode as jwt_decode
        from django.conf import settings

        # Valider le token
        UntypedToken(token)

        # Décoder pour obtenir l'user_id
        decoded = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id")
        if not user_id:
            return None

        user = await database_sync_to_async(User.objects.get)(id=user_id)
        return user
    except Exception:
        return None


# ─── ChatConsumer ──────────────────────────────────────────────────────────────

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket pour le chat en temps réel.

    Chaque utilisateur rejoint son groupe personnel `chat_<user_id>`.
    L'expéditeur précise le `receiver_id` dans le message JSON.
    Le serveur diffuse le message au groupe du destinataire ET à celui de l'expéditeur.

    Protocole (JSON) :
      Envoi    → { "message": "...", "receiver_id": 42 }
      Réception← { "type": "chat_message", "message": "...", "sender_id": 7,
                   "sender_name": "Jean Dupont", "sender_role": "employe",
                   "receiver_id": 42, "timestamp": "2025-01-01T10:00:00Z" }
    """

    async def connect(self):
        # Authentification via token JWT dans l'URL (?token=...)
        token = self.scope['query_string'].decode()
        if token.startswith('token='):
            token = token[len('token='):]

        self.user = await get_user_from_token(token)

        if not self.user:
            # Refus de connexion si non authentifié
            await self.close(code=4001)
            return

        # Groupe personnel de cet utilisateur
        self.room_group_name = f'chat_{self.user.id}'

        # Rejoindre son groupe personnel
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Rejoindre le groupe collectif RH si le rôle est rh
        if self.user.role == 'rh':
            await self.channel_layer.group_add(
                'chat_rh',
                self.channel_name
            )

        await self.accept()
        print(f"[WS CHAT] Connexion : {self.user.username} (rôle: {self.user.role})")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            if self.user.role == 'rh':
                await self.channel_layer.group_discard(
                    'chat_rh',
                    self.channel_name
                )
            print(f"[WS CHAT] Déconnexion : {getattr(self, 'user', '?')}")

    async def receive(self, text_data):
        """Reçoit un message du client WebSocket et le diffuse."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "JSON invalide"}))
            return

        message = data.get('message', '').strip()
        receiver_id = data.get('receiver_id')

        if not message:
            return

        # Persister le message en base de données
        chat_msg = await self._save_message(message, receiver_id)
        if not chat_msg:
            await self.send(text_data=json.dumps({"error": "Impossible d'envoyer le message"}))
            return

        # Déterminer l'ID de l'employé concerné
        employee_id = receiver_id if self.user.role == 'rh' else self.user.id

        # Invalider le cache unread_count
        if self.user.role == 'rh':
            cache.delete(f'chat:unread:{employee_id}')
        else:
            cache.delete('chat:unread:rh')

        # Construire le payload
        payload = {
            'type': 'chat_message',
            'id': chat_msg['id'],
            'message': message,
            'sender_id': self.user.id,
            'sender_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
            'sender_role': self.user.role,
            'receiver_id': receiver_id,
            'timestamp': chat_msg['timestamp'],
        }

        # Diffuser au groupe de l'employé
        employee_group = f'chat_{employee_id}'
        await self.channel_layer.group_send(employee_group, payload)

        # Diffuser au groupe collectif des RH
        await self.channel_layer.group_send('chat_rh', payload)

    async def chat_message(self, event):
        """Handler appelé quand un message est broadcasté dans le groupe."""
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'id': event['id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_role': event['sender_role'],
            'receiver_id': event['receiver_id'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def _save_message(self, message: str, receiver_id):
        """Sauvegarde le message en DB et retourne un dict."""
        from core.chat import ChatMessage
        try:
            receiver = None
            if receiver_id:
                receiver = User.objects.get(id=receiver_id)

            # Les employés envoient toujours sans receiver (vers les RH)
            if self.user.role != 'rh':
                receiver = None

            msg = ChatMessage.objects.create(
                sender=self.user,
                receiver=receiver,
                message=message,
            )
            return {
                'id': msg.id,
                'timestamp': msg.timestamp.isoformat(),
            }
        except Exception as e:
            print(f"[WS CHAT] Erreur sauvegarde message : {e}")
            return None


# ─── NotificationConsumer ──────────────────────────────────────────────────────

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket pour les notifications push en temps réel.

    Utilisé pour notifier le frontend quand :
    - Un badge RFID scanne (pointage enregistré)
    - Un congé est approuvé/refusé
    - Une demande de permission est traitée

    Protocole (JSON reçu par le frontend) :
      { "type": "pointage", "user": "Jean Dupont", "heure": "08:32", "statut": "present" }
      { "type": "conge", "action": "approuve", "employe": "Marie Keita" }
    """

    GLOBAL_GROUP = 'notifications_global'

    async def connect(self):
        # Authentification via token JWT
        token = self.scope['query_string'].decode()
        if token.startswith('token='):
            token = token[len('token='):]

        self.user = await get_user_from_token(token)

        if not self.user:
            await self.close(code=4001)
            return

        # Groupe global (admin/RH) et groupe personnel
        self.personal_group = f'notif_{self.user.id}'

        await self.channel_layer.group_add(self.personal_group, self.channel_name)

        # Admin et RH rejoignent aussi le groupe global (pour voir tous les pointages)
        if self.user.role in ['admin', 'rh']:
            await self.channel_layer.group_add(self.GLOBAL_GROUP, self.channel_name)

        await self.accept()
        print(f"[WS NOTIF] Connexion : {self.user.username} (rôle: {self.user.role})")

    async def disconnect(self, close_code):
        if hasattr(self, 'personal_group'):
            await self.channel_layer.group_discard(self.personal_group, self.channel_name)
            if self.user.role in ['admin', 'rh']:
                await self.channel_layer.group_discard(self.GLOBAL_GROUP, self.channel_name)

    async def receive(self, text_data):
        # Les clients ne sont pas censés envoyer de données ici (lecture seule)
        pass

    async def notification(self, event):
        """Handler pour diffuser une notification au client WebSocket."""
        await self.send(text_data=json.dumps(event))


# ─── Helpers (appelables depuis le code Django classique) ──────────────────────

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_pointage(user_display: str, heure: str, statut: str, employee_id: int = None):
    """
    Envoie une notification de pointage à tous les admin/RH connectés en WebSocket.
    Appel depuis apps.py (thread MQTT) ou un signal Django.
    
    Usage :
        from core.consumers import broadcast_pointage
        broadcast_pointage("Jean Dupont", "08:32", "present", employee_id=7)
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    try:
        async_to_sync(channel_layer.group_send)(
            NotificationConsumer.GLOBAL_GROUP,
            {
                'type': 'notification',
                'notification_type': 'pointage',
                'user': user_display,
                'heure': heure,
                'statut': statut,
                'employee_id': employee_id,
            }
        )
    except Exception as e:
        print(f"[WS NOTIF] Erreur broadcast pointage : {e}")


def broadcast_conge(employe: str, action: str, conge_id: int = None, target_user_id: int = None):
    """
    Envoie une notification de congé à un employé spécifique ou à tous les RH.
    
    Usage :
        from core.consumers import broadcast_conge
        broadcast_conge("Marie Keita", "approuve", target_user_id=12)
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    try:
        group = f'notif_{target_user_id}' if target_user_id else NotificationConsumer.GLOBAL_GROUP
        async_to_sync(channel_layer.group_send)(
            group,
            {
                'type': 'notification',
                'notification_type': 'conge',
                'employe': employe,
                'action': action,
                'conge_id': conge_id,
            }
        )
    except Exception as e:
        print(f"[WS NOTIF] Erreur broadcast congé : {e}")
