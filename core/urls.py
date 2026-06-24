"""
Module des URLs pour le système core avec authentification complète
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .permissions import PermissionRequestViewSet
from .bulletin import BulletinViewSet
from .user_management import UserViewSet
from .conges import CongeViewSet
from .solde import SoldeViewSet
from .rapport import RapportViewSet
from .pointage import PointageViewSet
from .chat import ChatMessageViewSet
from .auth_complete import (
    register, login, refresh_token, profile, update_profile,
    change_password, reset_password, logout, user_permissions
)

# Créer les routeurs
router = DefaultRouter()
router.register(r'permissions', PermissionRequestViewSet)
router.register(r'bulletins', BulletinViewSet)
router.register(r'users', UserViewSet)
router.register(r'conges', CongeViewSet)
router.register(r'soldes', SoldeViewSet)
router.register(r'rapports', RapportViewSet)
router.register(r'pointages', PointageViewSet)
router.register(r'chat', ChatMessageViewSet)

urlpatterns = [
    # Routes des ViewSets
    path('', include(router.urls)),
    
    # Routes d'authentification complètes
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/refresh/', refresh_token, name='refresh_token'),
    path('auth/logout/', logout, name='logout'),
    path('auth/profile/', profile, name='profile'),
    path('auth/me/', profile, name='me'),  # Alias pour /profile/
    path('auth/profile/update/', update_profile, name='update_profile'),
    path('auth/password/change/', change_password, name='change_password'),
    path('auth/password/reset/', reset_password, name='reset_password'),
    path('auth/permissions/', user_permissions, name='user_permissions'),
    
    # Endpoints JWT standards (pour compatibilité)
    path('token/', login, name='token_obtain'),  # Alias vers login
    path('token/refresh/', refresh_token, name='token_refresh'),
]
