from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('rh', 'RH'),
        ('employe', 'Employé'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employe')
    service = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    adresse = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse")

    badge_rfid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    face_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


# 🔽 🔽 🔽 TU AJOUTES ICI 🔽 🔽 🔽

class Pointage(models.Model):

    STATUS_CHOICES = [
        ('autorise', 'Autorisé'),
        ('refuse', 'Refusé'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    uid = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    heure = models.CharField(max_length=20)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uid} - {self.status} - {self.date}"