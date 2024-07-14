from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
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
            text='Просто текст.',
            slug='1996',
            author=cls.author
        )
        cls.SLUG = (cls.notes.slug,)
        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.EDIT_URL = reverse('notes:edit', args=cls.SLUG)

    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        note_object = Note.objects.get()
        self.assertEqual(object_list.count(), 1)
        self.assertEqual(note_object.title, self.notes.title)
        self.assertEqual(note_object.text, self.notes.text)
        self.assertEqual(note_object.slug, self.notes.slug)
        self.assertEqual(note_object.author, self.notes.author)

    def test_note_not_in_list_for_another_user(self):
        response = self.reader_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 0)

    def test_create_and_edit_note_page_contains_form(self):
        urls = (
            self.ADD_URL,
            self.EDIT_URL
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.author_client.get(self.ADD_URL)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
