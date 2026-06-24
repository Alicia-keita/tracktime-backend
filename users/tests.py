from django.test import TestCase
from django.core import mail
from core.user_management import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserEmailTest(TestCase):
    def test_welcome_email_sent_on_user_creation(self):
        data = {
            'username': 'test_email_user',
            'password': 'TestPassword123',
            'email': 'test@example.com',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'role': 'employe',
            'service': 'IT',
            'telephone': '0123456789'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        
        # Verify that the email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Création de votre compte - TRACKTIME")
        self.assertIn("Jean Dupont", email.body)
        self.assertIn("test_email_user", email.body)
        self.assertIn("TestPassword123", email.body)
        self.assertIn("IT", email.body)
        self.assertIn("http://localhost:5173/", email.body)
        self.assertEqual(email.to, ['test@example.com'])
