from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client, Project, Task, Notification


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ClientSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    project_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ('id', 'owner', 'name', 'email', 'company', 'notes',
                  'project_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')

    def get_project_count(self, obj):
        return obj.projects.count()


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    remaining_days = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = ('id', 'project', 'title', 'description', 'status',
                  'priority', 'due_date', 'is_overdue', 'remaining_days',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'project', 'created_at', 'updated_at')


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    total_tasks = serializers.ReadOnlyField()
    completed_tasks = serializers.ReadOnlyField()
    progress = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = ('id', 'owner', 'client', 'title', 'description', 'status',
                  'deadline', 'budget', 'tasks', 'total_tasks',
                  'completed_tasks', 'progress', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')


class ProjectListSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    total_tasks = serializers.ReadOnlyField()
    progress = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = ('id', 'owner', 'client', 'title', 'status', 'deadline',
                  'budget', 'total_tasks', 'progress', 'created_at')
        read_only_fields = ('id', 'owner', 'created_at')


class NotificationSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'task', 'task_title', 'notification_type',
                  'message', 'is_read', 'created_at')
        read_only_fields = ('id', 'created_at')