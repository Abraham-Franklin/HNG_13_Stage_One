from django.db import models

class StringRecord(models.Model):
    value = models.CharField(max_length=255)
    length = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    sha256_hash = models.CharField(max_length=64)
    character_frequency_map = models.JSONField()
    is_palindrome = models.BooleanField()

    def __str__(self):
        return self.value
