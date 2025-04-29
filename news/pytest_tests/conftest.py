import pytest
from datetime import datetime
from django.test.client import Client
from news.models import News, Comment
from django.contrib.auth import get_user_model


@pytest.fixture
def user_model():
    """Фикстура возвращает модель пользователя."""
    return get_user_model()


@pytest.fixture
def author(user_model):
    """Создает пользователя-автора."""
    return user_model.objects.create_user(
        username='Автор',
        password='testpass123'
    )


@pytest.fixture
def not_author(user_model):
    """Создает пользователя, который не является автором."""
    return user_model.objects.create_user(
        username='Не автор',
        password='testpass123'
    )


@pytest.fixture
def author_client(author):
    """Клиент с авторизованным автором."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Клиент с авторизованным не-автором."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def anonymous_client():
    """Анонимный клиент."""
    return Client()


@pytest.fixture
def news():
    """Создает тестовую новость."""
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости',
        date=datetime.today()
    )


@pytest.fixture
def comment(author, news):
    """Создает тестовый комментарий."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Тестовый комментарий'
    )


@pytest.fixture
def another_comment(not_author, news):
    """Создает комментарий от другого пользователя."""
    return Comment.objects.create(
        news=news,
        author=not_author,
        text='Чужой комментарий'
    )