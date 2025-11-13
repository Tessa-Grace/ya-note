from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='password123'
        )
        # Создаем больше 10 заметок для теста пагинации
        for i in range(15):
            Note.objects.create(
                title=f'Note {i}',
                text=f'Content {i}',
                author=cls.author
            )
        cls.notes = Note.objects.all()

    def test_notes_list_max_10_notes(self):
        """На странице списка заметок не более 10 заметок."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 10)

    def test_notes_sorted_by_creation_date(self):
        """Заметки отсортированы от самой свежей к самой старой."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']

        # Проверяем, что заметки идут в порядке убывания id (предполагая, что id увеличиваются)
        notes_ids = [note.id for note in object_list]
        self.assertEqual(notes_ids, sorted(notes_ids, reverse=True))

    def test_comment_form_available_to_authenticated(self):
        """Форма добавления заметки доступна авторизованному пользователю."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
