from django.apps import AppConfig
import threading
import json
import time as time_module
import paho.mqtt.client as mqtt
import os


def start_mqtt():
    
    from core.pointage import Pointage

    def on_message(client, userdata, msg):
        print("MQTT:", msg.topic, msg.payload.decode())

        try:
            data = json.loads(msg.payload.decode())
            from django.contrib.auth import get_user_model
            from django.utils import timezone
            
            User = get_user_model()
            
            uid = data.get("uid")
            status = data.get("status")
            heure_str = data.get("heure")
            
            # Si le statut est "refuse", on ignore
            if status == "refuse":
                print(f"[WARN] Accès refusé pour UID {uid}")
                return
            
            # Chercher l'utilisateur par badge_rfid
            try:
                user = User.objects.get(badge_rfid=uid)
            except User.DoesNotExist:
                print(f"[ERROR] Utilisateur non trouvé pour UID {uid}")
                return
            
            # Toujours utiliser l'heure locale exacte de la machine (serveur)
            local_now = timezone.localtime(timezone.now())
            current_time = local_now.time()
            today = local_now.date()
            time_str = current_time.strftime('%H:%M:%S')
            print(f"[INFO] Scan RFID reçu. Heure machine: {time_str} (Heure RFID reçue: {heure_str})")
            
            # Logique de pointage séquentiel
            from core.pointage import Pointage
            
            # Récupérer ou créer le pointage du jour
            pointage, created = Pointage.objects.get_or_create(
                employee=user,
                date=today,
                defaults={'heure_arrivee': current_time}
            )
            
            if created:
                print(f"[OK] 1er scan - Arrivée enregistrée pour {user.username} à {time_str}")
            else:
                # Déterminer l'étape actuelle du pointage
                if not pointage.heure_arrivee:
                    pointage.heure_arrivee = current_time
                    print(f"[OK] 1er scan - Arrivée enregistrée pour {user.username} à {time_str}")
                elif not pointage.debut_pause:
                    pointage.debut_pause = current_time
                    print(f"[OK] 2ème scan - Début pause enregistré pour {user.username} à {time_str}")
                elif not pointage.fin_pause:
                    pointage.fin_pause = current_time
                    print(f"[OK] 3ème scan - Fin pause enregistrée pour {user.username} à {time_str}")
                elif not pointage.heure_depart:
                    pointage.heure_depart = current_time
                    print(f"[OK] 4ème scan - Départ enregistré pour {user.username} à {time_str}")
                else:
                    # Tous les champs sont remplis, on met à jour l'heure de départ
                    pointage.heure_depart = current_time
                    print(f"[OK] Mise à jour - Départ enregistré pour {user.username} à {time_str}")
                
                pointage.save()

        except Exception as e:
            print("[ERROR] Erreur MQTT:", e)

    client = mqtt.Client()
    client.on_message = on_message

    mqtt_host = os.environ.get("MQTT_HOST", "127.0.0.1")
    try:
        client.connect(mqtt_host, 1883)
        client.subscribe("pointage/rfid")
        print(f"[OK] MQTT connecté à {mqtt_host}:1883")
        client.loop_forever()
    except Exception as e:
        print(f"[WARN] MQTT non disponible ({e.__class__.__name__}: {e}). Le serveur continue sans MQTT.")


def mark_absences_at_end_of_day():
    """
    Thread qui s'exécute en boucle et marque automatiquement comme ABSENT
    tout employé qui n'a pas pointé à 17h00 (fin de journée).
    S'exécute chaque jour ouvrable (lundi à vendredi).
    Le samedi et le dimanche sont ignorés.
    Au démarrage, effectue un rattrapage sur les 7 derniers jours ouvrables
    pour couvrir les jours potentiellement manqués.
    """
    import django
    from django.utils import timezone
    from datetime import time as dt_time, timedelta

    HEURE_VERIFICATION = dt_time(17, 0)  # 17h00 = fin de journée

    print("[OK] Thread vérification absences démarré (vérification quotidienne à 17h00, week-end exclu)")

    # --- Rattrapage au démarrage : couvrir les 7 derniers jours ouvrables ---
    try:
        local_now = timezone.localtime(timezone.now())
        today = local_now.date()
        for delta in range(1, 8):  # 1 à 7 jours en arrière
            past_day = today - timedelta(days=delta)
            # Ignorer les week-ends
            if past_day.weekday() >= 5:
                continue
            print(f"[INFO] Rattrapage absences pour le {past_day}...")
            _do_mark_absences(past_day)
        print("[OK] Rattrapage absences terminé.")
    except Exception as e:
        print(f"[ERROR] Erreur rattrapage absences: {e}")
    # --- Fin rattrapage ---

    already_run_today = None  # date de la dernière exécution

    while True:
        try:
            local_now = timezone.localtime(timezone.now())
            today = local_now.date()
            current_time = local_now.time()
            weekday = today.weekday()  # 0=Lundi, 6=Dimanche

            # Seulement les jours ouvrables (lun=0 à ven=4) et à partir de 17h00
            is_workday = weekday < 5  # 5=Samedi, 6=Dimanche exclus
            is_end_of_day = current_time >= HEURE_VERIFICATION
            not_already_run = (already_run_today != today)

            if is_workday and is_end_of_day and not_already_run:
                print(f"[INFO] Marquage des absences pour le {today}...")
                _do_mark_absences(today)
                already_run_today = today
                print(f"[OK] Absences marquées pour le {today}.")

        except Exception as e:
            print(f"[ERROR] Erreur thread absences: {e}")

        # Vérifier toutes les 5 minutes
        time_module.sleep(300)


def _do_mark_absences(today):
    """
    Marque comme absent tout employé sans pointage pour la date donnée.
    Ne s'exécute JAMAIS pour un samedi ou un dimanche.
    """
    from django.contrib.auth import get_user_model
    from core.pointage import Pointage
    from core.conges import Conge
    from core.permissions import PermissionRequest
    from django.utils import timezone

    # Sécurité : ne jamais créer d'absences un week-end
    if today.weekday() >= 5:  # 5=Samedi, 6=Dimanche
        print(f"[INFO] {today} est un week-end — marquage absences ignoré.")
        return

    User = get_user_model()
    employes = User.objects.filter(role='employe', is_active=True)

    count_absent = 0
    for emp in employes:
        # ✅ CORRIGÉ : Conge utilise le champ 'employe' (pas 'employee')
        en_conge = Conge.objects.filter(
            employe=emp,
            statut='approuve',
            date_debut__date__lte=today,
            date_fin__date__gte=today,
        ).exists()

        # PermissionRequest utilise bien 'employee'
        en_permission = PermissionRequest.objects.filter(
            employee=emp,
            status='approuve',
            date_sortie__date__lte=today,
            date_retour__date__gte=today,
        ).exists()

        if en_conge or en_permission:
            # L'employé est en congé ou permission -> ne pas marquer absent
            continue

        # Vérifier si un pointage existe déjà pour aujourd'hui
        # ✅ CORRIGÉ : Pointage utilise bien 'employee'
        pointage_existant = Pointage.objects.filter(employee=emp, date=today).first()

        if not pointage_existant:
            # Aucun pointage -> créer un enregistrement ABSENT
            Pointage.objects.create(
                employee=emp,
                date=today,
                statut='absent',
                commentaire='Absence automatique - Aucun pointage enregistré pour ce jour ouvrable'
            )
            count_absent += 1
            print(f"  [ABSENT] {emp.username} ({emp.email}) - aucun pointage ce jour")
        elif pointage_existant.statut not in ['present', 'retard', 'conge', 'permission', 'absent']:
            # Pointage partiel sans statut valide — marquer absent
            pointage_existant.statut = 'absent'
            pointage_existant.commentaire = (
                pointage_existant.commentaire or ''
            ) + ' | Absence auto: pointage incomplet (pas de départ enregistré)'
            pointage_existant.save()
            count_absent += 1
            print(f"  [ABSENT-PARTIEL] {emp.username} - pointage incomplet")

    print(f"[INFO] {count_absent} employé(s) marqué(s) absent(s) pour le {today}.")


def auto_checkout_at_1730():
    """
    Thread qui s'exécute en boucle et enregistre le départ à 17h30
    pour tout employé qui a un pointage d'arrivée mais n'a pas pointé son départ.
    S'exécute uniquement les jours ouvrables (lundi au vendredi).
    """
    import django
    from django.utils import timezone
    from datetime import time as dt_time, timedelta

    HEURE_AUTO_CHECKOUT = dt_time(17, 30) # 17h30 = heure limite de pointage

    print("[OK] Thread départ automatique démarré (vérification quotidienne à 17h30, week-end exclu)")

    # --- Rattrapage au démarrage : couvrir les 7 derniers jours ouvrables ---
    try:
        local_now = timezone.localtime(timezone.now())
        today = local_now.date()
        for delta in range(1, 8):
            past_day = today - timedelta(days=delta)
            if past_day.weekday() >= 5:
                continue
            print(f"[INFO] Rattrapage départ automatique pour le {past_day}...")
            _do_auto_checkout(past_day)
        print("[OK] Rattrapage départ automatique terminé.")
    except Exception as e:
        print(f"[ERROR] Erreur rattrapage départ automatique: {e}")

    already_run_today = None

    while True:
        try:
            local_now = timezone.localtime(timezone.now())
            today = local_now.date()
            current_time = local_now.time()
            weekday = today.weekday()

            is_workday = weekday < 5
            is_checkout_time = current_time >= HEURE_AUTO_CHECKOUT
            not_already_run = (already_run_today != today)

            if is_workday and is_checkout_time and not_already_run:
                print(f"[INFO] Exécution du départ automatique pour le {today}...")
                _do_auto_checkout(today)
                already_run_today = today
                print(f"[OK] Départ automatique terminé pour le {today}.")

        except Exception as e:
            print(f"[ERROR] Erreur thread départ automatique: {e}")

        time_module.sleep(300) # Vérifier toutes les 5 minutes


def _do_auto_checkout(today):
    """Enregistre le départ automatique à 17h30 pour la date donnée si l'employé a un pointage sans heure de départ."""
    from core.pointage import Pointage
    from datetime import time as dt_time
    
    # Sécurité : ne jamais faire de pointage automatique le week-end
    if today.weekday() >= 5:
        return

    pointages_sans_depart = Pointage.objects.filter(
        date=today,
        heure_arrivee__isnull=False,
        heure_depart__isnull=True
    )
    
    count_checkout = 0
    HEURE_AUTO_CHECKOUT = dt_time(17, 30)
    for pt in pointages_sans_depart:
        pt.heure_depart = HEURE_AUTO_CHECKOUT
        pt.commentaire = (pt.commentaire or "") + (" | " if pt.commentaire else "") + "Départ automatique enregistré à 17h30"
        pt.save()
        count_checkout += 1
        print(f"  [AUTO-CHECKOUT] Départ automatique enregistré pour {pt.employee.username}")
    
    if count_checkout > 0:
        print(f"[INFO] {count_checkout} départ(s) automatique(s) enregistré(s) pour le {today}.")


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return

        print("MQTT THREAD STARTED")

        # Thread MQTT (badge RFID)
        thread_mqtt = threading.Thread(target=start_mqtt)
        thread_mqtt.daemon = True
        thread_mqtt.start()

        # Thread vérification absences quotidiennes à 17h00
        thread_absences = threading.Thread(target=mark_absences_at_end_of_day)
        thread_absences.daemon = True
        thread_absences.start()
        print("[OK] Thread vérification absences démarré")

        # Thread départ automatique à 17h30
        thread_checkout = threading.Thread(target=auto_checkout_at_1730)
        thread_checkout.daemon = True
        thread_checkout.start()
        print("[OK] Thread départ automatique démarré")