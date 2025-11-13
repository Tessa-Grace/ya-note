from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.note = Note.objects.create(title='Заголовок', text='Текст')
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        # От имени одного пользователя создаём комментарий к новости:
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Текст комментария'
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.notes.id,)),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('news:edit', 'news:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.comment.id,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('news:edit', 'news:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.comment.id,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse

# from notes.models import Note

# User = get_user_model()


# class TestRoutes(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         cls.author = User.objects.create_user(
#             username='author',
#             password='password123'
#         )
#         cls.reader = User.objects.create_user(
#             username='reader',
#             password='password123'
#         )
#         cls.note = Note.objects.create(
#             title='Test Note',
#             text='Test content',
#             author=cls.author
#         )

#     def test_home_page_available_to_anonymous(self):
#         """Главная страница доступна анонимному пользователю."""
#         url = reverse('notes:home')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_note_detail_available_to_anonymous(self):
#         """Страница отдельной заметки доступна анонимному пользователю."""
#         url = reverse('notes:detail', kwargs={'slug': self.note.slug})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_edit_delete_pages_available_to_author(self):
#         """Страницы редактирования и удаления доступны автору заметки."""
#         self.client.force_login(self.author)

#         edit_url = reverse('notes:edit', kwargs={'slug': self.note.slug})
#         delete_url = reverse('notes:delete', kwargs={'slug': self.note.slug})

#         response_edit = self.client.get(edit_url)
#         response_delete = self.client.get(delete_url)

#         self.assertEqual(response_edit.status_code, 200)
#         self.assertEqual(response_delete.status_code, 200)

#     def test_edit_delete_redirect_anonymous_to_login(self):
#         """Аноним перенаправляется на логин при попытке редактирования/удаления."""
#         login_url = reverse('login')

#         edit_url = reverse('notes:edit', kwargs={'slug': self.note.slug})
#         delete_url = reverse('notes:delete', kwargs={'slug': self.note.slug})

#         response_edit = self.client.get(edit_url)
#         response_delete = self.client.get(delete_url)

#         self.assertRedirects(response_edit, f'{login_url}?next={edit_url}')
#         self.assertRedirects(response_delete, f'{login_url}?next={delete_url}')

#     def test_edit_delete_not_available_to_other_user(self):
#         """Чужой пользователь получает 404 при редактировании/удалении."""
#         self.client.force_login(self.reader)

#         edit_url = reverse('notes:edit', kwargs={'slug': self.note.slug})
#         delete_url = reverse('notes:delete', kwargs={'slug': self.note.slug})

#         response_edit = self.client.get(edit_url)
#         response_delete = self.client.get(delete_url)

#         self.assertEqual(response_edit.status_code, 404)
#         self.assertEqual(response_delete.status_code, 404)

#     def test_auth_pages_available_to_anonymous(self):
#         """Страницы регистрации, входа и выхода доступны анонимам."""
#         urls = [
#             reverse('login'),
#             reverse('logout'),
#         ]

#         for url in urls:
#             with self.subTest(url=url):
#                 response = self.client.get(url)
#                 self.assertEqual(response.status_code, 200)
