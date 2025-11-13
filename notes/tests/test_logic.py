from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='password123'
        )
        cls.reader = User.objects.create_user(
            username='reader',
            password='password123'
        )
        cls.note = Note.objects.create(
            title='Test Note',
            text='Test content',
            slug='test-note',
            author=cls.author
        )

    def test_anonymous_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(url, {
            'title': 'New Note',
            'text': 'New Content',
            'slug': 'new-note'
        })
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)
        # Должен быть редирект на логин
        self.assertEqual(response.status_code, 302)

    def test_authenticated_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(url, {
            'title': 'New Note',
            'text': 'New Content',
            'slug': 'new-note'
        })
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        # Должен быть редирект на страницу успеха
        self.assertRedirects(response, reverse('notes:success'))

    def test_duplicate_slug_validation(self):
        """Проверка валидации уникальности slug."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, {
            'title': 'Different Title',
            'text': 'Different Content',
            'slug': 'test-note'  # Такой же slug как у существующей заметки
        })
        # Форма должна вернуть ошибку
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            'form',
            'slug',
            'test-note - такой slug уже существует, придумайте уникальное значение!'
        )

    def test_author_can_edit_own_note(self):
        """Автор может редактировать свою заметку."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', kwargs={'slug': self.note.slug})
        response = self.client.post(url, {
            'title': 'Updated Title',
            'text': 'Updated Content',
            'slug': 'updated-note'
        })
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Title')
        self.assertRedirects(response, reverse('notes:success'))

    def test_author_can_delete_own_note(self):
        """Автор может удалить свою заметку."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        url = reverse('notes:delete', kwargs={'slug': self.note.slug})
        response = self.client.post(url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)
        self.assertRedirects(response, reverse('notes:success'))

    def test_user_cannot_edit_others_note(self):
        """Пользователь не может редактировать чужую заметку."""
        self.client.force_login(self.reader)
        url = reverse('notes:edit', kwargs={'slug': self.note.slug})
        response = self.client.post(url, {
            'title': 'Hacked Title',
            'text': 'Hacked Content',
            'slug': 'hacked-note'
        })
        # Должен получить 404
        self.assertEqual(response.status_code, 404)
        # Заметка не должна измениться
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Test Note')

    def test_user_cannot_delete_others_note(self):
        """Пользователь не может удалить чужую заметку."""
        self.client.force_login(self.reader)
        notes_count_before = Note.objects.count()
        url = reverse('notes:delete', kwargs={'slug': self.note.slug})
        response = self.client.post(url)
        notes_count_after = Note.objects.count()
        # Должен получить 404
        self.assertEqual(response.status_code, 404)
        # Количество заметок не должно измениться
        self.assertEqual(notes_count_after, notes_count_before)
