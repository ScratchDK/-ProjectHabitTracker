import habits.views as views
from rest_framework.routers import DefaultRouter

app_name = "habits"

router = DefaultRouter()

router.register("habits", views.HabitViewSet, basename="habits")

urlpatterns = [] + router.urls
