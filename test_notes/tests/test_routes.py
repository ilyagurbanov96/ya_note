from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

SLUG = ('1996',)
HOME_URL = reverse('notes:home')
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
EDIT_URL = reverse('notes:edit', args=SLUG)
DELETE_URL = reverse('notes:delete', args=SLUG)
DETAIL_URL = reverse('notes:detail', args=SLUG)
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='1996',
            author=cls.author,
        )

        cls.urls = (
            (HOME_URL),
            (LIST_URL),
            (ADD_URL),
            (SUCCESS_URL),
            (EDIT_URL),
            (DELETE_URL),
            (DETAIL_URL),
            (LOGIN_URL),
            (LOGOUT_URL),
            (SIGNUP_URL),
        )

    def test_availability_for_notes_author(self):
        """Тест что все урлы доступны автору."""
        for url in self.urls:
            with self.subTest(url=url):
                response = self.author_client.get(url[0])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_auth_client(self):
        """Тест что все урлы, кроме редактирования,
        удаления и детали доступны не автору,
        и проверка 404 на эти 3 урла.
        """
        url_404 = (
            (EDIT_URL),
            (DELETE_URL),
            (DETAIL_URL),
        )
        for url in self.urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                if url in url_404:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.OK)

    def test_availability_for_notes_client(self):
        """Тест что все урлы кроме шести доступны анониму,
        а с тех шести - редирект на авторизацию
        """
        url_not_redirect = (
            (HOME_URL),
            (LOGIN_URL),
            (LOGOUT_URL),
            (SIGNUP_URL),
        )
        for url in self.urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                if url in url_not_redirect:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    redirect_url = f'{LOGIN_URL}?next={url}'
                    self.assertRedirects(response, redirect_url)
