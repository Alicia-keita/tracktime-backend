"""
Module de gestion des congés
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class Conge(models.Model):
    """Modèle pour les demandes de congé"""
    
    TYPE_CONGE_CHOICES = [
        ('annuel', 'Congé Annuel'),
        ('maladie', 'Congé Maladie'),
        ('maternite', 'Congé Maternité'),
        ('paternite', 'Congé Paternité'),
        ('sans_solde', 'Congé Sans Solde'),
        ('exceptionnel', 'Congé Exceptionnel'),
        ('formation', 'Congé Formation'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En Attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
        ('annule', 'Annulé'),
    ]
    
    # Informations de base
    employe = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conges')
    type_conge = models.CharField(max_length=20, choices=TYPE_CONGE_CHOICES)
    
    # Dates
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    duree_jours = models.IntegerField(help_text="Durée en jours ouvrés")
    
    # Statut et validation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='conges_valides')
    
    # Informations complémentaires
    motif = models.TextField(help_text="Motif de la demande de congé")
    commentaire_rh = models.TextField(blank=True, help_text="Commentaire du RH/Admin")
    
    # Documents joints
    document_attache = models.FileField(upload_to='documents_conges/', null=True, blank=True)
    
    # Solde de congés
    solde_avant = models.DecimalField(max_digits=4, decimal_places=1, default=0.0, 
                                     help_text="Solde de congés avant cette demande")
    solde_apres = models.DecimalField(max_digits=4, decimal_places=1, default=0.0,
                                   help_text="Solde de congés après cette demande")
    
    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"
        ordering = ['-date_demande']
    
    def __str__(self):
        return f"Congé {self.get_type_conge_display()} - {self.employe.username} ({self.date_debut.date()})"
    
    @property
    def employe_name(self):
        """Nom complet de l'employé"""
        return f"{self.employe.first_name} {self.employe.last_name}"
    
    @property
    def employe_service(self):
        """Service de l'employé"""
        return self.employe.service
    
    @property
    def type_conge_display(self):
        """Affichage du type de congé"""
        return dict(self.TYPE_CONGE_CHOICES).get(self.type_conge, self.type_conge)
    
    @property
    def statut_display(self):
        """Affichage du statut"""
        return dict(self.STATUT_CHOICES).get(self.statut, self.statut)
    
    def clean(self):
        """Validation du modèle"""
        if self.date_fin <= self.date_debut:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")
        
        if self.duree_jours <= 0:
            raise ValidationError("La durée doit être positive.")
    
    def save(self, *args, **kwargs):
        """Surcharge de la sauvegarde pour mettre à jour les soldes"""
        if not self.pk:  # Nouvelle demande
            # Calculer le solde avant (à implémenter selon la logique métier)
            self.solde_avant = self.calculer_solde_conges()
            self.solde_apres = max(0, self.solde_avant - self.duree_jours)
        
        super().save(*args, **kwargs)
    
    def calculer_solde_conges(self):
        """Calculer le solde de congés de l'employé (logique à implémenter)"""
        # Logique de base : 25 jours par an
        # À adapter selon les règles de l'entreprise
        return 25.0


# Serializers
class CongeSerializer(serializers.ModelSerializer):
    """Serializer pour les demandes de congé - ID masqué pour le frontend"""
    employe_name = serializers.CharField(read_only=True)
    employe_service = serializers.CharField(read_only=True)
    type_conge_display = serializers.CharField(read_only=True)
    statut_display = serializers.CharField(read_only=True)
    reference = serializers.CharField(source='id', read_only=True)  # ID technique sous un autre nom
    
    class Meta:
        model = Conge
        fields = [
            'reference', 'employe', 'employe_name', 'employe_service',
            'type_conge', 'type_conge_display', 'date_debut', 'date_fin',
            'duree_jours', 'statut', 'statut_display', 'date_demande',
            'date_traitement', 'valide_par', 'motif', 'commentaire_rh',
            'document_attache', 'solde_avant', 'solde_apres'
        ]
        read_only_fields = ['reference', 'employe', 'date_demande', 'date_traitement', 'valide_par',
                          'solde_avant', 'solde_apres']


class CongeCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de demande de congé"""
    
    class Meta:
        model = Conge
        fields = [
            'type_conge', 'date_debut', 'date_fin', 'duree_jours', 'motif', 
            'document_attache'
        ]
        read_only_fields = ['employe', 'date_demande', 'date_traitement', 'valide_par',
                          'solde_avant', 'solde_apres']

    def validate(self, data):
        """Validation des données"""
        print(f'[DEBUG] CongeCreateSerializer validate - data: {data}')
        if data['date_fin'] <= data['date_debut']:
            raise serializers.ValidationError(
                "La date de fin doit être postérieure à la date de début."
            )
        
        if data['duree_jours'] <= 0:
            raise serializers.ValidationError("La durée doit être positive.")
        
        # Vérifier les conflits de dates
        employe = self.context['request'].user
        conflits = Conge.objects.filter(
            employe=employe,
            statut__in=['en_attente', 'approuve'],
            date_debut__lte=data['date_fin'],
            date_fin__gte=data['date_debut']
        )
        
        if conflits.exists():
            raise serializers.ValidationError(
                "Vous avez déjà une demande de congé sur cette période."
            )
        
        return data


class CongeValidationSerializer(serializers.ModelSerializer):
    """Serializer pour la validation des demandes de congé"""
    status = serializers.CharField(write_only=True)  # Accepter 'status' du frontend
    
    class Meta:
        model = Conge
        fields = ['status', 'statut', 'commentaire_rh', 'date_traitement', 'valide_par']
        read_only_fields = ['date_traitement', 'valide_par']
    
    def validate(self, data):
        """Validation de la validation"""
        # Utiliser 'status' si fourni, sinon 'statut'
        statut_value = data.get('status') or data.get('statut')
        
        if statut_value not in ['approuve', 'rejete']:
            raise serializers.ValidationError(
                "Le statut doit être 'approuve' ou 'rejete'."
            )
        
        if statut_value == 'rejete' and not data.get('commentaire_rh'):
            raise serializers.ValidationError(
                "Un commentaire est requis pour rejeter une demande."
            )
        
        # Mettre à jour data avec la valeur correcte
        data['statut'] = statut_value
        return data


# Permissions
class IsEmployeOrReadOnly(permissions.BasePermission):
    """Permission pour les employés"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        # L'employé ne peut voir que ses propres demandes
        if request.user.role == 'employe':
            return obj.employe == request.user
        # RH et Admin peuvent voir toutes les demandes
        return request.user.role in ['rh', 'admin']


class IsRHOrAdmin(permissions.BasePermission):
    """Permission pour RH et Admin"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['rh', 'admin']


# ViewSet
class CongeViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des congés"""
    queryset = Conge.objects.all()
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action == 'create':
            return CongeCreateSerializer
        elif self.action in ['approve', 'reject']:
            return CongeValidationSerializer
        return CongeSerializer
    
    def get_permissions(self):
        """Définir les permissions par action"""
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['approve', 'reject']:
            permission_classes = [IsRHOrAdmin]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsEmployeOrReadOnly]
        else:
            permission_classes = [IsRHOrAdmin]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Créer une demande de congé"""
        conge = serializer.save(employe=self.request.user)
        # Retourner le serializer complet avec tous les champs
        return CongeSerializer(conge).data
    
    def create(self, request, *args, **kwargs):
        """Surcharge de create pour retourner la réponse complète"""
        print(f'[DEBUG] CongeViewSet.create - data: {request.data}')
        print(f'[DEBUG] User: {request.user}, Role: {request.user.role}')
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f'[DEBUG] Serializer errors: {serializer.errors}')
            raise serializers.ValidationError(serializer.errors)
        conge_data = self.perform_create(serializer)
        return Response(conge_data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        """Filtrer selon l'utilisateur"""
        from .role_utils import is_admin_or_rh
        user = self.request.user
        if is_admin_or_rh(user):
            return Conge.objects.all()
        return Conge.objects.filter(employe=user)
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Approuver une demande de congé"""
        print(f'[DEBUG] approve action called for pk={pk}')
        conge = self.get_object()
        print(f'[DEBUG] conge found: {conge}, statut: {conge.statut}')
        
        if conge.statut != 'en_attente':
            return Response(
                {"error": "Cette demande n'est plus en attente."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(conge, data=request.data, partial=True)
        print(f'[DEBUG] serializer data: {request.data}')
        if serializer.is_valid():
            print(f'[DEBUG] serializer is valid, saving...')
            serializer.save(
                date_traitement=timezone.now(),
                valide_par=request.user
            )
            return Response({
                "message": "Demande de congé approuvée avec succès",
                "conge": CongeSerializer(conge).data
            })
        print(f'[DEBUG] serializer errors: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """Rejeter une demande de congé"""
        print(f'[DEBUG] reject action called for pk={pk}')
        conge = self.get_object()
        print(f'[DEBUG] conge found: {conge}, statut: {conge.statut}')
        
        if conge.statut != 'en_attente':
            return Response(
                {"error": "Cette demande n'est plus en attente."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(conge, data=request.data, partial=True)
        print(f'[DEBUG] serializer data: {request.data}')
        if serializer.is_valid():
            print(f'[DEBUG] serializer is valid, saving...')
            serializer.save(
                date_traitement=timezone.now(),
                valide_par=request.user
            )
            return Response({
                "message": "Demande de congé rejetée",
                "conge": CongeSerializer(conge).data
            })
        print(f'[DEBUG] serializer errors: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Annuler sa propre demande de congé"""
        conge = self.get_object()
        
        # Seul l'employé concerné peut annuler sa demande
        if conge.employe != request.user:
            return Response(
                {"error": "Vous ne pouvez annuler que vos propres demandes."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if conge.statut not in ['en_attente']:
            return Response(
                {"error": "Vous ne pouvez annuler qu'une demande en attente."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conge.statut = 'annule'
        conge.date_traitement = timezone.now()
        conge.save()
        
        return Response({
            "message": "Demande de congé annulée",
            "conge": CongeSerializer(conge).data
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Lister les demandes en attente"""
        if request.user.role not in ['rh', 'admin']:
            return Response(
                {"error": "Accès non autorisé."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_conges = Conge.objects.filter(statut='en_attente')
        serializer = self.get_serializer(pending_conges, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mes_conges(self, request):
        """Lister les congés de l'utilisateur connecté"""
        conges = Conge.objects.filter(employe=request.user)
        serializer = self.get_serializer(conges, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def solde(self, request):
        """Afficher le solde de congés de l'utilisateur"""
        # Calculer le solde (logique à implémenter selon les règles de l'entreprise)
        solde_annuel = 25.0  # Base : 25 jours par an
        conges_pris = Conge.objects.filter(
            employe=request.user,
            statut='approuve'
        ).aggregate(total=models.Sum('duree_jours'))['total'] or 0
        
        solde_restant = solde_annuel - conges_pris
        
        return Response({
            "solde_annuel": solde_annuel,
            "conges_pris": conges_pris,
            "solde_restant": solde_restant,
            "employe": request.user.username
        })
