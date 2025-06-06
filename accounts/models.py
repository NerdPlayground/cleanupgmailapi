from django.db import models

class Account(models.Model):
    user_id=models.CharField(max_length=255)
    credentials=models.JSONField()
