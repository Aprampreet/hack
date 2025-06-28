from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
class Entry(models.Model):
    MOODS = [
        ('happy', '😊 Happy & Joyful'),
        ('sad', '😢 Sad & Melancholy'),
        ('excited', '🎉 Excited & Energetic'),
        ('calm', '😌 Calm & Peaceful'),
        ('anxious', '😰 Anxious & Worried'),
        ('grateful', '🙏 Grateful & Thankful'),
        ('reflective', '🤔 Reflective & Thoughtful'),
        ('creative', '🎨 Creative & Inspired'),
        ('nostalgic', '💭 Nostalgic & Reminiscent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    memory_title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_watered = models.DateTimeField(default=timezone.now)
    is_dead = models.BooleanField(default=False)  # ✅ BooleanField
    mood = models.CharField(max_length=20, choices=MOODS, default='happy')

    def check_decay(self):
        if not self.is_dead and timezone.now() - self.last_watered > timezone.timedelta(minutes=3):
            self.is_dead = True
            self.save()

    def __str__(self):
        return self.content[:30]

    @property
    def decay_percentage(self):
        if self.is_dead:
            return 0

        now = timezone.now()
        time_passed = now - self.last_watered
        total_life = timedelta(hours=24)
        decay = min(time_passed / total_life, 1.0)
        vitality = (1.0 - decay) * 100
        return round(vitality)
