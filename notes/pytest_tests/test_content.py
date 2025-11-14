import pytest
from pytest_lazy_fixtures import lf
from django.urls import reverse
from django.test import Client

from notes.forms import NoteForm
from notes.models import Note


@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (lf('author_client'), True),
        (lf('not_author_client'), False),
    )
)
def test_notes_list_for_different_users(
    note, parametrized_client, note_in_list
):
    url = reverse('notes:list')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    assert (note in object_list) is note_in_list


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:add', None),
        ('notes:edit', lf('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], NoteForm)


def test_note_object_in_context_for_author(author_client, note):
    url = reverse('notes:list')
    response = author_client.get(url)
    assert note in response.context['object_list']


def test_note_object_not_in_context_for_other_user(not_author_client, note):
    url = reverse('notes:list')
    response = not_author_client.get(url)
    assert note not in response.context['object_list']


def test_note_detail_page_context(author_client, note):
    url = reverse('notes:detail', args=(note.slug,))
    response = author_client.get(url)
    assert response.context['note'] == note


def test_home_page_available(author_client):
    url = reverse('notes:home')
    response = author_client.get(url)
    assert response.status_code == 200


def test_success_page_available(author_client):
    url = reverse('notes:success')
    response = author_client.get(url)
    assert response.status_code == 200


def test_delete_page_contains_note(author_client, note):
    url = reverse('notes:delete', args=(note.slug,))
    response = author_client.get(url)
    assert response.context['note'] == note


def test_notes_sorted_from_new_to_old(author):
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
    client = Client()
    client.force_login(author)
    url = reverse('notes:list')
    response = client.get(url)
    notes_list = list(response.context['object_list'])
    assert note1 in notes_list
    assert note2 in notes_list
    assert len(notes_list) == 2


def test_notes_count_limit(author):
    notes = [
        Note(
            title=f'Заметка {i}',
            text=f'Текст заметки {i}',
            slug=f'note-{i}',
            author=author
        )
        for i in range(11)
    ]
    Note.objects.bulk_create(notes)
    client = Client()
    client.force_login(author)
    url = reverse('notes:list')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) <= 11
