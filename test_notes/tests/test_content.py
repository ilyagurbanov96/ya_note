from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from notes.models import Note
from notes.forms import NoteForm

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
        cls.url = reverse('notes:list')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Просто текст.',
            slug='1996',
            author=cls.author
        )

    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.url)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    def test_note_not_in_list_for_another_user(self):
        response = self.reader_client.get(self.url)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)

    def test_create_note_page_contains_form(self):
        url = reverse('notes:add')
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_note_page_contains_form(self):
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
