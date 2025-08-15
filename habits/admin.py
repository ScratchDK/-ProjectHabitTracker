from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "place",
        "time",
        "periodicity",
        "status",
        "is_public",
        "created_at",
    )
    list_filter = ("periodicity", "status", "is_pleasant", "is_public", "created_at")
    search_fields = ("action", "place", "user__email", "user__username")
    list_editable = ("status", "is_public")
    list_per_page = 20
    ordering = ("-created_at",)
    fieldsets = (
        ("Основная информация", {"fields": ("user", "place", "time", "action")}),
        (
            "Характеристики привычки",
            {
                "fields": (
                    "is_pleasant",
                    "related_habit",
                    "periodicity",
                    "status",
                    "duration",
                )
            },
        ),
        (
            "Дополнительно",
            {"fields": ("reward", "is_public"), "classes": ("collapse",)},
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("created_at",)
        return ()
