import pytest
from django.contrib.auth.models import User
from api.models import Client, Project, Task


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@test.com',
        password='testpass123'
    )


@pytest.fixture
def second_user(db):
    return User.objects.create_user(
        username='otheruser',
        email='other@test.com',
        password='testpass123'
    )


@pytest.fixture
def client_obj(db, user):
    return Client.objects.create(
        owner=user,
        name='Test Client',
        email='client@test.com',
        company='Test Company'
    )


@pytest.fixture
def project(db, user, client_obj):
    return Project.objects.create(
        owner=user,
        client=client_obj,
        title='Test Project',
        status='active'
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client