from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Habit(models.Model):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

    PERIODICITY_CHOICES = [
        (DAILY, "Ежедневно"),
        (WEEKLY, "Еженедельно"),
        (MONTHLY, "Ежемесячно"),
    ]

    STATUS_CHOICES = [
        ("Completed", "Завершенный"),
        ("Active", "Активный"),
        ("Overdue", "Просроченный"),
    ]

    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="habits",
        verbose_name="Пользователь",
    )

    place = models.CharField(max_length=255, verbose_name="Место выполнения")
    time = models.TimeField(verbose_name="Время выполнения")
    action = models.CharField(max_length=255, verbose_name="Действие")
    is_pleasant = models.BooleanField(
        default=False, verbose_name="Признак приятной привычки"
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        related_name="main_habits",
    )

    periodicity = models.CharField(
        max_length=10,
        choices=PERIODICITY_CHOICES,
        default=DAILY,
        verbose_name="Периодичность",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Active",
        verbose_name="Статус выполнения",
    )

    reward = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Вознаграждение"
    )
    duration = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        verbose_name="Время на выполнение (в секундах)",
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная привычка",
        help_text="Отметьте, чтобы привычку видели все пользователи",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Я буду {self.action} в {self.time} в {self.place}"

    def clean(self):
        # Проверка на одновременное заполнение полей
        if self.reward and self.related_habit:
            raise ValidationError(
                "Можно указать либо вознаграждение, либо связанную привычку, но не оба поля одновременно."
            )

        # Проверка, что связанная привычка является приятной
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна быть приятной.")

        # Проверка, что приятная привычка не имеет вознаграждения или связанной привычки
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError(
                "Приятная привычка не может иметь вознаграждения или связанной привычки."
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Вызов валидации перед сохранением
        super().save(*args, **kwargs)


# class HabitCompletion(models.Model):
#     habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
#     completion_date = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
#
#     class Meta:
#         ordering = ['-completion_date']
