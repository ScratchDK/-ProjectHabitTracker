from celery import shared_task
from telegram import Bot
from django.conf import settings
from users.models import CustomUser
from habits.models import Habit

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


@shared_task(bind=True)
def send_daily_reminders(self):

    users = CustomUser.objects.filter(telegram_chat_id__isnull=False)

    for user in users:
        chat_id = user.telegram_chat_id
        if not chat_id:
            continue

        main_habits = user.habits.filter(status="Active", related_habit__isnull=True)

        if main_habits.exists():
            message_lines = [
                "🔔 Основные привычки на сегодня:",
                "Следующие привычки требуют выполнения:",
            ]

            for habit in main_habits:
                message_lines.append(
                    f"- {habit.action} в {habit.time.strftime('%H:%M')} ({habit.place})"
                )

            bot.send_message(chat_id=chat_id, text="\n".join(message_lines))


@shared_task
def send_related_habits_notification(habit_id, user_id):
    habit = Habit.objects.get(id=habit_id)
    user = CustomUser.objects.get(id=user_id)

    if not user.telegram_chat_id:
        return

    related_habits = habit.main_habits.filter(status="Active")

    message_lines = [
        "🎉 Основная привычка выполнена!",
        "Теперь можно вознаградить себя и выполнить:",
    ]

    if related_habits.exists():
        for h in related_habits:
            message_lines.append(
                f"- {h.action} в {h.time.strftime('%H:%M')} ({h.place})"
            )
    elif habit.reward:
        message_lines.append(habit.reward)
    else:
        return

    bot.send_message(chat_id=user.telegram_chat_id, text="\n".join(message_lines))
