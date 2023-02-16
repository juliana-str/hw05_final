from django.test import TestCase, Client

from ..forms import User


class CreationFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_client = Client()
        cls.user = User.objects.create_user(
            first_name='first_name',
            last_name='last_name',
            username='Anonimus',
            email='test@test.ru'
        )
        cls.authorized_client.force_login(cls.user)

    def test_create_form_user(self):
        self.assertEqual(self.user.first_name, 'first_name')
        self.assertEqual(self.user.last_name, 'last_name')
        self.assertEqual(self.user.username, 'Anonimus')
        self.assertEqual(self.user.email, 'test@test.ru')
