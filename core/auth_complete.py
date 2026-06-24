"""
Module d'authentification complet basé sur la structure User
"""

import threading
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'service',
            'badge_rfid', 'face_id'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'service', 'badge_rfid', 'face_id',
            'is_staff', 'is_superuser', 'date_joined', 'last_login'
        ]
        read_only_fields = ['is_staff', 'is_superuser', 'date_joined', 'last_login']


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Serializer personnalisé pour le login - accepte username ou email"""
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        print(f"DEBUG - Données reçues: {data}")  # Debug log

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password')

        # Résoudre le vrai username Django à partir de l'email
        # Cas 1 : username ressemble à un email (contient @)
        if username and '@' in username:
            email = email or username
            username = ''

        # Cas 2 : email fourni → chercher l'utilisateur par email
        if email and not username:
            try:
                user_by_email = User.objects.get(email=email)
                username = user_by_email.username
                print(f"DEBUG - Email trouvé, username résolu: {username}")
            except User.DoesNotExist:
                print(f"DEBUG - Aucun utilisateur avec l'email: {email}")
                raise serializers.ValidationError(
                    "Identifiants invalides. Veuillez vérifier votre email et mot de passe."
                )

        if not username or not password:
            print(f"DEBUG - Champs manquants - username: {username}, password: {'***' if password else None}")
            raise serializers.ValidationError(
                "Veuillez fournir un identifiant et un mot de passe."
            )

        user = authenticate(username=username, password=password)

        if not user:
            print(f"DEBUG - Authentification échouée pour username: {username}")
            raise serializers.ValidationError(
                "Identifiants invalides. Veuillez vérifier votre nom d'utilisateur et mot de passe."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Ce compte a été désactivé."
            )

        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)

        # Créer la réponse avec les tokens et les infos utilisateur
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data
        }

        print(f"DEBUG - Login réussi pour: {user.username} | role: {user.role}")
        return response_data



class PasswordChangeSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("L'ancien mot de passe est incorrect.")
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer pour la réinitialisation du mot de passe"""
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Aucun utilisateur trouvé avec cet email.")
        return value


def send_welcome_email(user, raw_password):
    """Envoie un email de bienvenue complet avec les identifiants de connexion."""
    try:
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'TRACKTIME <noreply@tracktime.com>')

        prenom = user.first_name or user.username
        nom_complet = f"{user.first_name} {user.last_name}".strip() or user.username
        role_labels = {
            'admin':   'Administrateur',
            'rh':      'Responsable RH',
            'employe': 'Employé',
        }
        role_display = role_labels.get(user.role, user.role)

        subject = '🎉 Bienvenue sur TRACKTIME – Vos identifiants de connexion'

        text_content = (
            f"Bonjour {prenom},\n\n"
            f"Bienvenue sur la plateforme TRACKTIME !\n"
            f"Votre compte employé a été créé avec succès.\n\n"
            f"--- VOS IDENTIFIANTS DE CONNEXION ---\n"
            f"Nom d'utilisateur : {user.username}\n"
            f"Mot de passe      : {raw_password}\n"
            f"Rôle              : {role_display}\n\n"
            f"Accédez à votre espace ici : {frontend_url}\n\n"
            f"Pour vous connecter :\n"
            f"  1. Allez sur {frontend_url}\n"
            f"  2. Entrez votre nom d'utilisateur : {user.username}\n"
            f"  3. Entrez votre mot de passe\n"
            f"  4. Cliquez sur 'Se connecter'\n\n"
            f"Nous vous conseillons de changer votre mot de passe après la première connexion.\n\n"
            f"Cordialement,\nL'équipe TRACKTIME"
        )

        html_content = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>Bienvenue sur TRACKTIME</title>
        </head>
        <body style="margin:0;padding:0;background:#eef2f7;font-family:'Segoe UI',Arial,sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#eef2f7;padding:40px 0;">
            <tr>
              <td align="center">
                <table width="620" cellpadding="0" cellspacing="0"
                       style="background:#ffffff;border-radius:20px;overflow:hidden;
                              box-shadow:0 8px 32px rgba(30,58,95,0.13);max-width:620px;width:100%;">

                  <!-- HEADER -->
                  <tr>
                    <td style="background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);
                               padding:44px 48px 36px;text-align:center;">
                      <div style="display:inline-block;background:rgba(255,255,255,0.15);
                                  border-radius:50%;padding:16px;margin-bottom:16px;">
                        <span style="font-size:36px;">&#x23F1;</span>
                      </div>
                      <h1 style="margin:0 0 6px;color:#ffffff;font-size:30px;font-weight:800;
                                 letter-spacing:3px;">TRACKTIME</h1>
                      <p style="margin:0;color:#a8d4f5;font-size:13px;letter-spacing:1px;
                                text-transform:uppercase;">Gestion du temps de travail</p>
                    </td>
                  </tr>

                  <!-- GREETING -->
                  <tr>
                    <td style="padding:40px 48px 0;">
                      <h2 style="margin:0 0 12px;color:#1e3a5f;font-size:24px;font-weight:700;">
                        Bonjour {prenom} ! &#x1F44B;
                      </h2>
                      <p style="margin:0 0 8px;color:#4a5568;font-size:15px;line-height:1.8;">
                        Nous sommes ravis de vous accueillir sur la plateforme
                        <strong style="color:#2563eb;">TRACKTIME</strong>.
                        Votre compte employé a été créé avec succès par votre administrateur.
                      </p>
                      <p style="margin:0 0 32px;color:#4a5568;font-size:15px;line-height:1.8;">
                        Vous trouverez ci-dessous vos <strong>identifiants de connexion</strong>.
                        Gardez ces informations en lieu sûr.
                      </p>
                    </td>
                  </tr>

                  <!-- CREDENTIALS CARD -->
                  <tr>
                    <td style="padding:0 48px 32px;">
                      <table width="100%" cellpadding="0" cellspacing="0"
                             style="background:linear-gradient(135deg,#f0f7ff,#e8f0fe);
                                    border-radius:14px;border:2px solid #bfdbfe;">
                        <tr>
                          <td style="padding:28px 32px;">
                            <p style="margin:0 0 20px;color:#1e40af;font-size:13px;font-weight:700;
                                       text-transform:uppercase;letter-spacing:1.5px;
                                       border-bottom:1px solid #bfdbfe;padding-bottom:12px;">
                              &#x1F511; Vos identifiants de connexion
                            </p>
                            <table width="100%" cellpadding="8" cellspacing="0">
                              <tr>
                                <td style="color:#64748b;font-size:13px;font-weight:600;
                                           text-transform:uppercase;letter-spacing:0.8px;width:38%;">
                                  Nom complet
                                </td>
                                <td style="color:#1e3a5f;font-size:15px;font-weight:600;">
                                  {nom_complet}
                                </td>
                              </tr>
                              <tr>
                                <td style="color:#64748b;font-size:13px;font-weight:600;
                                           text-transform:uppercase;letter-spacing:0.8px;">
                                  Identifiant
                                </td>
                                <td style="color:#1e3a5f;font-size:15px;font-weight:700;
                                           font-family:monospace;background:#dbeafe;
                                           padding:6px 12px;border-radius:6px;">
                                  {user.username}
                                </td>
                              </tr>
                              <tr>
                                <td style="color:#64748b;font-size:13px;font-weight:600;
                                           text-transform:uppercase;letter-spacing:0.8px;">
                                  Mot de passe
                                </td>
                                <td style="color:#1e3a5f;font-size:15px;font-weight:700;
                                           font-family:monospace;background:#fef3c7;
                                           padding:6px 12px;border-radius:6px;
                                           border:1px dashed #f59e0b;">
                                  {raw_password}
                                </td>
                              </tr>
                              <tr>
                                <td style="color:#64748b;font-size:13px;font-weight:600;
                                           text-transform:uppercase;letter-spacing:0.8px;">
                                  Rôle
                                </td>
                                <td>
                                  <span style="display:inline-block;background:#dcfce7;
                                               color:#166534;padding:4px 14px;
                                               border-radius:20px;font-size:13px;font-weight:700;">
                                    &#x2705; {role_display}
                                  </span>
                                </td>
                              </tr>
                            </table>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>

                  <!-- HOW TO LOGIN -->
                  <tr>
                    <td style="padding:0 48px 32px;">
                      <table width="100%" cellpadding="0" cellspacing="0"
                             style="background:#f8fafc;border-radius:14px;
                                    border:1px solid #e2e8f0;">
                        <tr>
                          <td style="padding:24px 28px;">
                            <p style="margin:0 0 16px;color:#1e3a5f;font-size:14px;font-weight:700;
                                       text-transform:uppercase;letter-spacing:1px;">
                              &#x1F4CB; Comment se connecter ?
                            </p>
                            <table cellpadding="0" cellspacing="0" width="100%">
                              <tr>
                                <td style="padding:6px 0;">
                                  <span style="display:inline-block;background:#2563eb;color:#fff;
                                               border-radius:50%;width:24px;height:24px;
                                               text-align:center;line-height:24px;
                                               font-size:12px;font-weight:700;
                                               margin-right:10px;">1</span>
                                  <span style="color:#374151;font-size:14px;">Ouvrez votre navigateur et allez sur</span>
                                  <a href="{frontend_url}"
                                     style="color:#2563eb;font-weight:600;text-decoration:none;
                                            margin-left:4px;">{frontend_url}</a>
                                </td>
                              </tr>
                              <tr>
                                <td style="padding:6px 0;">
                                  <span style="display:inline-block;background:#2563eb;color:#fff;
                                               border-radius:50%;width:24px;height:24px;
                                               text-align:center;line-height:24px;
                                               font-size:12px;font-weight:700;
                                               margin-right:10px;">2</span>
                                  <span style="color:#374151;font-size:14px;">Saisissez votre identifiant :
                                    <strong style="color:#1e3a5f;">{user.username}</strong>
                                  </span>
                                </td>
                              </tr>
                              <tr>
                                <td style="padding:6px 0;">
                                  <span style="display:inline-block;background:#2563eb;color:#fff;
                                               border-radius:50%;width:24px;height:24px;
                                               text-align:center;line-height:24px;
                                               font-size:12px;font-weight:700;
                                               margin-right:10px;">3</span>
                                  <span style="color:#374151;font-size:14px;">Saisissez votre mot de passe</span>
                                </td>
                              </tr>
                              <tr>
                                <td style="padding:6px 0;">
                                  <span style="display:inline-block;background:#2563eb;color:#fff;
                                               border-radius:50%;width:24px;height:24px;
                                               text-align:center;line-height:24px;
                                               font-size:12px;font-weight:700;
                                               margin-right:10px;">4</span>
                                  <span style="color:#374151;font-size:14px;">Cliquez sur <strong>"Se connecter"</strong></span>
                                </td>
                              </tr>
                            </table>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>

                  <!-- CTA BUTTON -->
                  <tr>
                    <td style="padding:0 48px 40px;text-align:center;">
                      <a href="{frontend_url}"
                         style="display:inline-block;
                                background:linear-gradient(135deg,#2563eb 0%,#1e40af 100%);
                                color:#ffffff;text-decoration:none;padding:16px 48px;
                                border-radius:10px;font-size:17px;font-weight:700;
                                letter-spacing:0.5px;
                                box-shadow:0 4px 15px rgba(37,99,235,0.4);">
                        &#x1F680; Accéder à ma plateforme
                      </a>
                      <p style="margin:16px 0 0;color:#94a3b8;font-size:12px;">
                        Nous vous recommandons de changer votre mot de passe après votre première connexion.
                      </p>
                    </td>
                  </tr>

                  <!-- WARNING -->
                  <tr>
                    <td style="padding:0 48px 32px;">
                      <table width="100%" cellpadding="0" cellspacing="0"
                             style="background:#fffbeb;border-radius:10px;
                                    border-left:4px solid #f59e0b;">
                        <tr>
                          <td style="padding:16px 20px;">
                            <p style="margin:0;color:#92400e;font-size:13px;line-height:1.6;">
                              <strong>&#x26A0; Sécurité :</strong> Ne partagez jamais vos identifiants
                              avec qui que ce soit. Si vous n'avez pas demandé ce compte,
                              contactez immédiatement votre administrateur.
                            </p>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>

                  <!-- FOOTER -->
                  <tr>
                    <td style="background:#f1f5f9;border-top:1px solid #e2e8f0;
                               padding:24px 48px;text-align:center;border-radius:0 0 20px 20px;">
                      <p style="margin:0 0 4px;color:#64748b;font-size:13px;font-weight:600;">
                        &#x23F1; TRACKTIME &mdash; Système de gestion du temps de travail
                      </p>
                      <p style="margin:0;color:#94a3b8;font-size:12px;">
                        Cet email a été envoyé automatiquement, merci de ne pas y répondre.
                      </p>
                    </td>
                  </tr>

                </table>
              </td>
            </tr>
          </table>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        print(f"[OK] Email de bienvenue envoyé à {user.email}")

    except Exception as e:
        print(f"[WARN] Échec envoi email de bienvenue à {user.email}: {e}")


# Vues d'authentification
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Inscription d'un nouvel utilisateur"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        # Capturer le mot de passe en clair AVANT le hashage
        raw_password = serializer.validated_data.get('password')
        user = serializer.save()
        # Envoi de l'email de bienvenue avec identifiants en arrière-plan
        if user.email:
            thread = threading.Thread(
                target=send_welcome_email,
                args=(user, raw_password),
                daemon=True
            )
            thread.start()
        return Response({
            'message': 'Utilisateur créé avec succès. Un email avec vos identifiants a été envoyé.',
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Connexion d'un utilisateur"""
    print("=" * 80)
    print("LOGIN REQUEST RECEIVED!")
    print("Request data:", request.data)
    print("Headers:", dict(request.headers))
    print("=" * 80)
    
    serializer = CustomTokenObtainPairSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Rafraîchir le token JWT"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Le token de rafraîchissement est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        return Response({
            'access': str(token.access_token)
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': 'Token de rafraîchissement invalide'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Obtenir le profil de l'utilisateur connecté"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Mettre à jour le profil utilisateur"""
    serializer = UserProfileSerializer(
        request.user, 
        data=request.data, 
        partial=request.method == 'PATCH'
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Changer le mot de passe"""
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({
            'message': 'Mot de passe changé avec succès'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Demander une réinitialisation de mot de passe"""
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        users = User.objects.filter(email=email)
        
        # Ici vous pourriez envoyer un email avec un token de réinitialisation
        # Pour l'instant, nous retournons juste un message de succès
        
        return Response({
            'message': 'Si cet email existe, un lien de réinitialisation a été envoyé'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Déconnexion"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({
            'message': 'Déconnexion réussie'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Erreur lors de la déconnexion'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions(request):
    """Obtenir les permissions de l'utilisateur connecté"""
    user = request.user
    permissions = {
        'can_create_permission': user.role == 'employe',
        'can_approve_permission': user.role in ['rh', 'admin'],
        'can_generate_bulletin': user.role in ['rh', 'admin'],
        'can_delete_bulletin': user.role == 'admin' or user.is_staff or user.is_superuser,
        'can_manage_users': user.is_staff or user.is_superuser,
        'can_view_all_permissions': user.role in ['rh', 'admin'],
        'can_view_all_bulletins': user.role in ['rh', 'admin'],
        'role': user.role,
        'is_admin': user.is_staff or user.is_superuser,
    }
    return Response(permissions, status=status.HTTP_200_OK)
