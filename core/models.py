from django.db import models
from django.contrib.auth.models import User

class MatchResult(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    opponent = models.CharField(max_length=150)
    player_score = models.IntegerField()
    opponent_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} {self.player_score} - {self.opponent_score} {self.opponent} ({self.created_at.strftime('%Y-%m-%d')})"

