import pytest
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth.models import User
from rest_framework import status
from api.models import Client, Project, Task, Notification

@pytest.mark.django_db
class TestTaskModel:

    def test_task_is_overdue(self, db, project):
        task = Task.objects.create(
            project=project,
            title='Overdue Task',
            due_date=date.today() - timedelta(days=1),
            status='todo'
        )
        assert task.is_overdue is True

    def test_task_not_overdue(self, db, project):
        task = Task.objects.create(
            project=project,
            title='Future Task',
            due_date=date.today() + timedelta(days=5),
            status='todo'
        )
        assert task.is_overdue is False

    def test_done_task_not_overdue(self, db, project):
        task = Task.objects.create(
            project=project,
            title='Done Task',
            due_date=date.today() - timedelta(days=1),
            status='done'
        )
        assert task.is_overdue is False

    def test_remaining_days(self, db, project):
        task = Task.objects.create(
            project=project,
            title='Future Task',
            due_date=date.today() + timedelta(days=10),
            status='todo'
        )
        assert task.remaining_days == 10

    def test_no_due_date_remaining_days(self, db, project):
        task = Task.objects.create(
            project=project,
            title='No Due Date Task',
            status='todo'
        )
        assert task.remaining_days is None


class TestProjectModel:

    def test_project_progress_no_tasks(self, db, project):
        assert project.progress == 0



