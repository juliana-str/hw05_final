from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..forms import User


USER_USERNAME = 'Anonimus'


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USER_USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_templates_1(self):
        response = self.authorized_client.get('/auth/login/')
        self.assertTemplateUsed(response, 'users/login.html')

    def test_templates_2(self):
        response = self.authorized_client.get('/auth/password_change/')
        self.assertTemplateUsed(response, 'users/password_change_form.html')

    def test_templates_3(self):
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertTemplateUsed(response, 'users/password_change_done.html')

    def test_templates_4(self):
        response = self.authorized_client.get('/auth/password_reset/')
        self.assertTemplateUsed(response, 'users/password_reset_form.html')

    def test_templates_5(self):
        response = self.authorized_client.get('/auth/password_reset/done/')
        self.assertTemplateUsed(response, 'users/password_reset_done.html')

    def test_templates_6(self):
        response = self.authorized_client.get('/auth/reset/<uidb64>/<token>/')
        self.assertTemplateUsed(response, 'users/password_reset_confirm.html')

    def test_templates_7(self):
        response = self.authorized_client.get('/auth/reset/done/')
        self.assertTemplateUsed(response, 'users/password_reset_complete.html')

    def test_templates_8(self):
        response = self.authorized_client.get('/auth/signup/')
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_templates_9(self):
        response = self.authorized_client.get('/auth/logout/')
        self.assertTemplateUsed(response, 'users/logged_out.html')

    # Проверяем доступ для неавторизованного пользователя
    def test_urls_uses_correct_template_for_guest(self):
        template = 'users/signup.html'
        response = self.guest_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, template)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_correct_redirect_for_authorized_client(self):
        urls = (
            reverse('login'),
            reverse('logout'),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url_uses_correct_redirect(self):
        """Страница /password_change/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse(
            'password_change'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_url_uses_correct_redirect(self):
        """Страница /password_change/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse(
            'password_change_done'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_url_uses_correct_redirect(self):
        """Страница /password_reset/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_url_uses_correct_redirect(self):
        """Страница /password_reset/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
