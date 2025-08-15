from django.core.management.base import BaseCommand
from habits.models import Habit
from django.core.management import call_command


class Command(BaseCommand):
    help = "Добавляет тестовые привычки"

    def handle(self, *args, **kwargs):
        self.stdout.write("Очистка существующих данных...")

        # Удаляем все привычки
        Habit.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Старые данные успешно удалены!"))

        call_command("loaddata", "habits_fixture.json")
        self.stdout.write(self.style.SUCCESS("Данные успешно загружены!"))
