"""
Module de gestion du pointage (présence et heures de travail)
Horaires: 8h à 17h
- Arrivée après 8h30 = Retard
- Pause déjeuner obligatoire : 13h00 - 13h30 (30 min)
- Pas de pointage entre 08h00 et 17h00 = Absence
- Samedi et Dimanche : pointage INACTIF (week-end)
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, time, timedelta

from .permissions import PermissionRequest

User = get_user_model()


def is_weekend(date):
    """Retourne True si la date est un samedi (5) ou dimanche (6)."""
    return date.weekday() >= 5


def employee_has_sortie_permission(employee, moment):
    """Permission de sortie approuvée couvrant l'heure de départ."""
    return PermissionRequest.objects.filter(
        employee=employee,
        status='approuve',
        type_permission='permission',
        date_sortie__lte=moment,
        date_retour__gte=moment,
    ).exists()


class Pointage(models.Model):
    """Modèle de pointage des employés"""
    
    STATUT_CHOICES = [
        ('present', 'Présent'),
        ('retard', 'Retard'),
        ('absent', 'Absent'),
        ('permission', 'Permission'),
        ('conge', 'Congé'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pointages')
    date = models.DateField(verbose_name="Date", default=timezone.now)
    
    # Heures de pointage
    heure_arrivee = models.TimeField(verbose_name="Heure d'arrivée", null=True, blank=True)
    heure_depart = models.TimeField(verbose_name="Heure de départ", null=True, blank=True)
    
    # Pause déjeuner
    debut_pause = models.TimeField(verbose_name="Début pause", null=True, blank=True)
    fin_pause = models.TimeField(verbose_name="Fin pause", null=True, blank=True)
    
    # Horaires de référence (8h-17h)
    HEURE_DEBUT = time(8, 0)   # 8h00
    HEURE_FIN = time(17, 0)    # 17h00
    SEUIL_RETARD = time(8, 30) # À partir de 8h30 = retard
    
    # Horaires de pause déjeuner (13h-13h30)
    HEURE_PAUSE_DEBUT = time(13, 0)  # 13h00
    HEURE_PAUSE_FIN = time(13, 30)   # 13h30
    DUREE_PAUSE_MINUTES = 30  # 30 minutes de pause obligatoire
    
    # Statut et calculs
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='absent', verbose_name="Statut")
    minutes_retard = models.IntegerField(default=0, verbose_name="Minutes de retard")
    heures_travaillees = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Heures travaillées")
    
    # Validation pause
    pause_respectee = models.BooleanField(default=False, null=True, blank=True, verbose_name="Pause respectée")
    minutes_retard_pause = models.IntegerField(default=0, verbose_name="Minutes de retard sur pause")
    
    # Commentaires
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Pointage"
        verbose_name_plural = "Pointages"
        ordering = ['-date', '-heure_arrivee']
        unique_together = ['employee', 'date']
    
    def __str__(self):
        return f"{self.employee} - {self.date} - {self.statut}"
    
    def calculer_statut(self):
        """Calcule le statut en fonction de l'heure d'arrivée.
        - Arrivée avant 08h30 → Présent
        - Arrivée à partir de 08h30 → Retard
        - Pas de pointage entre 08h00 et 17h00 → Absent
        La pause est vérifiée uniquement à la fin de journée."""
        if not self.heure_arrivee:
            return 'absent'
        
        # Vérifier si l'arrivée est après le seuil de retard (8h30)
        arrivee = datetime.combine(self.date, self.heure_arrivee)
        seuil_retard = datetime.combine(self.date, self.SEUIL_RETARD)
        
        # Calculer le retard d'arrivée (à partir de 08h30)
        total_retard = 0
        if arrivee > seuil_retard:
            retard = arrivee - seuil_retard
            total_retard += int(retard.total_seconds() / 60)
        
        # Vérifier la pause SEULEMENT si la journée est terminée (heure_depart enregistrée)
        # pour ne pas pénaliser l'employé au moment du pointage d'arrivée
        if self.heure_depart:
            self.verifier_pause()
            total_retard += self.minutes_retard_pause
        else:
            # Journée en cours : pas de pénalité pour la pause
            self.pause_respectee = None  # Pas encore déterminé
            self.minutes_retard_pause = 0
        
        self.minutes_retard = total_retard
        
        if total_retard > 0:
            return 'retard'
        else:
            return 'present'
    
    def verifier_pause(self):
        """Vérifie si la pause déjeuner est respectée (13h00-13h30, 30 min obligatoires)"""
        pause_debut_ref = datetime.combine(self.date, self.HEURE_PAUSE_DEBUT)
        pause_fin_ref = datetime.combine(self.date, self.HEURE_PAUSE_FIN)
        
        retard_pause = 0
        
        if self.debut_pause and self.fin_pause:
            pause_debut = datetime.combine(self.date, self.debut_pause)
            pause_fin = datetime.combine(self.date, self.fin_pause)
            
            # Vérifier si début de pause est après 13h00
            if pause_debut > pause_debut_ref:
                diff = pause_debut - pause_debut_ref
                retard_pause += int(diff.total_seconds() / 60)
            
            # Vérifier si fin de pause est après 13h30
            if pause_fin > pause_fin_ref:
                diff = pause_fin - pause_fin_ref
                retard_pause += int(diff.total_seconds() / 60)
            
            # Vérifier si durée de pause est < 30 minutes
            duree_pause = pause_fin - pause_debut
            duree_minutes = int(duree_pause.total_seconds() / 60)
            if duree_minutes < self.DUREE_PAUSE_MINUTES:
                # Pénalité : le temps non pris en pause est compté comme retard
                penalite = self.DUREE_PAUSE_MINUTES - duree_minutes
                retard_pause += penalite
            
            self.pause_respectee = (retard_pause == 0)
        else:
            # Pas de pause enregistrée = pause non respectée
            self.pause_respectee = False
            # Pénalité : 30 minutes de retard si pas de pause
            retard_pause = self.DUREE_PAUSE_MINUTES
        
        self.minutes_retard_pause = retard_pause
        return retard_pause
    
    def calculer_heures_travaillees(self):
        """Calcule les heures travaillées"""
        if not self.heure_arrivee or not self.heure_depart:
            return 0
        
        # Heures travaillées (départ - arrivée)
        arrivee = datetime.combine(self.date, self.heure_arrivee)
        depart = datetime.combine(self.date, self.heure_depart)
        duree = depart - arrivee
        
        # Soustraire la pause si définie
        if self.debut_pause and self.fin_pause:
            debut_pause = datetime.combine(self.date, self.debut_pause)
            fin_pause = datetime.combine(self.date, self.fin_pause)
            duree_pause = fin_pause - debut_pause
            duree = duree - duree_pause
        
        # Convertir en heures décimales
        heures = duree.total_seconds() / 3600
        return round(heures, 2)
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec calcul automatique"""
        if self.heure_arrivee:
            self.statut = self.calculer_statut()
            self.heures_travaillees = self.calculer_heures_travaillees()
        else:
            self.statut = 'absent'
        super().save(*args, **kwargs)


# Serializers
class PointageSerializer(serializers.ModelSerializer):
    """Serializer pour les pointages"""
    employee_name = serializers.SerializerMethodField()
    employee_telephone = serializers.SerializerMethodField()
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    retard_heures = serializers.SerializerMethodField()
    retard_pause_heures = serializers.SerializerMethodField()
    reference = serializers.CharField(source='id', read_only=True)
    
    class Meta:
        model = Pointage
        fields = [
            'reference', 'employee', 'employee_name', 'employee_telephone', 'date',
            'heure_arrivee', 'heure_depart', 'debut_pause', 'fin_pause',
            'statut', 'statut_display', 'minutes_retard', 'retard_heures',
            'pause_respectee', 'minutes_retard_pause', 'retard_pause_heures',
            'heures_travaillees', 'commentaire'
        ]
        read_only_fields = ['reference', 'statut', 'minutes_retard', 'heures_travaillees', 
                           'pause_respectee', 'minutes_retard_pause']
    
    def get_employee_name(self, obj):
        """Retourne le nom complet ou le username de l'employé"""
        full_name = obj.employee.get_full_name()
        return full_name if full_name else obj.employee.username

    def get_employee_telephone(self, obj):
        """Retourne le numéro de téléphone de l'employé"""
        return getattr(obj.employee, 'telephone', None) or '-'

    def get_retard_heures(self, obj):
        """Retourne le retard au format HH:MM"""
        if obj.minutes_retard > 0:
            heures = obj.minutes_retard // 60
            minutes = obj.minutes_retard % 60
            return f"{heures}h {minutes:02d}min"
        return None
    
    def get_retard_pause_heures(self, obj):
        """Retourne le retard sur pause au format HH:MM"""
        if obj.minutes_retard_pause > 0:
            heures = obj.minutes_retard_pause // 60
            minutes = obj.minutes_retard_pause % 60
            return f"{heures}h {minutes:02d}min"
        return None


class PointageCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de pointage"""
    
    class Meta:
        model = Pointage
        fields = ['heure_arrivee', 'heure_depart', 'debut_pause', 'fin_pause', 'commentaire']
    
    def validate(self, data):
        """Validation des données"""
        from datetime import time
        
        heure_arrivee = data.get('heure_arrivee')
        heure_depart = data.get('heure_depart')
        debut_pause = data.get('debut_pause')
        fin_pause = data.get('fin_pause')
        
        # Vérifier que départ > arrivée
        if heure_arrivee and heure_depart:
            if heure_depart <= heure_arrivee:
                raise serializers.ValidationError(
                    "L'heure de départ doit être postérieure à l'heure d'arrivée."
                )
        
        # Vérifier la pause (doit être autour de 13h00-13h30)
        HEURE_PAUSE_DEBUT = time(13, 0)
        HEURE_PAUSE_FIN = time(13, 30)
        
        if debut_pause and fin_pause:
            if fin_pause <= debut_pause:
                raise serializers.ValidationError(
                    "La fin de pause doit être postérieure au début de pause."
                )
            if heure_arrivee and debut_pause < heure_arrivee:
                raise serializers.ValidationError(
                    "La pause ne peut commencer avant l'arrivée."
                )
            if heure_depart and fin_pause > heure_depart:
                raise serializers.ValidationError(
                    "La pause ne peut finir après le départ."
                )
            
            # Vérifier les horaires de pause (13h00-13h30)
            if debut_pause < HEURE_PAUSE_DEBUT:
                raise serializers.ValidationError(
                    "La pause ne peut pas commencer avant 13h00."
                )
            if fin_pause > HEURE_PAUSE_FIN:
                raise serializers.ValidationError(
                    "La pause ne peut pas finir après 13h30."
                )
        
        return data


# Permissions
class IsOwnPointage(permissions.BasePermission):
    """Permission pour voir/modifier ses propres pointages"""
    
    def has_object_permission(self, request, view, obj):
        return obj.employee == request.user


class IsRHOrAdmin(permissions.BasePermission):
    """Permission pour RH et Admin"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['rh', 'admin']


# ViewSet
class PointageViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des pointages"""
    queryset = Pointage.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PointageCreateSerializer
        return PointageSerializer
    
    def get_permissions(self):
        # Actions autorisées pour tous les utilisateurs authentifiés (employés, RH, admin)
        if self.action in ['create', 'check_in', 'check_out', 'today', 'my_stats', 'list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        # Actions réservées aux RH et Admin (update, destroy, etc.)
        else:
            permission_classes = [IsRHOrAdmin]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Créer un pointage avec l'employé courant"""
        # Vérifier si un pointage existe déjà pour cette date
        today = timezone.localtime(timezone.now()).date()
        existing = Pointage.objects.filter(
            employee=self.request.user,
            date=today
        ).first()
        
        if existing:
            # Mettre à jour le pointage existant
            for key, value in serializer.validated_data.items():
                setattr(existing, key, value)
            existing.save()
            return existing
        else:
            return serializer.save(employee=self.request.user, date=today)
    
    def get_queryset(self):
        """Filtrer selon l'utilisateur"""
        from .role_utils import is_admin_or_rh
        user = self.request.user
        if is_admin_or_rh(user):
            return Pointage.objects.all()
        return Pointage.objects.filter(employee=user)
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """Pointer l'arrivée (check-in) — inactif le week-end"""
        local_now = timezone.localtime(timezone.now())
        today = local_now.date()
        current_time = local_now.time()

        # ---- Règle Week-end : blocage samedi et dimanche ----
        if is_weekend(today):
            jour = "Samedi" if today.weekday() == 5 else "Dimanche"
            return Response(
                {
                    'error': (
                        f"Pointage désactivé le week-end ({jour}). "
                        "Le pointage n'est actif que du lundi au vendredi."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # ---- FIN Règle Week-end ----

        # ---- Règle 17h30 : blocage check-in après 17h30 ----
        HEURE_LIMITE_CHECKIN = time(17, 30)  # 17h30
        if current_time >= HEURE_LIMITE_CHECKIN:
            return Response(
                {
                    'error': (
                        f"Pointage refusé : il est {current_time.strftime('%Hh%M')}. "
                        "Le pointage d'arrivée n'est accepté que jusqu'à 17h30."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # ---- FIN Règle 17h30 ----

        # Vérifier si déjà pointé aujourd'hui
        pointage, created = Pointage.objects.get_or_create(
            employee=request.user,
            date=today,
            defaults={'heure_arrivee': current_time}
        )
        
        if not created and pointage.heure_arrivee:
            return Response({
                'message': 'Vous avez déjà pointé votre arrivée aujourd\'hui',
                'pointage': PointageSerializer(pointage).data
            }, status=status.HTTP_200_OK)
        
        if not created:
            pointage.heure_arrivee = current_time
            pointage.save()
        
        # Déterminer le statut et message
        seuil_retard = datetime.combine(today, Pointage.SEUIL_RETARD)
        arrivee = datetime.combine(today, current_time)
        
        if arrivee > seuil_retard:
            retard = arrivee - seuil_retard
            retard_minutes = int(retard.total_seconds() / 60)
            message = f"Pointage enregistré. Vous avez {retard_minutes // 60}h {retard_minutes % 60:02d}min de retard."
        else:
            message = "Pointage enregistré. Bonne journée !"
        
        # Ajouter rappel pause
        message += " N'oubliez pas votre pause déjeuner de 13h00 à 13h30 (30 min obligatoires)."
        
        return Response({
            'message': message,
            'pointage': PointageSerializer(pointage).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """Pointer le départ (check-out) — inactif le week-end"""
        local_now = timezone.localtime(timezone.now())
        today = local_now.date()
        current_time = local_now.time()

        # ---- Règle Week-end : blocage samedi et dimanche ----
        if is_weekend(today):
            jour = "Samedi" if today.weekday() == 5 else "Dimanche"
            return Response(
                {
                    'error': (
                        f"Pointage désactivé le week-end ({jour}). "
                        "Le pointage n'est actif que du lundi au vendredi."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # ---- FIN Règle Week-end ----
        
        try:
            pointage = Pointage.objects.get(employee=request.user, date=today)
        except Pointage.DoesNotExist:
            return Response(
                {'error': 'Vous n\'avez pas encore pointé votre arrivée aujourd\'hui'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if pointage.heure_depart:
            return Response({
                'message': 'Vous avez déjà pointé votre départ aujourd\'hui',
                'pointage': PointageSerializer(pointage).data
            }, status=status.HTTP_200_OK)
        
        pointage.heure_depart = current_time
        pointage.save()
        
        # Calculer les heures travaillées
        heures = float(pointage.heures_travaillees or 0)
        heures_str = f"{heures:.2f}"
        
        # Vérifier si départ avant 17h (sortie anticipée)
        reference_fin = datetime.combine(today, Pointage.HEURE_FIN)
        depart = datetime.combine(today, current_time)
        
        if depart < reference_fin:
            if employee_has_sortie_permission(request.user, local_now):
                diff = reference_fin - depart
                diff_minutes = int(diff.total_seconds() / 60)
                message = (
                    f"Départ enregistré. Heures travaillées: {heures_str}h. "
                    f"Sortie anticipée (permission validée) de {diff_minutes // 60}h {diff_minutes % 60}min."
                )
            else:
                Pointage.objects.filter(pk=pointage.pk).update(
                    statut='absent',
                    commentaire='Sortie anticipée sans permission de sortie — journée en absence',
                )
                pointage.refresh_from_db()
                message = (
                    f"Départ enregistré. Heures travaillées: {heures_str}h. "
                    "Sortie anticipée - Cette journée sera considérée comme ABSENCE."
                )
        else:
            message = f"Départ enregistré. Heures travaillées: {heures_str}h. Bonne soirée !"
        
        return Response({
            'message': message,
            'pointage': PointageSerializer(pointage).data
        })
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Récupérer le pointage du jour"""
        today = timezone.localtime(timezone.now()).date()
        from .role_utils import is_admin_or_rh
        pointages = Pointage.objects.filter(date=today)
        if not is_admin_or_rh(request.user):
            pointages = pointages.filter(employee=request.user)
        
        serializer = PointageSerializer(pointages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_stats(self, request):
        """Statistiques de pointage pour l'employé connecté (jours ouvrables uniquement)"""
        user = request.user
        local_now = timezone.localtime(timezone.now())
        mois = request.query_params.get('mois', local_now.month)
        annee = request.query_params.get('annee', local_now.year)
        
        # On exclut les weekends des statistiques
        pointages = Pointage.objects.filter(
            employee=user,
            date__month=mois,
            date__year=annee,
        ).exclude(date__week_day__in=[1, 7])  # 1=Dimanche, 7=Samedi (notation Django)
        
        total_retards = pointages.filter(statut='retard').count()
        total_permissions = pointages.filter(statut='permission').count()
        total_absences = pointages.filter(statut='absent').count()
        total_presence = pointages.filter(statut='present').count()
        
        total_heures = sum(p.heures_travaillees for p in pointages)
        total_minutes_retard = sum(p.minutes_retard for p in pointages)
        
        return Response({
            'mois': mois,
            'annee': annee,
            'total_jours': pointages.count(),
            'present': total_presence,
            'retards': total_retards,
            'permissions': total_permissions,
            'absences': total_absences,
            'heures_travaillees': round(total_heures, 2),
            'total_retard_heures': round(total_minutes_retard / 60, 2),
        })

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Statistiques pour le tableau de bord Admin et RH"""
        if request.user.role not in ['admin', 'rh']:
            return Response(
                {"error": "Accès non autorisé."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.utils import timezone
        from datetime import date, timedelta
        from django.db.models import Count, Q
        from core.conges import Conge
        from core.permissions import PermissionRequest
        
        local_now = timezone.localtime(timezone.now())
        today = local_now.date()

        # Si aujourd'hui est un week-end, calculer les stats sur le dernier vendredi
        ref_day = today
        while is_weekend(ref_day):
            ref_day -= timedelta(days=1)
        
        # Base queryset : seulement les pointages des employés (role='employe')
        # Exclut les pointages des admin/RH du tableau de bord
        employe_pointages = Pointage.objects.filter(employee__role='employe')
        
        # 1. KPIs de base
        total_employees = User.objects.filter(role='employe').count()
        
        # Employés présents = ceux qui ont un pointage 'present' ou 'retard' ce jour
        present_today = employe_pointages.filter(
            date=ref_day,
            statut__in=['present', 'retard']
        ).count()
        
        absent_today = max(0, total_employees - present_today)
        
        retard_today = employe_pointages.filter(
            date=ref_day,
            statut='retard'
        ).count()
        
        active_conges = Conge.objects.filter(
            date_debut__lte=local_now,
            date_fin__gte=local_now,
            statut='approuve'
        ).count()
        
        active_permissions = PermissionRequest.objects.filter(
            date_sortie__lte=local_now,
            date_retour__gte=local_now,
            status='approuve'
        ).count()
        
        conges_permissions_today = active_conges + active_permissions
        
        manual_pointages = employe_pointages.filter(
            commentaire__isnull=False
        ).exclude(commentaire='').count()
        
        start_of_month = today.replace(day=1)
        retard_month = employe_pointages.filter(
            date__gte=start_of_month,
            statut='retard'
        ).exclude(date__week_day__in=[1, 7]).count()
        
        # 2. Données pour les graphiques (selon la période demandée)
        # Toujours filtré sur role='employe' et excluant les week-ends
        period = request.query_params.get('period', 'jour')
        
        if period == 'jour':
            present_val = employe_pointages.filter(date=ref_day, statut='present').count()
            retard_val = employe_pointages.filter(date=ref_day, statut='retard').count()
            # Absent = employés sans pointage présent/retard ce jour
            absent_val = max(0, total_employees - present_val - retard_val)

        elif period == 'semaine':
            start_date = today - timedelta(days=6)
            period_qs = employe_pointages.filter(
                date__range=[start_date, today]
            ).exclude(date__week_day__in=[1, 7])
            
            present_val = period_qs.filter(statut='present').count()
            retard_val = period_qs.filter(statut='retard').count()
            
            # Absences = jours ouvrables où l'employé n'a pas de pointage présent/retard
            absent_val = 0
            for i in range(7):
                d = start_date + timedelta(days=i)
                if is_weekend(d):
                    continue
                p_count = employe_pointages.filter(date=d, statut__in=['present', 'retard']).count()
                absent_val += max(0, total_employees - p_count)

        elif period == 'mois':
            start_date = today - timedelta(days=29)
            period_qs = employe_pointages.filter(
                date__range=[start_date, today]
            ).exclude(date__week_day__in=[1, 7])
            
            present_val = period_qs.filter(statut='present').count()
            retard_val = period_qs.filter(statut='retard').count()
            
            absent_val = 0
            for i in range(30):
                d = start_date + timedelta(days=i)
                if is_weekend(d):
                    continue
                p_count = employe_pointages.filter(date=d, statut__in=['present', 'retard']).count()
                absent_val += max(0, total_employees - p_count)

        else:  # annee / an
            start_date = today - timedelta(days=364)
            period_qs = employe_pointages.filter(
                date__range=[start_date, today]
            ).exclude(date__week_day__in=[1, 7])
            
            present_val = period_qs.filter(statut='present').count()
            retard_val = period_qs.filter(statut='retard').count()
            
            total_active = period_qs.filter(statut__in=['present', 'retard']).count()
            # Compter les jours ouvrables réels de la période
            working_days_count = sum(
                1 for i in range(365)
                if not is_weekend(start_date + timedelta(days=i))
            )
            absent_val = max(0, (total_employees * working_days_count) - total_active)
            
        return Response({
            "kpis": {
                "total_employees": total_employees,
                "present_today": present_today,
                "absent_today": absent_today,
                "retard_today": retard_today,
                "manual_pointages": manual_pointages,
                "retard_month": retard_month,
                "conges_permissions_today": conges_permissions_today,
            },
            "charts": {
                "present": present_val,
                "retard": retard_val,
                "absent": absent_val,
            }
        })


        # Si aujourd'hui est un week-end, calculer les stats sur le dernier vendredi
        ref_day = today
        while is_weekend(ref_day):
            ref_day -= timedelta(days=1)
        
        # 1. KPIs de base
        total_employees = User.objects.filter(role='employe').count()
        
        present_today = Pointage.objects.filter(
            date=ref_day, 
            statut__in=['present', 'retard']
        ).count()
        
        absent_today = max(0, total_employees - present_today)
        
        retard_today = Pointage.objects.filter(
            date=ref_day,
            statut='retard'
        ).count()
        
        active_conges = Conge.objects.filter(
            date_debut__lte=local_now,
            date_fin__gte=local_now,
            statut='approuve'
        ).count()
        
        active_permissions = PermissionRequest.objects.filter(
            date_sortie__lte=local_now,
            date_retour__gte=local_now,
            status='approuve'
        ).count()
        
        conges_permissions_today = active_conges + active_permissions
        
        manual_pointages = Pointage.objects.filter(
            commentaire__isnull=False
        ).exclude(commentaire='').count()
        
        start_of_month = today.replace(day=1)
        retard_month = Pointage.objects.filter(
            date__gte=start_of_month,
            statut='retard'
        ).exclude(date__week_day__in=[1, 7]).count()
        
        # 2. Données pour les graphiques (selon la période demandée)
        # On exclut toujours les week-ends des comptages
        period = request.query_params.get('period', 'jour')
        
        if period == 'jour':
            present_val = Pointage.objects.filter(date=ref_day, statut='present').count()
            retard_val = Pointage.objects.filter(date=ref_day, statut='retard').count()
            # Absents réels en DB + ceux non marqués (employees sans pointage ce jour)
            absent_in_db = Pointage.objects.filter(date=ref_day, statut='absent').count()
            # Employees sans aucun pointage aujourd'hui = aussi absents
            employees_with_pointage = Pointage.objects.filter(
                date=ref_day, statut__in=['present', 'retard', 'absent', 'permission', 'conge']
            ).values('employee').distinct().count()
            absent_val = absent_in_db + max(0, total_employees - employees_with_pointage - absent_in_db)
            # Simplifié : total employes - ceux présents (present+retard)
            absent_val = max(0, total_employees - present_val - retard_val)

        elif period == 'semaine':
            start_date = today - timedelta(days=6)
            # Filtrer uniquement les jours ouvrables
            pointages_period = Pointage.objects.filter(
                date__range=[start_date, today]
            ).exclude(date__week_day__in=[1, 7])
            
            present_val = pointages_period.filter(statut='present').count()
            retard_val = pointages_period.filter(statut='retard').count()
            absent_in_db = pointages_period.filter(statut='absent').count()
            
            # Calculer les absences implicites (employees sans pointage par jour ouvrable)
            absent_implicit = 0
            for i in range(7):
                d = start_date + timedelta(days=i)
                if is_weekend(d):
                    continue  # Ignorer samedi et dimanche
                p_count = Pointage.objects.filter(date=d, statut__in=['present', 'retard']).count()
                absent_implicit += max(0, total_employees - p_count)
            absent_val = absent_implicit

        elif period == 'mois':
            start_date = today - timedelta(days=29)
            pointages_period = Pointage.objects.filter(
                date__range=[start_date, today]
            ).exclude(date__week_day__in=[1, 7])
            
            present_val = pointages_period.filter(statut='present').count()
            retard_val = pointages_period.filter(statut='retard').count()
            
            absent_val = 0
            for i in range(30):
                d = start_date + timedelta(days=i)
                if is_weekend(d):
                    continue  # Ignorer samedi et dimanche
                p_count = Pointage.objects.filter(date=d, statut__in=['present', 'retard']).count()
                absent_val += max(0, total_employees - p_count)

        else: # annee / an
            start_date = today - timedelta(days=364)
            pointages_period = Pointage.objects.filter(
                date__range=[start_date, today]
            ).exclude(date__week_day__in=[1, 7])
            
            present_val = pointages_period.filter(statut='present').count()
            retard_val = pointages_period.filter(statut='retard').count()
            
            total_active_pointages = pointages_period.filter(statut__in=['present', 'retard']).count()
            # ~260 jours ouvrables par an (52 semaines × 5 jours)
            working_days = 260
            absent_val = max(0, (total_employees * working_days) - total_active_pointages)
            
        return Response({
            "kpis": {
                "total_employees": total_employees,
                "present_today": present_today,
                "absent_today": absent_today,
                "retard_today": retard_today,
                "manual_pointages": manual_pointages,
                "retard_month": retard_month,
                "conges_permissions_today": conges_permissions_today,
            },
            "charts": {
                "present": present_val,
                "retard": retard_val,
                "absent": absent_val,
            }
        })

