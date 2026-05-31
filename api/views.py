from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Client, Project, Task, Notification
from .serializers import (
    RegisterSerializer, UserSerializer,
    ClientSerializer, ProjectSerializer, ProjectListSerializer,
    TaskSerializer, NotificationSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class ClientListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientSerializer

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClientSerializer

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ProjectListCreateView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        qs = Project.objects.filter(owner=self.request.user).select_related('client')
        status_filter = self.request.query_params.get('status')
        client_filter = self.request.query_params.get('client')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if client_filter:
            qs = qs.filter(client_id=client_filter)
        return qs

    def perform_create(self, serializer):
        client = get_object_or_404(
            Client, id=serializer.validated_data['client'].id, owner=self.request.user
        )
        serializer.save(owner=self.request.user, client=client)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectSerializer
        return ProjectListSerializer

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        project = get_object_or_404(
            Project, id=self.kwargs['project_id'], owner=self.request.user
        )
        qs = project.tasks.all()
        status_filter = self.request.query_params.get('status')
        priority_filter = self.request.query_params.get('priority')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if priority_filter:
            qs = qs.filter(priority=priority_filter)
        return qs

    def perform_create(self, serializer):
        project = get_object_or_404(
            Project, id=self.kwargs['project_id'], owner=self.request.user
        )
        serializer.save(project=project)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        unread_only = self.request.query_params.get('unread')
        if unread_only == 'true':
            qs = qs.filter(is_read=False)
        return qs


@api_view(['POST'])
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return Response({'status': 'marked as read'})


@api_view(['POST'])
def mark_all_notifications_read(request):
    count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'marked_read': count})