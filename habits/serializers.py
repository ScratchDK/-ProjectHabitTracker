from rest_framework import serializers
from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"

    def validate(self, data):
        reward = data.get('reward')
        related_habit = data.get('related_habit')

        if reward and related_habit:
            raise serializers.ValidationError(
                "Можно указать либо вознаграждение, либо связанную привычку, но не оба"
            )

        if not reward and not related_habit:
            raise serializers.ValidationError(
                "Необходимо указать либо вознаграждение, либо связанную привычку"
            )

        return data

    def create(self, validated_data):
        return super().create(validated_data)
