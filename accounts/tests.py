from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.translations import TRANSLATIONS


class ProfileLanguageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='Pass12345!',
            first_name='Test',
            last_name='User',
        )
        self.client.force_login(self.user)

    def test_profile_language_change_persists_to_dashboard(self):
        response = self.client.post(reverse('profile'), {
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '',
            'currency': 'INR',
            'language': 'hi',
            'theme': 'light',
            'date_of_birth': '',
            'address': '',
        })

        self.assertRedirects(response, reverse('profile'))

        self.user.refresh_from_db()
        self.assertEqual(self.user.language, 'hi')

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.context['current_lang'], 'hi')
        self.assertEqual(response.context['t'], TRANSLATIONS['hi'])
