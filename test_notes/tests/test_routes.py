from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


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
        cls.SLUG = (cls.notes.slug,)
        cls.HOME_URL = reverse('notes:home')
        cls.LOGIN_URL = reverse('users:login')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.SIGNUP_URL = reverse('users:signup')
        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.EDIT_URL = reverse('notes:edit', args=cls.SLUG)
        cls.SUCCESS_URL = reverse('notes:success')
        cls.DELETE_URL = reverse('notes:delete', args=cls.SLUG)
        cls.DETAIL_URL = reverse('notes:detail', args=cls.SLUG)

        cls.urls = (
            (cls.HOME_URL),
            (cls.LOGIN_URL),
            (cls.LOGOUT_URL),
            (cls.SIGNUP_URL),
            (cls.LIST_URL),
            (cls.ADD_URL),
            (cls.EDIT_URL),
            (cls.SUCCESS_URL),
            (cls.DELETE_URL),
            (cls.DETAIL_URL),
        )

    def test_availability_for_notes_author(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in self.urls:
                with self.subTest(user=user, url=url):
                    response = self.author_client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in (self.ADD_URL, self.LIST_URL, self.SUCCESS_URL):
                with self.subTest(user=user, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability(self):
        urls = (
            (self.HOME_URL),
            (self.LOGIN_URL),
            (self.LOGOUT_URL),
            (self.SIGNUP_URL),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_edit_and_detail_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in (self.EDIT_URL, self.DELETE_URL, self.DETAIL_URL):
                with self.subTest(user=user, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        for url in (self.EDIT_URL, self.DELETE_URL):
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_for_client(self):
        for url in (
            (self.LIST_URL), (self.SUCCESS_URL),
            (self.ADD_URL), (self.DELETE_URL),
            (self.EDIT_URL), (self.DETAIL_URL)
        ):
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
