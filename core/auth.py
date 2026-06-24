"""
Module d'authentification JWT
"""

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.views import APIView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personnalisé pour inclure plus d'informations dans le token"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Ajouter des informations supplémentaires à la réponse
        data.update({
            'user_id': self.user.id,
            'username': self.user.username,
            'role': self.user.role,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        })
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue personnalisée pour obtenir les tokens JWT"""
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(APIView):
    """Vue pour obtenir le profil de l'utilisateur connecté"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Utilisateur non authentifié"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
            'service': user.service,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })


class AuthSystem:
    """Classe principale pour gérer l'authentification"""
    
    @staticmethod
    def get_login_view():
        """Retourne la vue de login"""
        return CustomTokenObtainPairView.as_view()
    
    @staticmethod
    def get_refresh_view():
        """Retourne la vue de rafraîchissement"""
        return TokenRefreshView.as_view()
    
    @staticmethod
    def get_profile_view():
        """Retourne la vue de profil"""
        return UserProfileView.as_view()
    
    @staticmethod
    def authenticate_user(username, password):
        """Authentifie un utilisateur"""
        user = authenticate(username=username, password=password)
        if user is not None:
            return user
        return None
    
    @staticmethod
    def get_user_permissions(user):
        """Retourne les permissions de l'utilisateur"""
        permissions = {
            'can_create_permission': user.role == 'employe',
            'can_approve_permission': user.role in ['rh', 'admin'],
            'can_generate_bulletin': user.role in ['rh', 'admin'],
            'can_delete_bulletin': user.role == 'admin' or user.is_staff or user.is_superuser,
            'can_manage_users': user.is_staff or user.is_superuser,
        }
        return permissions
