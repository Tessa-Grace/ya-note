from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesListPage(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметок')
        cls.reader = User.objects.create(username='Читатель')

        notes_author = [
            Note(
                title=f'Заметка автора {index}',
                text='Текст заметки.',
                slug=f'note-author-{index}',
                author=cls.author
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(notes_author)

        notes_reader = [
            Note(
                title=f'Заметка читателя {index}',
                text='Текст заметки.',
                slug=f'note-reader-{index}',
                author=cls.reader
            )
            for index in range(3)
        ]
        Note.objects.bulk_create(notes_reader)

    def test_notes_in_list_context(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, 5)
        for note in object_list:
            self.assertEqual(note.author, self.author)

    def test_user_notes_separation(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list_author = response.context['object_list']

        self.assertEqual(object_list_author.count(), 5)
        for note in object_list_author:
            self.assertEqual(note.author, self.author)

        self.client.force_login(self.reader)
        response = self.client.get(self.LIST_URL)
        object_list_reader = response.context['object_list']
        self.assertEqual(object_list_reader.count(), 3)
        for note in object_list_reader:
            self.assertEqual(note.author, self.reader)

        author_notes_titles = [note.title for note in object_list_author]
        reader_notes_titles = [note.title for note in object_list_reader]
        for title in author_notes_titles:
            self.assertNotIn(title, reader_notes_titles)


class TestNoteCreateEditPages(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст тестовой заметки.',
            slug='test-note',
            author=cls.author
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_anonymous_client_has_no_form_on_add_page(self):
        response = self.client.get(self.add_url)
        self.assertNotEqual(response.status_code, 200)

    def test_authorized_client_has_form_on_add_page(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_anonymous_client_has_no_form_on_edit_page(self):
        response = self.client.get(self.edit_url)
        self.assertNotEqual(response.status_code, 200)

    def test_authorized_client_has_form_on_edit_page(self):
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
        form = response.context['form']
        self.assertEqual(form.instance.title, self.note.title)
        self.assertEqual(form.instance.text, self.note.text)
        self.assertEqual(form.instance.slug, self.note.slug)

    def test_other_user_has_no_access_to_edit_page(self):
        other_user = User.objects.create(username='Другой пользователь')
        self.client.force_login(other_user)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 404)