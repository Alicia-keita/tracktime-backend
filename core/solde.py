"""
Module de gestion des soldes de congés
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class Solde(models.Model):
    """Modèle pour les soldes de congés des employés"""
    
    # Informations employé
    employe = models.OneToOneField(User, on_delete=models.CASCADE, related_name='solde_conges')
    
    # Soldes de congés
    solde_annuel = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        default=25.0,
        help_text="Solde annuel de congés en jours"
    )
    
    conges_pris = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        default=0.0,
        help_text="Nombre de jours de congés pris"
    )
    
    conges_restant = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        default=25.0,
        help_text="Solde de congés restant"
    )
    
    # Période de référence
    annee_reference = models.IntegerField(
        default=2026,
        help_text="Année de référence des soldes"
    )
    
    # Métadonnées
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    mis_a_jour_par = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='soldes_mis_a_jour'
    )
    
    class Meta:
        verbose_name = "Solde de Congés"
        verbose_name_plural = "Soldes de Congés"
        ordering = ['-annee_reference', 'employe__username']
        unique_together = ['employe', 'annee_reference']
    
    def __str__(self):
        return f"Solde {self.employe.get_full_name()} - {self.annee_reference}: {self.conges_restant} jours"
    
    @property
    def nom_complet(self):
        """Nom complet de l'employé"""
        return f"{self.employe.first_name} {self.employe.last_name}"
    
    @property
    def username(self):
        """Username de l'employé"""
        return self.employe.username
    
    @property
    def service(self):
        """Service de l'employé"""
        return self.employe.service
    
    def clean(self):
        """Validation du modèle"""
        if self.conges_pris < 0:
            raise ValidationError("Le nombre de congés pris ne peut pas être négatif.")
        
        if self.conges_restant < 0:
            raise ValidationError("Le solde restant ne peut pas être négatif.")
        
        if self.solde_annuel < 0:
            raise ValidationError("Le solde annuel ne peut pas être négatif.")
    
    def save(self, *args, **kwargs):
        """Surcharge de la sauvegarde pour calculer automatiquement le solde restant"""
        self.conges_restant = self.solde_annuel - self.conges_pris
        super().save(*args, **kwargs)
    
    def ajouter_conges_pris(self, jours):
        """Ajouter des jours de congés pris"""
        self.conges_pris += jours
        self.save()
    
    def reinitialiser_solde_annuel(self, nouveau_solde):
        """Réinitialiser le solde annuel"""
        self.solde_annuel = nouveau_solde
        self.save()


# Serializers
class SoldeSerializer(serializers.ModelSerializer):
    """Serializer pour les soldes de congés - ID masqué pour le frontend"""
    nom_complet = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    service = serializers.CharField(read_only=True)
    
    class Meta:
        model = Solde
        fields = [
            'employe', 'nom_complet', 'username', 'service',
            'solde_annuel', 'conges_pris', 'conges_restant',
            'annee_reference', 'date_mise_a_jour', 'mis_a_jour_par'
        ]
        read_only_fields = ['date_mise_a_jour', 'mis_a_jour_par']


class SoldeCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de solde"""
    
    class Meta:
        model = Solde
        fields = [
            'employe', 'solde_annuel', 'conges_pris', 'annee_reference'
        ]
    
    def validate(self, data):
        """Validation des données"""
        employe = data['employe']
        annee = data['annee_reference']
        
        # Vérifier qu'il n'existe pas déjà un solde pour cet employé et cette année
        if Solde.objects.filter(employe=employe, annee_reference=annee).exists():
            raise serializers.ValidationError(
                f"Un solde existe déjà pour {employe.get_full_name()} en {annee}."
            )
        
        # Valider les valeurs numériques
        if data['solde_annuel'] <= 0:
            raise serializers.ValidationError("Le solde annuel doit être positif.")
        
        if data['conges_pris'] < 0:
            raise serializers.ValidationError("Les congés pris ne peuvent pas être négatifs.")
        
        return data


class SoldeUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour de solde"""
    
    class Meta:
        model = Solde
        fields = [
            'solde_annuel', 'conges_pris', 'annee_reference'
        ]
    
    def validate(self, data):
        """Validation des données de mise à jour"""
        if 'solde_annuel' in data and data['solde_annuel'] <= 0:
            raise serializers.ValidationError("Le solde annuel doit être positif.")
        
        if 'conges_pris' in data and data['conges_pris'] < 0:
            raise serializers.ValidationError("Les congés pris ne peuvent pas être négatifs.")
        
        return data


# Permissions
class IsAdminOrRH(permissions.BasePermission):
    """Permission pour Admin et RH uniquement"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'rh']
    
    def has_object_permission(self, request, view, obj):
        return request.user.role in ['admin', 'rh']


class IsEmployeReadOnly(permissions.BasePermission):
    """Permission pour les employés (lecture seule)"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admin et RH peuvent tout faire
        if request.user.role in ['admin', 'rh']:
            return True
        
        # Employés peuvent seulement lire leur propre solde
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin et RH peuvent tout voir
        if request.user.role in ['admin', 'rh']:
            return True
        
        # Employés peuvent voir seulement leur solde
        return obj.employe == request.user


# ViewSet
class SoldeViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des soldes de congés"""
    queryset = Solde.objects.all()
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action == 'create':
            return SoldeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SoldeUpdateSerializer
        return SoldeSerializer
    
    def get_permissions(self):
        """Définir les permissions par action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrRH]
        elif self.action in ['list', 'retrieve', 'mon_solde']:
            permission_classes = [IsEmployeReadOnly]
        else:
            permission_classes = [IsAdminOrRH]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrer selon l'utilisateur"""
        from .role_utils import is_admin_or_rh
        user = self.request.user
        if is_admin_or_rh(user):
            return Solde.objects.all()
        return Solde.objects.filter(employe=user)
    
    def perform_create(self, serializer):
        """Créer un solde"""
        solde = serializer.save(mis_a_jour_par=self.request.user)
        # Retourner le serializer complet avec tous les champs
        return SoldeSerializer(solde).data
    
    def create(self, request, *args, **kwargs):
        """Surcharge de create pour retourner la réponse complète"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solde_data = self.perform_create(serializer)
        return Response(solde_data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        """Mettre à jour un solde"""
        solde = serializer.save(mis_a_jour_par=self.request.user)
        # Retourner le serializer complet avec tous les champs
        return SoldeSerializer(solde).data
    
    def update(self, request, *args, **kwargs):
        """Surcharge de update pour retourner la réponse complète"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        solde_data = self.perform_update(serializer)
        return Response(solde_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def mon_solde(self, request):
        """Afficher le solde de l'utilisateur connecté"""
        try:
            solde = Solde.objects.get(employe=request.user, annee_reference=2026)
            serializer = self.get_serializer(solde)
            return Response(serializer.data)
        except Solde.DoesNotExist:
            # Créer un solde par défaut si inexistant
            solde = Solde.objects.create(
                employe=request.user,
                annee_reference=2026,
                solde_annuel=25.0,
                conges_pris=0.0,
                mis_a_jour_par=request.user
            )
            serializer = self.get_serializer(solde)
            return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reinitialiser(self, request, pk=None):
        """Réinitialiser le solde annuel (Admin/RH uniquement)"""
        solde = self.get_object()
        
        nouveau_solde = request.data.get('solde_annuel')
        if not nouveau_solde:
            return Response(
                {"error": "Le nouveau solde annuel est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            solde.reinitialiser_solde_annuel(float(nouveau_solde))
            return Response({
                "message": f"Solde réinitialisé à {nouveau_solde} jours",
                "solde": SoldeSerializer(solde).data
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def ajouter_conges(self, request, pk=None):
        """Ajouter des jours de congés pris (Admin/RH uniquement)"""
        solde = self.get_object()
        
        jours = request.data.get('jours')
        if not jours:
            return Response(
                {"error": "Le nombre de jours est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            jours = float(jours)
            solde.ajouter_conges_pris(jours)
            return Response({
                "message": f"{jours} jour(s) ajouté(s) aux congés pris",
                "solde": SoldeSerializer(solde).data
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Statistiques globales des soldes (Admin/RH uniquement)"""
        if request.user.role not in ['admin', 'rh']:
            return Response(
                {"error": "Accès non autorisé."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        total_employes = Solde.objects.count()
        total_conges_pris = Solde.objects.aggregate(
            total=models.Sum('conges_pris')
        )['total'] or 0
        
        total_conges_restants = Solde.objects.aggregate(
            total=models.Sum('conges_restant')
        )['total'] or 0
        
        # Par service
        stats_par_service = Solde.objects.values('employe__service').annotate(
            nb_employes=models.Count('id'),
            total_pris=models.Sum('conges_pris'),
            total_restant=models.Sum('conges_restant')
        )
        
        return Response({
            "total_employes": total_employes,
            "total_conges_pris": total_conges_pris,
            "total_conges_restants": total_conges_restants,
            "moyenne_conges_par_employe": total_conges_pris / total_employes if total_employes > 0 else 0,
            "stats_par_service": list(stats_par_service)
        })
