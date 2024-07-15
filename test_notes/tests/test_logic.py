from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


SLUG = ('1996',)
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
EDIT_URL = reverse('notes:edit', args=SLUG)
DELETE_URL = reverse('notes:delete', args=SLUG)


class TestNoteCreation(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст'
    SLUG = '1996'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='1996',
            author=cls.author,
        )
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        self.client.post(ADD_URL, data=self.form_data)
        self.assertEqual(notes_count, Note.objects.count())

    def test_user_can_create_note(self):
        """Залогиненый пользователь может создать заметку."""
        Note.objects.all().delete()
        notes_count = Note.objects.count()
        response = self.auth_client.post(ADD_URL, data=self.form_data)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)
        self.assertRedirects(response, SUCCESS_URL)
        notes_count_new = Note.objects.count()
        self.assertEqual(notes_count_new, notes_count + 1)

    def test_slug_is_unique(self):
        """Невозможно создать две заметки с одинаковым slug."""
        notes_count = Note.objects.count()
        self.auth_client.post(ADD_URL, data=self.form_data)
        self.assertEqual(notes_count, Note.objects.count())

    def test_empty_slug(self):
        """Если при создании заметки не заполнен slug,
        то он формируется автоматически,
        с помощью функции pytils.translit.slugify.
        """
        Note.objects.all().delete()
        notes_count = Note.objects.count()
        self.form_data.pop('slug')
        response = self.auth_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(notes_count + 1, Note.objects.count())


class TestNoteEditDelete(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст'
    SLUG = '1996'
    TITLE_NOW = 'Новый заголовок'
    TEXT_NOW = 'Новый текст'
    SLUG_NOW = '19961'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )
        cls.form_note_old = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }
        cls.form_note_now = {

            'title': cls.TITLE_NOW,
            'text': cls.TEXT_NOW,
            'slug': cls.SLUG_NOW,
        }

    def test_author_can_delete_note(self):
        """Автор может удалятьл свои заметки"""
        notes_count = Note.objects.count()
        response = self.author_client.delete(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(notes_count - 1, Note.objects.count())

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалять чужие заметки"""
        notes_count = Note.objects.count()
        response = self.reader_client.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count, Note.objects.count())

    def test_author_can_edit_note(self):
        """Автор может редактировать свои заметки"""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.author_client.post(
            EDIT_URL, data=self.form_note_now
        )
        self.assertRedirects(response, SUCCESS_URL)
        note_new = Note.objects.get()
        self.assertEqual(note_new.title, self.form_note_now['title'])
        self.assertEqual(note_new.text, self.form_note_now['text'])
        self.assertEqual(note_new.slug, self.form_note_now['slug'])
        self.assertEqual(note_new.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки"""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.reader_client.post(
            EDIT_URL, data=self.form_note_now
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get()
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.slug, note.slug)
        self.assertEqual(self.note.author, note.author)
