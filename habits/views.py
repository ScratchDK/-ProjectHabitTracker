from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.paginators import MyPagination
from habits.permissions import IsOwner
from habits.tasks import send_related_habits_notification


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    pagination_class = MyPagination
    permission_classes = [permissions.IsAuthenticated]  # Чтение для всех, запись для авторизованных

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Habit.objects.filter(Q(user=self.request.user) | Q(is_public=True))
        return Habit.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwner()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]  # По умолчанию для других действий

    @action(detail=True, methods=['post'])
    def perform(self, request, pk=None):
        habit = self.get_object()

        if habit.user != request.user:
            return Response(
                {"detail": "Вы не можете отмечать выполнение чужих привычек"},
                status=status.HTTP_403_FORBIDDEN
            )

        if habit.status == "Completed":
            return Response(
                {"detail": "Эта привычка уже выполнена"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем статус
        habit.status = "Completed"
        habit.save()

        send_related_habits_notification.delay(habit.id, request.user.id)

        return Response(
            {
                "status": "success",
                "message": "Привычка отмечена как выполненная",
                "habit_id": habit.id,
                "action": habit.action,
                "has_related": habit.main_habits.filter(status="Active").exists()
            },
            status=status.HTTP_200_OK
        )
