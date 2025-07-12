from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from habits.models import Habit
from users.models import CustomUser
from django.utils import timezone


class HabitViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            telegram_chat_id="12345",
        )

        self.other_user = CustomUser.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Создаем приятную привычку
        self.pleasant_habit = Habit.objects.create(
            user=self.other_user,
            action="Приятная привычка",
            time=timezone.now().time(),
            place="Парк",
            duration=60,
            is_pleasant=True,
            is_public=True,
            status="Active",
        )

        # Публичная привычка
        self.habit_public = Habit.objects.create(
            user=self.other_user,
            action="Публичная привычка",
            time=timezone.now().time(),
            place="Дом",
            duration=120,
            is_public=True,
            status="Active",
            related_habit=self.pleasant_habit,
        )

        # Личная привычка
        self.habit_private = Habit.objects.create(
            user=self.user,
            action="Личная привычка",
            time=timezone.now().time(),
            place="Работа",
            duration=90,
            is_public=False,
            status="Active",
            reward="Чашка кофе",
        )

    def test_list_habits_authenticated(self):
        url = reverse("habits:habits-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_habits_unauthenticated(self):
        self.client.logout()
        url = reverse("habits:habits-public")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        public_habits = [h for h in response.data["results"] if h["is_public"]]
        self.assertEqual(len(response.data["results"]), len(public_habits))

        # Конкретное количество зависит от ваших тестовых данных
        # В вашем случае ожидается 1 публичная привычка
        self.assertEqual(len(response.data["results"]), 2)

    def test_create_habit(self):
        url = reverse("habits:habits-list")
        data = {
            "action": "Новая привычка",
            "time": "12:00:00",
            "place": "Офис",
            "duration": 60,
            "is_public": True,
            "reward": "Перерыв",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 4)

    def test_update_own_habit(self):
        url = reverse("habits:habits-detail", args=[self.habit_private.id])
        data = {"action": "Обновленная привычка", "reward": "Награда"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit_private.refresh_from_db()
        self.assertEqual(self.habit_private.action, "Обновленная привычка")

    def test_update_others_habit(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("habits:habits-detail", args=[self.habit_private.id])
        data = {"action": "Попытка изменить"}
        response = self.client.patch(url, data, format="json")
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_perform_habit_success(self):
        url = reverse("habits:habits-perform", args=[self.habit_private.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit_private.refresh_from_db()
        self.assertEqual(self.habit_private.status, "Completed")

    def test_perform_habit_already_completed(self):
        self.habit_private.status = "Completed"
        self.habit_private.save()
        url = reverse("habits:habits-perform", args=[self.habit_private.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Эта привычка уже выполнена")

    def test_perform_others_habit(self):
        url = reverse("habits:habits-perform", args=[self.habit_public.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "Вы не можете отмечать выполнение чужих привычек"
        )

    def test_habit_validation(self):
        url = reverse("habits:habits-list")
        invalid_data = {
            "action": "Невалидная привычка",
            "time": "12:00:00",
            "place": "Офис",
            "duration": 60,
            "reward": "Награда",
            "related_habit": self.pleasant_habit.id,
        }

        response = self.client.post(url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Можно указать либо вознаграждение, либо связанную привычку, но не оба",
            str(response.data),
        )
