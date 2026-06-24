"""
Module de gestion des rapports
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

User = get_user_model()


class Rapport(models.Model):
    """Modèle pour les rapports d'activité et de présence"""
    
    TYPE_RAPPORT_CHOICES = [
        ('presence', 'Rapport de Présence'),
        ('activite', 'Rapport d\'Activité'),
        ('performance', 'Rapport de Performance'),
        ('conges', 'Rapport de Congés'),
        ('bulletins', 'Rapport de Bulletins'),
        ('violations', 'Rapport de Violations'),
        ('statistiques', 'Rapport Statistiques'),
    ]
    
    STATUT_RAPPORT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('en_cours', 'En Cours'),
        ('termine', 'Terminé'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]
    
    PERIODE_RAPPORT_CHOICES = [
        ('jour', 'Journalier'),
        ('semaine', 'Hebdomadaire'),
        ('mois', 'Mensuel'),
        ('trimestre', 'Trimestriel'),
        ('semestre', 'Semestriel'),
        ('annee', 'Annuel'),
        ('personnalise', 'Personnalisé'),
    ]
    
    # Informations générales
    titre = models.CharField(max_length=200)
    type_rapport = models.CharField(max_length=20, choices=TYPE_RAPPORT_CHOICES)
    periode_rapport = models.CharField(max_length=20, choices=PERIODE_RAPPORT_CHOICES)
    
    # Dates
    date_debut = models.DateField()
    date_fin = models.DateField()
    date_generation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # Contenu et métadonnées
    description = models.TextField(blank=True)
    contenu = models.TextField(help_text="Contenu détaillé du rapport")
    fichier_attache = models.FileField(upload_to='rapports/', null=True, blank=True)
    
    # Auteur et validation
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rapports_crees')
    valide_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='rapports_valides')
    statut = models.CharField(max_length=20, choices=STATUT_RAPPORT_CHOICES, default='brouillon')
    
    # Paramètres et filtres
    filtres = models.JSONField(default=dict, blank=True, help_text="Filtres appliqués au rapport")
    parametres = models.JSONField(default=dict, blank=True, help_text="Paramètres de génération")
    
    # Statistiques et résultats
    total_enregistrements = models.IntegerField(default=0, help_text="Nombre total d'enregistrements")
    total_heures = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, 
                                     help_text="Total des heures")
    pourcentage_presence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                         help_text="Pourcentage de présence")
    
    # Destinataires
    destinataires = models.ManyToManyField(User, blank=True, related_name='rapports_recus',
                                      help_text="Utilisateurs ayant accès au rapport")
    
    class Meta:
        verbose_name = "Rapport"
        verbose_name_plural = "Rapports"
        ordering = ['-date_generation']
        indexes = [
            models.Index(fields=['type_rapport', 'date_debut']),
            models.Index(fields=['auteur', 'statut']),
            models.Index(fields=['date_generation']),
        ]
    
    def __str__(self):
        return f"{self.titre} - {self.get_type_rapport_display()}"
    
    @property
    def auteur_name(self):
        """Nom complet de l'auteur"""
        return f"{self.auteur.first_name} {self.auteur.last_name}"
    
    @property
    def auteur_username(self):
        """Username de l'auteur"""
        return self.auteur.username
    
    @property
    def type_rapport_display(self):
        """Affichage du type de rapport"""
        return dict(self.TYPE_RAPPORT_CHOICES).get(self.type_rapport, self.type_rapport)
    
    @property
    def statut_display(self):
        """Affichage du statut"""
        return dict(self.STATUT_RAPPORT_CHOICES).get(self.statut, self.statut)
    
    @property
    def periode_display(self):
        """Affichage de la période"""
        return dict(self.PERIODE_RAPPORT_CHOICES).get(self.periode_rapport, self.periode_rapport)
    
    @property
    def duree_jours(self):
        """Durée en jours"""
        return (self.date_fin - self.date_debut).days + 1
    
    def clean(self):
        """Validation du modèle"""
        if self.date_fin < self.date_debut:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")
        
        if self.pourcentage_presence and (self.pourcentage_presence < 0 or self.pourcentage_presence > 100):
            raise ValidationError("Le pourcentage de présence doit être entre 0 et 100.")
    
    def generer_rapport_presence(self, employe_ids=None, service_ids=None):
        """Générer un rapport de présence"""
        from core.permissions import PermissionRequest
        from core.conges import Conge
        
        # Logique de génération du rapport de présence
        queryset = PermissionRequest.objects.filter(
            date_sortie__gte=self.date_debut,
            date_retour__lte=self.date_fin
        )
        
        if employe_ids:
            queryset = queryset.filter(employee_id__in=employe_ids)
        
        if service_ids:
            queryset = queryset.filter(employee__service_id__in=service_ids)
        
        # Calculer les statistiques
        total_requests = queryset.count()
        approved_requests = queryset.filter(status='approved').count()
        
        self.contenu = f"""
        Rapport de Présence du {self.date_debut} au {self.date_fin}
        
        Statistiques:
        - Total des demandes: {total_requests}
        - Demandes approuvées: {approved_requests}
        - Taux d'approbation: {(approved_requests/total_requests*100):.1f}%
        
        Détail par employé:
        """
        
        # Ajouter les détails par employé
        for permission in queryset.select_related('employee'):
            self.contenu += f"""
        - {permission.employee.first_name} {permission.employee.last_name}: {permission.status}
          Période: {permission.date_sortie} au {permission.date_retour}
          Motif: {permission.motif}
        """
        
        self.total_enregistrements = total_requests
        self.save()
    
    def generer_rapport_conges(self, employe_ids=None):
        """Générer un rapport de congés"""
        from core.conges import Conge
        
        queryset = Conge.objects.filter(
            date_debut__gte=self.date_debut,
            date_fin__lte=self.date_fin
        )
        
        if employe_ids:
            queryset = queryset.filter(employe_id__in=employe_ids)
        
        total_conges = queryset.count()
        total_jours = queryset.aggregate(total=models.Sum('duree_jours'))['total'] or 0
        
        self.contenu = f"""
        Rapport des Congés du {self.date_debut} au {self.date_fin}
        
        Statistiques:
        - Total des congés: {total_conges}
        - Total jours pris: {total_jours}
        - Moyenne jours par congé: {(total_jours/total_conges):.1f} si total_conges > 0 else 0
        
        Détail par employé:
        """
        
        for conge in queryset.select_related('employe'):
            self.contenu += f"""
        - {conge.employe.first_name} {conge.employe.last_name}: {conge.get_type_conge_display()}
          Période: {conge.date_debut} au {conge.date_fin}
          Durée: {conge.duree_jours} jours
          Statut: {conge.get_statut_display()}
        """
        
        self.total_enregistrements = total_conges
        self.total_heures = Decimal(str(total_jours * 8))  # 8h par jour
        self.save()
    
    def generer_rapport_bulletins(self, employe_ids=None):
        """Générer un rapport des bulletins"""
        from core.bulletin import Bulletin
        
        queryset = Bulletin.objects.filter(
            periode_debut__gte=self.date_debut,
            periode_fin__lte=self.date_fin
        )
        
        if employe_ids:
            queryset = queryset.filter(employee_id__in=employe_ids)
        
        total_bulletins = queryset.count()
        total_salaire_net = queryset.aggregate(total=models.Sum('salaire_net'))['total'] or 0
        
        self.contenu = f"""
        Rapport des Bulletins du {self.date_debut} au {self.date_fin}
        
        Statistiques:
        - Total bulletins: {total_bulletins}
        - Total salaire net: {total_salaire_net:,.2f} €
        - Moyenne salaire net: {(total_salaire_net/total_bulletins):,.2f} € si total_bulletins > 0 else 0
        
        Détail par employé:
        """
        
        for bulletin in queryset.select_related('employee'):
            self.contenu += f"""
        - {bulletin.employee.first_name} {bulletin.employee.last_name}
          Période: {bulletin.periode_debut} au {bulletin.periode_fin}
          Salaire net: {bulletin.salaire_net} €
          Heures sup: {bulletin.heures_supplementaires}
        """
        
        self.total_enregistrements = total_bulletins
        self.save()


# Serializers
class RapportSerializer(serializers.ModelSerializer):
    """Serializer pour les rapports - ID masqué pour le frontend"""
    auteur_name = serializers.CharField(read_only=True)
    auteur_username = serializers.CharField(read_only=True)
    type_rapport_display = serializers.CharField(read_only=True)
    statut_display = serializers.CharField(read_only=True)
    periode_display = serializers.CharField(read_only=True)
    duree_jours = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Rapport
        fields = [
            'titre', 'type_rapport', 'type_rapport_display',
            'periode_rapport', 'periode_display', 'date_debut', 'date_fin',
            'duree_jours', 'description', 'contenu', 'fichier_attache',
            'auteur', 'auteur_name', 'auteur_username',
            'valide_par', 'statut', 'statut_display',
            'date_generation', 'date_modification', 'filtres', 'parametres',
            'total_enregistrements', 'total_heures', 'pourcentage_presence',
            'destinataires'
        ]
        read_only_fields = ['auteur', 'date_generation', 'date_modification', 'valide_par']


class RapportCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de rapports"""
    
    class Meta:
        model = Rapport
        fields = [
            'titre', 'type_rapport', 'periode_rapport',
            'date_debut', 'date_fin', 'description',
            'filtres', 'parametres', 'destinataires'
        ]
    
    def validate(self, data):
        """Validation des données"""
        if data['date_fin'] < data['date_debut']:
            raise serializers.ValidationError(
                "La date de fin doit être postérieure à la date de début."
            )
        
        # Valider la cohérence période/type
        periode = data.get('periode_rapport')
        date_debut = data['date_debut']
        date_fin = data['date_fin']
        
        if periode == 'mois':
            # Vérifier que c'est bien un mois complet
            if date_debut.day != 1 or date_fin.day != 1:
                raise serializers.ValidationError(
                    "Pour un rapport mensuel, utilisez le premier jour du mois."
                )
        
        return data


class RapportGenerationSerializer(serializers.Serializer):
    """Serializer pour la génération automatique de rapports"""
    employe_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Liste des IDs des employés"
    )
    service_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Liste des IDs des services"
    )
    inclure_details = serializers.BooleanField(default=True)
    format_export = serializers.ChoiceField(
        choices=['json', 'csv', 'pdf'],
        default='json'
    )


# Permissions
class IsAdminOrRH(permissions.BasePermission):
    """Permission pour Admin et RH"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'rh']
    
    def has_object_permission(self, request, view, obj):
        return request.user.role in ['admin', 'rh']


class IsAuteurOrReadOnly(permissions.BasePermission):
    """Permission pour l'auteur ou lecture seule"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        # L'auteur peut tout modifier
        if obj.auteur == request.user:
            return True
        
        # Admin et RH peuvent tout voir
        if request.user.role in ['admin', 'rh']:
            return True
        
        # Autres ne peuvent que voir
        return request.method in permissions.SAFE_METHODS


# ViewSet
class RapportViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des rapports"""
    queryset = Rapport.objects.all()
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action == 'create':
            return RapportCreateSerializer
        elif self.action in ['generer_auto', 'valider']:
            return RapportGenerationSerializer
        return RapportSerializer
    
    def get_permissions(self):
        """Définir les permissions par action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrRH]
        elif self.action in ['validate']:
            permission_classes = [IsAdminOrRH]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAuteurOrReadOnly]
        else:
            permission_classes = [IsAdminOrRH]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrer selon l'utilisateur"""
        user = self.request.user
        if user.role == 'employe':
            return Rapport.objects.filter(destinataires=user)
        elif user.role in ['rh', 'admin']:
            return Rapport.objects.all()
        return Rapport.objects.none()
    
    def perform_create(self, serializer):
        """Créer un rapport"""
        rapport = serializer.save(auteur=self.request.user)
        
        # Ajouter l'auteur comme destinataire par défaut
        rapport.destinataires.add(self.request.user)
        
        # Retourner le serializer complet avec tous les champs
        return RapportSerializer(rapport).data
    
    def create(self, request, *args, **kwargs):
        """Surcharge de create pour retourner la réponse complète"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rapport_data = self.perform_create(serializer)
        return Response(rapport_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def generer_auto(self, request, pk=None):
        """Générer automatiquement le contenu du rapport"""
        rapport = self.get_object()
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                if rapport.type_rapport == 'presence':
                    rapport.generer_rapport_presence(
                        employe_ids=data.get('employe_ids'),
                        service_ids=data.get('service_ids')
                    )
                elif rapport.type_rapport == 'conges':
                    rapport.generer_rapport_conges(
                        employe_ids=data.get('employe_ids')
                    )
                elif rapport.type_rapport == 'bulletins':
                    rapport.generer_rapport_bulletins(
                        employe_ids=data.get('employe_ids')
                    )
                
                rapport.statut = 'termine'
                rapport.save()
                
                return Response({
                    "message": "Rapport généré avec succès",
                    "rapport": RapportSerializer(rapport).data
                })
            except Exception as e:
                return Response(
                    {"error": f"Erreur lors de la génération: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """Valider un rapport"""
        rapport = self.get_object()
        
        if rapport.statut != 'termine':
            return Response(
                {"error": "Seuls les rapports terminés peuvent être validés."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rapport.statut = 'valide'
        rapport.valide_par = request.user
        rapport.date_modification = timezone.now()
        rapport.save()
        
        return Response({
            "message": "Rapport validé avec succès",
            "rapport": RapportSerializer(rapport).data
        })
    
    @action(detail=False, methods=['get'])
    def mes_rapports(self, request):
        """Lister les rapports de l'utilisateur connecté"""
        rapports = Rapport.objects.filter(destinataires=request.user)
        serializer = self.get_serializer(rapports, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Statistiques des rapports (Admin/RH uniquement)"""
        if request.user.role not in ['admin', 'rh']:
            return Response(
                {"error": "Accès non autorisé."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_rapports': Rapport.objects.count(),
            'par_type': list(Rapport.objects.values('type_rapport')
                              .annotate(count=models.Count('id'))
                              .values('type_rapport', 'count')),
            'par_statut': list(Rapport.objects.values('statut')
                              .annotate(count=models.Count('id'))
                              .values('statut', 'count')),
            'par_auteur': list(Rapport.objects.values('auteur__username')
                              .annotate(count=models.Count('id'))
                              .values('auteur__username', 'count')),
            'recent': list(Rapport.objects.all()[:10]
                              .values('id', 'titre', 'type_rapport', 'date_generation', 'statut')),
        }
        
        # Ajouter les noms d'affichage
        for item in stats['par_type']:
            item['type_rapport_display'] = dict(Rapport.TYPE_RAPPORT_CHOICES).get(
                item['type_rapport'], item['type_rapport']
            )
        
        for item in stats['par_statut']:
            item['statut_display'] = dict(Rapport.STATUT_RAPPORT_CHOICES).get(
                item['statut'], item['statut']
            )
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def dupliquer(self, request, pk=None):
        """Dupliquer un rapport"""
        original = self.get_object()
        
        # Créer une copie
        nouveau_rapport = Rapport.objects.create(
            titre=f"Copie de {original.titre}",
            type_rapport=original.type_rapport,
            periode_rapport=original.periode_rapport,
            date_debut=original.date_debut,
            date_fin=original.date_fin,
            description=original.description,
            contenu=original.contenu,
            filtres=original.filtres,
            parametres=original.parametres,
            auteur=request.user,
            statut='brouillon'
        )
        
        # Copier les destinataires
        nouveau_rapport.destinataires.set(original.destinataires.all())
        
        serializer = RapportSerializer(nouveau_rapport)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
