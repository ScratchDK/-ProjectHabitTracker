from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    CITY_CHOICES = [
        ("Pyatigorsk", "Пятигорск"),
        ('Moscow', 'Москва'),
        ('Saint Petersburg', 'Санкт-Петербург'),
        ('Omsk', 'Омск'),
    ]

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='users/images/', blank=True, null=True)
    city = models.CharField(max_length=255, choices=CITY_CHOICES, null=True, blank=True, verbose_name="Город")
    # Токен для потверждения почты при регестрации и для восстановления пароля
    confirmation_token = models.CharField(max_length=32, blank=True, null=True)
    telegram_chat_id = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Телеграм chat-id", help_text="Укажите телеграм chat-id")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    def __str__(self):
        return self.email
