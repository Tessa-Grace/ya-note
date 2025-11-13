# test_content.py
import pytest

from django.urls import reverse

from notes.forms import NoteForm


@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, note_in_list',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False),
    )
)
# Используем фикстуру заметки и параметры из декоратора:
def test_notes_list_for_different_users(
    note, parametrized_client, note_in_list
):
    url = reverse('notes:list')
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    # Проверяем истинность утверждения "заметка есть в списке":
    assert (note in object_list) is note_in_list


# test_content.py
...
@pytest.mark.parametrize(
    # В качестве параметров передаём name и args для reverse.
    'name, args',
    (
        # Для тестирования страницы создания заметки 
        # никакие дополнительные аргументы для reverse() не нужны.
        ('notes:add', None),
        # Для тестирования страницы редактирования заметки нужен slug заметки.
        ('notes:edit', pytest.lazy_fixture('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    # Формируем URL.
    url = reverse(name, args=args)
    # Запрашиваем нужную страницу:
    response = author_client.get(url)
    # Проверяем, есть ли объект формы в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], NoteForm)

def test_note_object_in_context_for_author(author_client, note):
    """
    Проверяем, что отдельная заметка передаётся на страницу со списком заметок
    в списке object_list для автора.
    """
    url = reverse('notes:list')
    response = author_client.get(url)
    # Проверяем, что заметка есть в object_list для автора
    assert note in response.context['object_list']


def test_note_object_not_in_context_for_other_user(not_author_client, note):
    """
    Проверяем, что заметка не попадает в список для другого пользователя.
    """
    url = reverse('notes:list')
    response = not_author_client.get(url)
    # Проверяем, что заметки нет в object_list для другого пользователя
    assert note not in response.context['object_list']


def test_note_detail_page_context(author_client, note):
    """
    Проверяем, что на странице детального просмотра передаётся правильная заметка.
    """
    url = reverse('notes:detail', args=(note.slug,))
    response = author_client.get(url)
    # Проверяем, что в контексте есть объект note и это именно та заметка
    assert response.context['note'] == note


def test_home_page_available(author_client):
    """
    Проверяем, что главная страница доступна.
    """
    url = reverse('notes:home')
    response = author_client.get(url)
    assert response.status_code == 200


def test_success_page_available(author_client):
    """
    Проверяем, что страница успеха доступна.
    """
    url = reverse('notes:success')
    response = author_client.get(url)
    assert response.status_code == 200


def test_delete_page_contains_note(author_client, note):
    """
    Проверяем, что на странице удаления передаётся правильная заметка.
    """
    url = reverse('notes:delete', args=(note.slug,))
    response = author_client.get(url)
    assert response.context['note'] == note


def test_notes_sorted_from_new_to_old(author):
    """
    Проверяем, что заметки отсортированы от самой свежей к самой старой.
    """
    # Создаём несколько заметок с разными датами создания
    note1 = Note.objects.create(
        title='Первая заметка',
        text='Текст первой заметки',
        slug='first-note',
        author=author
    )
    
    note2 = Note.objects.create(
        title='Вторая заметка',
        text='Текст второй заметки', 
        slug='second-note',
        author=author
    )
    
    note3 = Note.objects.create(
        title='Третья заметка',
        text='Текст третьей заметки',
        slug='third-note',
        author=author
    )
    
    # Создаём клиента и авторизуем автора
    client = Client()
    client.force_login(author)
    
    url = reverse('notes:list')
    response = client.get(url)
    notes_list = list(response.context['object_list'])
    
    # Проверяем, что заметки отсортированы от новых к старым
    # (последняя созданная заметка должна быть первой в списке)
    assert notes_list[0] == note3  # Самая новая
    assert notes_list[1] == note2  # Средняя
    assert notes_list[2] == note1  # Самая старая


def test_notes_count_limit(author):
    """
    Проверяем, что на странице списка отображается не более 10 заметок.
    """
    # Создаём больше 10 заметок
    for i in range(15):
        Note.objects.create(
            title=f'Заметка {i}',
            text=f'Текст заметки {i}',
            slug=f'note-{i}',
            author=author
        )
    
    client = Client()
    client.force_login(author)
    
    url = reverse('notes:list')
    response = client.get(url)
    notes_list = response.context['object_list']
    assert len(notes_list) <= 10