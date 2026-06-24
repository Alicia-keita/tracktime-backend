from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from .models import User
from .serializers import UserSerializer


# 🔐 Permission Admin uniquement
class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD Users (Admin only)
    Utilisé pour :
    - gestion employés
    - association RFID badge
    - administration système
    """

    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminOnly]

    # 🔥 Response propre création
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Utilisateur créé avec succès",
            "data": response.data
        }, status=status.HTTP_201_CREATED)

    # 🔥 Response propre update
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Utilisateur modifié avec succès",
            "data": response.data
        })

    # 🔥 Delete amélioré
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = instance.username
        self.perform_destroy(instance)

        return Response({
            "message": f"Utilisateur '{username}' supprimé avec succès"
        }, status=status.HTTP_200_OK)