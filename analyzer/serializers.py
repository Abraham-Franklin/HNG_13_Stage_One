import hashlib
from rest_framework import serializers
from .models import StringRecord


class StringRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StringRecord
        fields = "__all__"

    def validate_value(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Value must be a string.")
        if not value.strip():
            raise serializers.ValidationError("Value cannot be empty or whitespace.")
        return value

    def create(self, validated_data):
        value = validated_data.get("value")

        # compute derived fields
        validated_data["length"] = len(value)
        validated_data["is_palindrome"] = value == value[::-1]
        validated_data["word_count"] = len(value.split())
        validated_data["unique_characters"] = len(set(value))
        validated_data["character_frequency_map"] = {c: value.count(c) for c in set(value)}
        validated_data["sha256_hash"] = hashlib.sha256(value.encode()).hexdigest()

        return super().create(validated_data)
