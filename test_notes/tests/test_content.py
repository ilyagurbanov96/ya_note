from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

SLUG = ('1996',)
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
EDIT_URL = reverse('notes:edit', args=SLUG)


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

    def test_note_in_list_for_author(self):
        """Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']
        note_object = Note.objects.get()
        self.assertEqual(object_list.count(), 1)
        self.assertEqual(note_object.title, self.notes.title)
        self.assertEqual(note_object.text, self.notes.text)
        self.assertEqual(note_object.slug, self.notes.slug)
        self.assertEqual(note_object.author, self.notes.author)

    def test_note_not_in_list_for_another_user(self):
        """В список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        response = self.reader_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 0)

    def test_create_and_edit_note_page_contains_form(self):
        """На страницы создания и редактирования
        заметки передаются формы
        """
        urls = (
            ADD_URL,
            EDIT_URL
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.author_client.get(ADD_URL)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
