from django.test import TestCase
from habits.tasks import send_daily_reminders, send_related_habits_notification
from users.models import CustomUser
from habits.models import Habit
from django.utils import timezone
from unittest.mock import patch


class TasksTestCase(TestCase):
    def setUp(self):
        self.user_with_chat = CustomUser.objects.create_user(
            username='withchat',
            email='withchat@example.com',
            password='testpass123',
            telegram_chat_id='12345'
        )

        self.user_without_chat = CustomUser.objects.create_user(
            username='nochat',
            email='nochat@example.com',
            password='testpass123'
        )

        # Создаем приятную привычку (для связанной)
        self.pleasant_habit = Habit.objects.create(
            user=self.user_with_chat,
            action='Приятная привычка',
            time=timezone.now().time(),
            place='Дом',
            duration=120,
            is_pleasant=True,
            status='Active'
        )

        # Создаем основную привычку
        self.main_habit = Habit.objects.create(
            user=self.user_with_chat,
            action='Основная привычка',
            time=timezone.now().time(),
            place='Дом',
            duration=120,
            status='Active',
            related_habit=self.pleasant_habit
        )

    @patch('habits.tasks.bot.send_message')
    def test_send_daily_reminders(self, mock_send):
        send_daily_reminders()
        self.assertTrue(mock_send.called)
        args, kwargs = mock_send.call_args
        self.assertIn('Основные привычки', kwargs['text'])
        self.assertEqual(kwargs['chat_id'], '12345')

        # Проверяем случай без chat_id
        self.user_with_chat.telegram_chat_id = None
        self.user_with_chat.save()
        mock_send.reset_mock()
        send_daily_reminders()
        self.assertFalse(mock_send.called)

    @patch('habits.tasks.bot.send_message')
    def test_send_related_habits_notification_with_related(self, mock_send):
        related_habit = Habit.objects.create(
            user=self.user_with_chat,
            action="Дом",
            place="Гостиная",
            duration=120,
            time="20:00",
            status="Active"
        )
        self.main_habit.main_habits.add(related_habit)

        self.user_with_chat.telegram_chat_id = "12345"
        self.user_with_chat.save()

        self.main_habit.refresh_from_db()

        send_related_habits_notification(self.main_habit.id, self.user_with_chat.id)

        self.assertTrue(mock_send.called)

        # Verify message content
        args, kwargs = mock_send.call_args
        self.assertIn('Основная привычка выполнена', kwargs['text'])
        self.assertIn('Дом', kwargs['text'])

    @patch('habits.tasks.bot.send_message')
    def test_send_related_habits_notification_with_reward(self, mock_send):
        # Устанавливаем вознаграждение вместо связанной привычки
        self.main_habit.related_habit = None
        self.main_habit.reward = 'Съесть апельсин'
        self.main_habit.save()

        send_related_habits_notification(self.main_habit.id, self.user_with_chat.id)
        self.assertTrue(mock_send.called)
        args, kwargs = mock_send.call_args
        self.assertIn('Съесть апельсин', kwargs['text'])

    @patch('habits.tasks.bot.send_message')
    def test_send_related_habits_notification_no_chat_id(self, mock_send):
        send_related_habits_notification(self.main_habit.id, self.user_without_chat.id)
        self.assertFalse(mock_send.called)

    @patch('habits.tasks.bot.send_message')
    def test_send_related_habits_notification_no_related_no_reward(self, mock_send):
        # Убираем и связанную привычку, и вознаграждение
        self.main_habit.related_habit = None
        self.main_habit.reward = ''
        self.main_habit.save()

        send_related_habits_notification(self.main_habit.id, self.user_with_chat.id)
        self.assertFalse(mock_send.called)
