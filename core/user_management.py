"""
Module de gestion des utilisateurs
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers, viewsets, permissions
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les utilisateurs - ID masqué pour le frontend"""
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'role', 'service', 'adresse', 'badge_rfid', 'telephone', 'is_active', 'date_joined']

    def get_role_choices(self):
        # Supprime "Entraîner" des choix
        all_choices = User._meta.get_field('role').choices
        return [choice for choice in all_choices if choice[0] != 'entraineur']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Applique les nouveaux choix (sans Entraîner)
        if 'role' in self.fields:
            self.fields['role'].choices = self.get_role_choices()

    def create(self, validated_data):
        from django.core.mail import send_mail
        from django.conf import settings

        raw_password = validated_data.get('password')
        email = validated_data.get('email')
        username = validated_data.get('username')
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')

        validated_data['password'] = make_password(raw_password)
        user = super().create(validated_data)

        # Assigner les droits Django correspondant au rôle
        role = validated_data.get('role', 'employe')
        user.is_staff = role in ['admin', 'rh']
        user.is_superuser = role == 'admin'
        user.save()

        if email:
            role_display = {
                'admin': 'Administrateur',
                'rh': 'Ressources Humaines (RH)',
                'employe': 'Employé'
            }.get(role, role)

            subject = "Création de votre compte - TRACKTIME"
            
            # Construire les détails de profil
            profile_details = [
                f"Nom complet : {first_name} {last_name}".strip(),
                f"E-mail : {email}",
                f"Nom d'utilisateur : {username}",
                f"Rôle : {role_display}",
                f"Service/Adresse : {validated_data.get('service') or 'Non spécifié'}",
                f"Téléphone : {validated_data.get('telephone') or 'Non spécifié'}"
            ]
            
            badge_rfid = validated_data.get('badge_rfid')
            if badge_rfid:
                profile_details.append(f"Badge RFID : {badge_rfid}")
                
            face_id = validated_data.get('face_id')
            if face_id:
                profile_details.append(f"Face ID : {face_id}")

            profile_details_text = "\n".join(profile_details)

            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
            message = f"""Bonjour {first_name} {last_name},


Votre compte a été créé avec succès sur la plateforme TRACKTIME.

Voici les détails de votre profil :
----------------------------------------
{profile_details_text}
----------------------------------------

Voici vos informations de connexion :
----------------------------------------
Identifiant (Nom d'utilisateur ou E-mail) : {username} / {email}
Mot de passe : {raw_password}
----------------------------------------

Vous pouvez vous connecter à l'application à l'adresse suivante :
URL de connexion : {frontend_url}/

Veuillez conserver ces informations précieusement et modifier votre mot de passe lors de votre première connexion.

Cordialement,
L'équipe RH - TRACKTIME"""
            try:
                send_mail(
                    subject,
                    message,
                    getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@unipro.com'),
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email : {e}")

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:  # Ne hasher et mettre à jour que si un mot de passe non-vide est fourni
            instance.password = make_password(password)
        
        user = super().update(instance, validated_data)
        
        # Mettre à jour les privilèges si le rôle a changé
        if 'role' in validated_data:
            role = validated_data['role']
            user.is_staff = role in ['admin', 'rh']
            user.is_superuser = role == 'admin'
            user.save()
            
        return user


class IsAdminOnly(permissions.BasePermission):
    """Permission réservée à l'admin uniquement (CRUD complet)"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_staff or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdminOrRHReadOnly(permissions.BasePermission):
    """Admin : accès complet. RH : lecture seule (GET, HEAD, OPTIONS)."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Admin = accès total
        if request.user.is_staff or request.user.is_superuser:
            return True
        # RH = lecture seule
        if getattr(request.user, 'role', None) == 'rh':
            return request.method in permissions.SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des utilisateurs"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Admin : CRUD complet | RH : GET uniquement
    permission_classes = [IsAdminOrRHReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = instance.username
        instance.delete()
        return Response({
            "message": f"L'utilisateur '{username}' a été supprimé avec succès."
        }, status=status.HTTP_200_OK)
