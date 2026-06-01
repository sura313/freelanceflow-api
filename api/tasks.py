import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Task, Notification

logger = logging.getLogger(__name__)


@shared_task
def check_overdue_tasks():
    """
    Runs every 30 minutes.
    Finds all tasks that are past due_date, not done,
    and haven't been notified yet — then sends an email
    and creates a Notification record.
    """
    today = timezone.now().date()

    overdue_tasks = Task.objects.filter(
        due_date__lt=today,
        status__in=['todo', 'in_progress', 'review'],
        overdue_notified=False
    ).select_related('project__owner')

    notified_count = 0

    for task in overdue_tasks:
        owner = task.project.owner

        # Create a Notification record in the database
        Notification.objects.create(
            user=owner,
            task=task,
            notification_type='overdue',
            message=f'Task "{task.title}" in project "{task.project.title}" is overdue. It was due on {task.due_date}.'
        )

        # Send email to the owner
        send_mail(
            subject=f'[FreelanceFlow] Overdue Task: {task.title}',
            message=f'''
Hi {owner.username},

Your task "{task.title}" in project "{task.project.title}" is overdue.
It was due on {task.due_date}.

Please update the task status or extend the deadline.

— FreelanceFlow
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner.email],
            fail_silently=True,
        )

        # Mark as notified so we don't send again
        task.overdue_notified = True
        task.save(update_fields=['overdue_notified'])

        notified_count += 1
        logger.info(f'Overdue notification sent for task: {task.title}')

    logger.info(f'check_overdue_tasks completed: {notified_count} tasks notified')
    return f'{notified_count} tasks notified'


@shared_task
def send_deadline_reminder():
    """
    Finds tasks due in the next 24 hours and sends a reminder email.
    """
    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)

    upcoming_tasks = Task.objects.filter(
        due_date=tomorrow,
        status__in=['todo', 'in_progress', 'review'],
    ).select_related('project__owner')

    for task in upcoming_tasks:
        owner = task.project.owner

        Notification.objects.create(
            user=owner,
            task=task,
            notification_type='deadline',
            message=f'Task "{task.title}" is due tomorrow ({task.due_date}).'
        )

        send_mail(
            subject=f'[FreelanceFlow] Due Tomorrow: {task.title}',
            message=f'''
Hi {owner.username},

Just a reminder that your task "{task.title}" in project "{task.project.title}" is due tomorrow ({task.due_date}).

— FreelanceFlow
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner.email],
            fail_silently=True,
        )

    return f'{upcoming_tasks.count()} reminders sent'