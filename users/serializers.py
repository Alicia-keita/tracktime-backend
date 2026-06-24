from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer User (CRUD Admin)
    - password write_only
    - s\u00e9curisation
    - compatibilit\u00e9 IoT RFID
    - envoi email de bienvenue HTML
    """

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'role',
            'service',
            'telephone',
            'badge_rfid',
            'face_id',
            'date_joined'
        ]

        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'service': {'required': False},
            'telephone': {'required': False},
            'badge_rfid': {'required': False},
            'face_id': {'required': False},
            'date_joined': {'required': False},
        }

    # \U0001f525 Nettoyage des r\u00f4les (corrig\u00e9 + simplifi\u00e9)
    def validate_role(self, value):
        allowed_roles = ['admin', 'rh', 'employe']
        if value not in allowed_roles:
            raise serializers.ValidationError("R\u00f4le invalide")
        return value

    # \U0001f525 Hash password cr\u00e9ation + envoi email HTML de bienvenue
    def create(self, validated_data):
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings

        raw_password = validated_data.get('password')
        email = validated_data.get('email')
        username = validated_data.get('username', '')
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        role = validated_data.get('role', 'employe')
        service = validated_data.get('service') or 'Non sp\u00e9cifi\u00e9'
        telephone = validated_data.get('telephone') or 'Non sp\u00e9cifi\u00e9'

        if raw_password:
            validated_data['password'] = make_password(raw_password)

        user = super().create(validated_data)

        if email and raw_password:
            role_display = {
                'admin': 'Administrateur',
                'rh': 'Ressources Humaines (RH)',
                'employe': 'Employ\u00e9'
            }.get(role, role)

            full_name = f"{first_name} {last_name}".strip() or username
            login_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')

            subject = "\U0001f44b Bienvenue sur TRACKTIME \u2014 Vos informations de connexion"

            # ── Version texte brut (fallback)
            text_body = f"""Bonjour {full_name},

Votre compte a \u00e9t\u00e9 cr\u00e9\u00e9 avec succ\u00e8s sur la plateforme TRACKTIME.

D\u00e9tails de votre profil :
  Nom complet    : {full_name}
  E-mail         : {email}
  Identifiant    : {username}
  R\u00f4le           : {role_display}
  Service        : {service}
  T\u00e9l\u00e9phone      : {telephone}

Informations de connexion :
  Identifiant    : {username}
  Mot de passe   : {raw_password}

Connectez-vous ici : {login_url}

Veuillez modifier votre mot de passe lors de votre premi\u00e8re connexion.

Cordialement,
L'\u00e9quipe TRACKTIME"""

            # ── Version HTML (riche)
            html_body = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Bienvenue sur TRACKTIME</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6fb;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6fb;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(59,36,110,0.12);">

          <!-- HEADER -->
          <tr>
            <td style="background:linear-gradient(135deg,#3B246E 0%,#5A3D9E 100%);padding:40px 40px 30px;text-align:center;">
              <div style="display:inline-block;background:rgba(255,255,255,0.15);border-radius:12px;padding:10px 24px;margin-bottom:20px;">
                <span style="color:#fff;font-size:22px;font-weight:800;letter-spacing:2px;">&#9200; TRACKTIME</span>
              </div>
              <h1 style="color:#ffffff;font-size:26px;font-weight:700;margin:0 0 8px;">
                Bienvenue, {first_name}&nbsp;!
              </h1>
              <p style="color:rgba(255,255,255,0.80);font-size:15px;margin:0;">
                Votre compte a \u00e9t\u00e9 cr\u00e9\u00e9 avec succ\u00e8s
              </p>
            </td>
          </tr>

          <!-- BODY -->
          <tr>
            <td style="background:#ffffff;padding:36px 40px;">

              <p style="color:#374151;font-size:15px;line-height:1.7;margin:0 0 24px;">
                Bonjour <strong>{full_name}</strong>,<br/>
                Vous avez \u00e9t\u00e9 ajout\u00e9(e) \u00e0 la plateforme <strong>TRACKTIME</strong> en tant que
                <span style="display:inline-block;background:#EDE9FA;color:#3B246E;font-size:12px;font-weight:700;padding:2px 10px;border-radius:20px;vertical-align:middle;">{role_display}</span>.
              </p>

              <!-- Carte profil -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#F9F7FF;border:1px solid #E8E2F8;border-radius:12px;padding:0;margin-bottom:24px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <p style="margin:0 0 14px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#7C6BB3;">
                      &#128100; Votre profil
                    </p>
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="padding:6px 0;color:#6B7280;font-size:13px;width:130px;">Nom complet</td>
                        <td style="padding:6px 0;color:#111827;font-size:14px;font-weight:600;">{full_name}</td>
                      </tr>
                      <tr style="background:rgba(59,36,110,0.03);">
                        <td style="padding:6px 0;color:#6B7280;font-size:13px;">E-mail</td>
                        <td style="padding:6px 0;color:#111827;font-size:14px;font-weight:600;">{email}</td>
                      </tr>
                      <tr>
                        <td style="padding:6px 0;color:#6B7280;font-size:13px;">R\u00f4le</td>
                        <td style="padding:6px 0;color:#111827;font-size:14px;font-weight:600;">{role_display}</td>
                      </tr>
                      <tr style="background:rgba(59,36,110,0.03);">
                        <td style="padding:6px 0;color:#6B7280;font-size:13px;">Service</td>
                        <td style="padding:6px 0;color:#111827;font-size:14px;font-weight:600;">{service}</td>
                      </tr>
                      <tr>
                        <td style="padding:6px 0;color:#6B7280;font-size:13px;">T\u00e9l\u00e9phone</td>
                        <td style="padding:6px 0;color:#111827;font-size:14px;font-weight:600;">{telephone}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- Encadr\u00e9 identifiants -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#FFF8F0;border:2px solid #FEC89A;border-radius:12px;margin-bottom:28px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <p style="margin:0 0 14px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#B45309;">
                      &#128274; Vos identifiants de connexion
                    </p>
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="padding:8px 0;color:#6B7280;font-size:13px;width:130px;">Identifiant</td>
                        <td style="padding:8px 0;">
                          <span style="background:#fff;border:1px solid #E5E7EB;border-radius:6px;padding:5px 14px;font-size:14px;font-weight:700;color:#111827;font-family:monospace;">{username}</span>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:8px 0;color:#6B7280;font-size:13px;">Mot de passe</td>
                        <td style="padding:8px 0;">
                          <span style="background:#fff;border:1px solid #E5E7EB;border-radius:6px;padding:5px 14px;font-size:14px;font-weight:700;color:#111827;font-family:monospace;">{raw_password}</span>
                        </td>
                      </tr>
                    </table>
                    <p style="margin:14px 0 0;font-size:12px;color:#92400E;">
                      &#9888;&#65039; Veuillez modifier votre mot de passe d\u00e8s votre premi\u00e8re connexion.
                    </p>
                  </td>
                </tr>
              </table>

              <!-- Bouton de connexion -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding-bottom:24px;">
                    <a href="{login_url}"
                       style="display:inline-block;background:linear-gradient(135deg,#3B246E,#5A3D9E);color:#ffffff;text-decoration:none;font-size:15px;font-weight:700;padding:14px 40px;border-radius:10px;letter-spacing:0.5px;">
                      &#128073; Se connecter \u00e0 TRACKTIME
                    </a>
                  </td>
                </tr>
              </table>

              <p style="color:#9CA3AF;font-size:13px;text-align:center;margin:0;">
                Si vous n\u2019\u00eates pas concern\u00e9(e) par cet e-mail, ignorez-le simplement.
              </p>

            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="background:#F3F0FA;padding:20px 40px;text-align:center;border-top:1px solid #E8E2F8;">
              <p style="margin:0 0 4px;color:#7C6BB3;font-size:13px;font-weight:700;">&#9200; TRACKTIME &mdash; Syst\u00e8me de gestion des pr\u00e9sences</p>
              <p style="margin:0;color:#9CA3AF;font-size:12px;">Cet e-mail a \u00e9t\u00e9 envoy\u00e9 automatiquement, merci de ne pas y r\u00e9pondre.</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'TRACKTIME <noreply@tracktime.com>'),
                    to=[email],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                print(f"[TRACKTIME] \u2705 Email de bienvenue envoy\u00e9 \u00e0 : {email}")
            except Exception as e:
                print(f"[TRACKTIME] \u26a0\ufe0f Erreur envoi email \u00e0 {email} : {e}")

        return user

    # \U0001f525 Hash password update
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)