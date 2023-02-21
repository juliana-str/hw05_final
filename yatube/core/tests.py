from django.test import TestCase
from http import HTTPStatus

class WiewTestClass(TestCase):
    def test_error_page_404(self):
      response = self.client.get('/unexisting_page/')
      self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
      self.assertTemplateUsed(response, 'core/404.html')
