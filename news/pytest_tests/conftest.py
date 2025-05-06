import pytest
from datetime import datetime
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def home_url():
    """Фикстура для URL главной страницы с новостями."""
    return reverse('news:home')


@pytest.fixture
def login_url():
    """Фикстура для URL login."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Фикстура для URL logout."""
    return reverse('users:logout')



@pytest.fixture
def signup_url():
    """Фикстура для URL успешной регистрации."""
    return reverse('users:signup')


@pytest.fixture
def detail_url(news):
    """Фикстура для URL страницы новости с подставленным `pk`."""
    return reverse('news:detail', kwargs={'pk': news.pk})


@pytest.fixture
def comment_edit_url(comment):
    """Фикстура для URL редактирования комментария."""
    return reverse('news:edit', kwargs={'pk': comment.pk})


@pytest.fixture
def comment_delete_url(comment):
    """Фикстура для URL удаления комментария."""
    return reverse('news:delete', kwargs={'pk': comment.pk})


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Автоматически предоставляет доступ к БД для всех тестов."""


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