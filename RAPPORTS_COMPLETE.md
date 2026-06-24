# 📊 **SYSTÈME DE GESTION DES RAPPORTS**

## 📋 **Table Rapport (Structure Complète)**

### 🏗️ **Modèle Rapport dans `core/rapport.py`**

```python
class Rapport(models.Model):
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
    filtres = models.JSONField(default=dict, blank=True)
    parametres = models.JSONField(default=dict, blank=True)
    
    # Statistiques et résultats
    total_enregistrements = models.IntegerField(default=0)
    total_heures = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pourcentage_presence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Destinataires
    destinataires = models.ManyToManyField(User, blank=True, related_name='rapports_recus')
```

### 📊 **Types de Rapports Disponibles**

| Type | Code | Description |
|------|-------|-------------|
| Rapport de Présence | `presence` | Analyse des présences et absences |
| Rapport d'Activité | `activite` | Rapport d'activité générale |
| Rapport de Performance | `performance` | Évaluation des performances |
| Rapport de Congés | `conges` | Synthèse des congés pris |
| Rapport de Bulletins | `bulletins` | Rapport des bulletins de salaire |
| Rapport de Violations | `violations` | Analyse des violations |
| Rapport Statistiques | `statistiques` | Rapport statistique global |

### 📅 **Périodes de Rapports**

| Période | Code | Description |
|---------|------|-------------|
| Journalier | `jour` | Rapport quotidien |
| Hebdomadaire | `semaine` | Rapport hebdomadaire |
| Mensuel | `mois` | Rapport mensuel |
| Trimestriel | `trimestre` | Rapport trimestriel |
| Semestriel | `semestre` | Rapport semestriel |
| Annuel | `annee` | Rapport annuel |
| Personnalisé | `personnalise` | Période personnalisée |

### 📋 **Statuts des Rapports**

| Statut | Code | Description |
|--------|-------|-------------|
| Brouillon | `brouillon` | Rapport en cours de rédaction |
| En Cours | `en_cours` | Rapport en cours de génération |
| Terminé | `termine` | Rapport généré, en attente de validation |
| Validé | `valide` | Rapport validé et publié |
| Rejeté | `rejete` | Rapport rejeté |

---

## 🌐 **API de Gestion des Rapports**

### 📝 **Créer un Rapport (Admin/RH uniquement)**
```http
POST /api/rapports/
Authorization: Bearer <admin_or_rh_token>
Content-Type: application/json

{
    "titre": "Rapport de Présence Mensuel",
    "type_rapport": "presence",
    "periode_rapport": "mois",
    "date_debut": "2026-04-01",
    "date_fin": "2026-04-30",
    "description": "Rapport de présence pour avril 2026",
    "filtres": {"service": "IT", "inclure_weekend": false},
    "parametres": {"format_export": "pdf"},
    "destinataires": [18, 19]
}
```

**Réponse :**
```json
{
    "id": 1,
    "titre": "Rapport de Présence Mensuel",
    "type_rapport": "presence",
    "type_rapport_display": "Rapport de Présence",
    "periode_rapport": "mois",
    "periode_display": "Mensuel",
    "date_debut": "2026-04-01",
    "date_fin": "2026-04-30",
    "duree_jours": 30,
    "auteur_name": "Pierre Martin",
    "statut": "brouillon",
    "statut_display": "Brouillon",
    "date_generation": "2026-04-01T10:00:00Z"
}
```

### 👁️ **Lister les Rapports**
```http
GET /api/rapports/
Authorization: Bearer <access_token>
```

**Réponse (Admin/RH) :** Tous les rapports
**Réponse (Employé) :** Seulement les rapports qui lui sont destinés

### 🔄 **Mettre à Jour un Rapport**
```http
PATCH /api/rapports/{id}/
Authorization: Bearer <admin_or_rh_token>
Content-Type: application/json

{
    "titre": "Rapport modifié",
    "description": "Description mise à jour",
    "statut": "termine"
}
```

---

## 🎯 **Actions Spéciales**

### 🤖 **Génération Automatique**
```http
POST /api/rapports/{id}/generer_auto/
Authorization: Bearer <admin_or_rh_token>
Content-Type: application/json

{
    "employe_ids": [18, 19],
    "inclure_details": true,
    "format_export": "json"
}
```

**Réponse :**
```json
{
    "message": "Rapport généré avec succès",
    "rapport": {
        "id": 1,
        "statut": "termine",
        "total_enregistrements": 45,
        "total_heures": 360.50
    }
}
```

### ✅ **Validation d'un Rapport**
```http
POST /api/rapports/{id}/valider/
Authorization: Bearer <admin_or_rh_token>
Content-Type: application/json

{}
```

### 📋 **Voir ses Propres Rapports**
```http
GET /api/rapports/mes_rapports/
Authorization: Bearer <access_token>
```

### 📊 **Statistiques des Rapports**
```http
GET /api/rapports/statistiques/
Authorization: Bearer <admin_or_rh_token>
```

**Réponse :**
```json
{
    "total_rapports": 15,
    "par_type": [
        {
            "type_rapport": "presence",
            "count": 8,
            "type_rapport_display": "Rapport de Présence"
        },
        {
            "type_rapport": "conges",
            "count": 4,
            "type_rapport_display": "Rapport de Congés"
        }
    ],
    "par_statut": [
        {
            "statut": "valide",
            "count": 10,
            "statut_display": "Validé"
        }
    ],
    "recent": [
        {
            "id": 15,
            "titre": "Rapport Q1 2026",
            "type_rapport": "presence",
            "date_generation": "2026-04-01",
            "statut": "valide"
        }
    ]
}
```

### 📋 **Dupliquer un Rapport**
```http
POST /api/rapports/{id}/dupliquer/
Authorization: Bearer <admin_or_rh_token>
Content-Type: application/json

{}
```

---

## 🔒 **Permissions par Rôle**

| Action | Employé | RH | Admin |
|--------|---------|----|-------|
| Créer rapport | ❌ | ✅ | ✅ |
| Voir tous les rapports | ❌ | ✅ | ✅ |
| Voir ses rapports | ✅ | ✅ | ✅ |
| Mettre à jour | ❌ | ✅ | ✅ |
| Supprimer | ❌ | ✅ | ✅ |
| Générer automatiquement | ❌ | ✅ | ✅ |
| Valider | ❌ | ✅ | ✅ |
| Voir statistiques | ❌ | ✅ | ✅ |
| Dupliquer | ❌ | ✅ | ✅ |

---

## 🤖 **Fonctions de Génération Automatique**

### 📊 **Rapport de Présence**
- Analyse des demandes de permission
- Calcul des taux de présence
- Statistiques par employé et par service
- Identification des absences récurrentes

### 🏖️ **Rapport de Congés**
- Synthèse des congés par type
- Calcul des soldes utilisés
- Analyse des tendances de congés
- Rapports par période et par employé

### 💰 **Rapport de Bulletins**
- Agrégation des bulletins de salaire
- Calculs des totaux par période
- Statistiques sur les heures supplémentaires
- Analyse des déductions et impôts

---

## 🧪 **Tests Validés avec Succès**

### ✅ **Fonctionnalités Testées**
```
✅ Table rapport créée et fonctionnelle
✅ API complète avec tous les endpoints
✅ Permissions CRUD respectées (Admin/RH uniquement)
✅ Génération automatique fonctionnelle
✅ Validation et workflow opérationnels
✅ Statistiques détaillées disponibles
✅ Sécurité des accès par rôle
```

### 📈 **Résultats des Tests**
```
✅ Admin connecté
✅ Rapport créé avec succès
   📋 Titre: Rapport de Présence Q1 2026
   📊 Type: Rapport de Présence
   📅 Période: Trimestriel
   📆 Durée: 90 jours
   👤 Auteur: Pierre Martin

✅ Statistiques obtenues
   📊 Total rapports: 4
   📈 Répartition par type:
      - Rapport de Congés: 1
      - Rapport de Présence: 3
```

---

## 🎉 **Avantages du Système**

### ✅ **Fonctionnalités Complètes**
- Gestion complète des rapports
- Génération automatique intelligente
- Workflow de validation intégré
- Statistiques détaillées et exportables

### 🔒 **Sécurité Robuste**
- Permissions granulaires par rôle
- Contrôle d'accès par destinataires
- Audit trail complet des modifications
- Validation des données d'entrée

### 📱 **Flexibilité et Extensibilité**
- Types de rapports personnalisables
- Périodes configurables
- Filtres et paramètres flexibles
- Support des exports multiples formats

### 🔧 **Performance Optimisée**
- Indexation des requêtes
- Mise en cache des statistiques
- Génération asynchrone possible
- Pagination des résultats

---

## 🔄 **Workflow Complet**

```
1. Admin/RH → Crée un rapport (brouillon)
2. Système → Configure les filtres et paramètres
3. Admin/RH → Lance la génération automatique
4. Système → Génère le contenu et les statistiques
5. Admin/RH → Valide le rapport
6. Système → Notifie les destinataires
7. Employés → Consultent les rapports qui leur sont destinés
```

**Le système de gestion des rapports est maintenant complet et prêt pour la production !** 🚀
