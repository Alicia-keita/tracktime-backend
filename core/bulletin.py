"""
Module de gestion des bulletins de salaire
"""

from django.db import models
from django.contrib.auth import get_user_model
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta

User = get_user_model()


class Bulletin(models.Model):
    """Modèle pour les bulletins de salaire"""
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bulletins')
    periode_debut = models.DateField(verbose_name="Début de période")
    periode_fin = models.DateField(verbose_name="Fin de période")
    
    # Données de pointage
    heures_travaillees = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Heures travaillées")
    heures_supplementaires = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Heures supplémentaires")
    nb_absences = models.IntegerField(default=0, verbose_name="Nombre d'absences")
    nb_retards = models.IntegerField(default=0, verbose_name="Nombre de retards")
    
    # Calculs salariaux
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire de base")
    prime_heures_sup = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Prime heures sup.")
    deduction_absences = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Déduction absences")
    salaire_brut = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire brut")
    
    # Déductions et net
    cnss = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="CNSS")
    impot = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Impôt sur le revenu")
    autres_deductions = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Autres déductions")
    salaire_net = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire net")
    
    # Métadonnées
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")
    genere_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bulletins_generees', verbose_name="Généré par")
    
    class Meta:
        verbose_name = "Bulletin de salaire"
        verbose_name_plural = "Bulletins de salaire"
        ordering = ['-periode_debut']
        unique_together = ['employee', 'periode_debut', 'periode_fin']

    def __str__(self):
        return f"Bulletin {self.employee.username} - {self.periode_debut} au {self.periode_fin}"


class BulletinSerializer(serializers.ModelSerializer):
    """Serializer pour les bulletins - ID masqué pour le frontend"""
    employee_name = serializers.CharField(source='employee.username', read_only=True)
    employee_first_name = serializers.CharField(source='employee.first_name', read_only=True)
    employee_last_name = serializers.CharField(source='employee.last_name', read_only=True)
    genere_par_name = serializers.CharField(source='genere_par.username', read_only=True)
    
    class Meta:
        model = Bulletin
        fields = [
            'employee', 'employee_name', 'employee_first_name', 'employee_last_name',
            'periode_debut', 'periode_fin', 'heures_travaillees', 'heures_supplementaires',
            'nb_absences', 'nb_retards', 'salaire_base', 'prime_heures_sup',
            'deduction_absences', 'salaire_brut', 'cnss', 'impot', 'autres_deductions',
            'salaire_net', 'date_generation', 'genere_par', 'genere_par_name'
        ]
        read_only_fields = ['date_generation', 'genere_par', 'salaire_brut', 'salaire_net']


class BulletinGenerateSerializer(serializers.Serializer):
    employee = serializers.IntegerField()
    periode_debut = serializers.DateField()
    periode_fin = serializers.DateField()
    
    def validate(self, data):
        if data['periode_debut'] > data['periode_fin']:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin."
            )
        return data


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == 'admin' or request.user.is_staff or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsRHOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['rh', 'admin']

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class BulletinViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des bulletins de salaire"""
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from .role_utils import is_admin_or_rh
        user = self.request.user
        if is_admin_or_rh(user):
            return Bulletin.objects.all()
        return Bulletin.objects.filter(employee=user)

    def get_permissions(self):
        """
        Définit les permissions par action :
        - generate : RH et Admin seulement
        - destroy (DELETE) : Admin seulement
        - autres : Utilisateurs authentifiés
        """
        if self.action == 'generate':
            permission_classes = [IsRHOrAdmin]
        elif self.action == 'destroy':
            permission_classes = [IsAdminOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], permission_classes=[IsRHOrAdmin])
    def generate(self, request):
        """
        Générer un bulletin de salaire selon le diagramme:
        1. RH demande la génération
        2. Système récupère données de pointage
        3. Système vérifie heures + absences
        4. Système effectue calcul du salaire
        5. Système enregistre le bulletin
        6. Retourne le bulletin généré
        """
        serializer = BulletinGenerateSerializer(data=request.data)
        if serializer.is_valid():
            employee_id = serializer.validated_data['employee']
            periode_debut = serializer.validated_data['periode_debut']
            periode_fin = serializer.validated_data['periode_fin']
            
            try:
                employee = User.objects.get(id=employee_id)
                
                # Vérifier si un bulletin existe déjà pour cette période
                if Bulletin.objects.filter(
                    employee=employee,
                    periode_debut=periode_debut,
                    periode_fin=periode_fin
                ).exists():
                    return Response(
                        {"error": "Un bulletin existe déjà pour cette période."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # 1. Récupérer les données de pointage (simulées)
                heures_travaillees = self._calculer_heures_travaillees(employee, periode_debut, periode_fin)
                heures_supplementaires = self._calculer_heures_supplementaires(employee, periode_debut, periode_fin)
                nb_absences = self._calculer_absences(employee, periode_debut, periode_fin)
                nb_retards = self._calculer_retards(employee, periode_debut, periode_fin)
                
                # 2. Vérifier heures + absences
                if nb_absences > 10:  # Seuil d'alerte
                    return Response(
                        {"warning": f"Nombre élevé d'absences: {nb_absences}"},
                        status=status.HTTP_200_OK
                    )
                
                # 3. Calcul du salaire
                salaire_base = Decimal('2000.00')  # Salaire de base mensuel
                taux_horaire = salaire_base / Decimal('173.33')  # Base 40h/semaine
                
                prime_heures_sup = heures_supplementaires * (taux_horaire * Decimal('1.25'))
                deduction_absences = nb_absences * (salaire_base / Decimal('30'))
                
                salaire_brut = salaire_base + prime_heures_sup - deduction_absences
                
                # Calcul des déductions
                cnss = salaire_brut * Decimal('0.043')  # 4.3% CNSS
                impot = self._calculer_impot(salaire_brut)
                autres_deductions = Decimal('0.00')
                
                salaire_net = salaire_brut - cnss - impot - autres_deductions
                
                # 4. Enregistrer le bulletin
                bulletin = Bulletin.objects.create(
                    employee=employee,
                    periode_debut=periode_debut,
                    periode_fin=periode_fin,
                    heures_travaillees=heures_travaillees,
                    heures_supplementaires=heures_supplementaires,
                    nb_absences=nb_absences,
                    nb_retards=nb_retards,
                    salaire_base=salaire_base,
                    prime_heures_sup=prime_heures_sup,
                    deduction_absences=deduction_absences,
                    salaire_brut=salaire_brut,
                    cnss=cnss,
                    impot=impot,
                    autres_deductions=autres_deductions,
                    salaire_net=salaire_net,
                    genere_par=request.user
                )
                
                # 5. Retourner le bulletin généré
                serializer = BulletinSerializer(bulletin)
                return Response({
                    "message": "Bulletin généré avec succès.",
                    "bulletin": serializer.data
                }, status=status.HTTP_201_CREATED)
                
            except User.DoesNotExist:
                return Response(
                    {"error": "Employé non trouvé."},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": f"Erreur lors de la génération: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _calculer_heures_travaillees(self, employee, debut, fin):
        """Simuler le calcul des heures travaillées"""
        jours_travailles = 20  # Simulé
        return Decimal(str(jours_travailles * 8))  # 8h par jour

    def _calculer_heures_supplementaires(self, employee, debut, fin):
        """Simuler le calcul des heures supplémentaires"""
        return Decimal('5.50')  # Simulé

    def _calculer_absences(self, employee, debut, fin):
        """Calculer le nombre d'absences depuis les permissions approuvées"""
        # Import ici pour éviter les imports circulaires
        from .permissions import PermissionRequest
        return PermissionRequest.objects.filter(
            employee=employee,
            status='approved',
            date_sortie__range=[debut, fin]
        ).count()

    def _calculer_retards(self, employee, debut, fin):
        """Simuler le calcul des retards"""
        return 2  # Simulé

    def _calculer_impot(self, salaire_brut):
        """Calculer l'impôt sur le revenu (simulation)"""
        if salaire_brut <= Decimal('3000'):
            return salaire_brut * Decimal('0.10')
        elif salaire_brut <= Decimal('5000'):
            return salaire_brut * Decimal('0.15')
        else:
            return salaire_brut * Decimal('0.20')
