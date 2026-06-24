"""
Module de gestion des permissions de demande
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class PermissionRequest(models.Model):
    """Modèle pour les demandes de permission"""
    
    TYPE_PERMISSION_CHOICES = [
        ('permission', 'Permission'),
        ('leave', 'Congé'),
        ('absence', 'Absence'),
        ('sick_leave', 'Arrêt maladie'),
        ('maternity', 'Congé maternité'),
        ('paternity', 'Congé paternité'),
        ('unpaid', 'Congé sans solde'),
    ]
    
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permission_requests')
    type_permission = models.CharField(max_length=20, choices=TYPE_PERMISSION_CHOICES)
    date_sortie = models.DateTimeField(verbose_name="Date de sortie")
    date_retour = models.DateTimeField(verbose_name="Date de retour")
    motif = models.TextField(verbose_name="Motif")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name="Date de demande")
    date_traitement = models.DateTimeField(null=True, blank=True, verbose_name="Date de traitement")
    rh_traitant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='permissions_traitees', verbose_name="RH traitant")
    commentaire_rh = models.TextField(blank=True, verbose_name="Commentaire RH")

    class Meta:
        verbose_name = "Demande de permission"
        verbose_name_plural = "Demandes de permission"
        ordering = ['-date_demande']

    def __str__(self):
        return f"Demande {self.type_permission} - {self.employee.username} ({self.get_status_display()})"


class PermissionRequestSerializer(serializers.ModelSerializer):
    """Serializer pour les demandes de permission - ID masqué pour le frontend"""
    employee_name = serializers.CharField(source='employee.username', read_only=True)
    employee_first_name = serializers.CharField(source='employee.first_name', read_only=True)
    employee_last_name = serializers.CharField(source='employee.last_name', read_only=True)
    rh_traitant_name = serializers.CharField(source='rh_traitant.username', read_only=True)
    type_permission_display = serializers.CharField(source='get_type_permission_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reference = serializers.CharField(source='id', read_only=True)  # ID technique sous un autre nom

    class Meta:
        model = PermissionRequest
        fields = [
            'reference', 'employee', 'employee_name', 'employee_first_name', 'employee_last_name',
            'type_permission', 'type_permission_display', 'date_sortie', 'date_retour', 
            'motif', 'status', 'status_display', 'date_demande', 'date_traitement',
            'rh_traitant', 'rh_traitant_name', 'commentaire_rh'
        ]
        read_only_fields = ['reference', 'employee', 'date_demande', 'date_traitement', 'rh_traitant']

    def validate(self, data):
        print(f'[DEBUG] PermissionRequestSerializer validate - data: {data}')
        if 'date_sortie' in data and 'date_retour' in data:
            if data['date_sortie'] >= data['date_retour']:
                raise serializers.ValidationError(
                    "La date de retour doit être postérieure à la date de sortie."
                )
        
        # Vérifier les conflits de permissions
        if self.context.get('request'):
            employee = self.context['request'].user
            date_sortie = data.get('date_sortie')
            date_retour = data.get('date_retour')
            if date_sortie and date_retour:
                conflits = PermissionRequest.objects.filter(
                    employee=employee,
                    status__in=['en_attente', 'approuve'],
                    date_sortie__lt=date_retour,
                    date_retour__gt=date_sortie
                )
                # Exclure l'instance actuelle si c'est une mise à jour
                if self.instance:
                    conflits = conflits.exclude(pk=self.instance.pk)
                
                if conflits.exists():
                    # Afficher les détails de la demande existante
                    conflit = conflits.first()
                    ds = conflit.date_sortie.strftime('%d/%m/%Y')
                    dr = conflit.date_retour.strftime('%d/%m/%Y')
                    type_disp = conflit.get_type_permission_display()
                    raise serializers.ValidationError(
                        f"Vous avez déjà une demande ({type_disp}) du {ds} au {dr}. "
                        f"Vérifiez vos demandes existantes."
                    )
        
        return data


class PermissionRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionRequest
        fields = ['status', 'commentaire_rh']

    def validate(self, data):
        if 'status' in data and data['status'] not in ['approuve', 'rejete']:
            raise serializers.ValidationError(
                "Le statut doit être 'approuve' ou 'rejete'."
            )
        return data


class IsEmployeeOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'employe'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return obj.employee == request.user


class IsRHOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['rh', 'admin']

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class PermissionRequestViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des demandes de permission"""
    queryset = PermissionRequest.objects.all()
    serializer_class = PermissionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from .role_utils import is_admin_or_rh
        user = self.request.user
        if is_admin_or_rh(user):
            return PermissionRequest.objects.all()
        return PermissionRequest.objects.filter(employee=user)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return PermissionRequestUpdateSerializer
        return PermissionRequestSerializer

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    def create(self, request, *args, **kwargs):
        """Surcharge de create pour ajouter des logs"""
        print(f'[DEBUG] PermissionViewSet.create - data: {request.data}')
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f'[DEBUG] Serializer errors: {serializer.errors}')
            raise serializers.ValidationError(serializer.errors)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['patch'], permission_classes=[IsRHOrAdmin])
    def approve(self, request, pk=None):
        """Approuver une demande de permission"""
        permission_request = self.get_object()
        
        if permission_request.status != 'en_attente':
            return Response(
                {"error": "Cette demande a déjà été traitée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permission_request.status = 'approuve'
        permission_request.rh_traitant = request.user
        permission_request.date_traitement = timezone.now()
        permission_request.save()
        
        serializer = self.get_serializer(permission_request)
        return Response({
            "message": "Demande approuvée avec succès.",
            "permission_request": serializer.data
        })

    @action(detail=True, methods=['patch'], permission_classes=[IsRHOrAdmin])
    def reject(self, request, pk=None):
        """Rejeter une demande de permission"""
        permission_request = self.get_object()
        
        if permission_request.status != 'en_attente':
            return Response(
                {"error": "Cette demande a déjà été traitée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permission_request.status = 'rejete'
        permission_request.rh_traitant = request.user
        permission_request.date_traitement = timezone.now()
        permission_request.commentaire_rh = request.data.get('commentaire_rh', '')
        permission_request.save()
        
        serializer = self.get_serializer(permission_request)
        return Response({
            "message": "Demande rejetée.",
            "permission_request": serializer.data
        })

    @action(detail=False, methods=['get'], permission_classes=[IsRHOrAdmin])
    def pending(self, request):
        """Lister toutes les demandes en attente"""
        pending_requests = PermissionRequest.objects.filter(status='en_attente')
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Supprimer une demande (uniquement l'employé concerné)"""
        instance = self.get_object()
        
        if request.user.role not in ['admin'] and instance.employee != request.user:
            return Response(
                {"error": "Vous ne pouvez supprimer que vos propres demandes."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance.delete()
        return Response(
            {"message": "Demande supprimée avec succès."},
            status=status.HTTP_200_OK
        )
