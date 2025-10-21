import hashlib
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import StringRecord
from .serializers import StringRecordSerializer


def normalize_string(s: str) -> str:
    """Normalize string for comparison."""
    return s.strip().lower()


def is_palindrome(s: str) -> bool:
    """Check if string is a palindrome ignoring spaces and case."""
    normalized = normalize_string(s).replace(" ", "")
    return normalized == normalized[::-1]


def parse_nl_filters(query: str) -> dict:
    """Parse a natural language query into multiple filters."""
    filters = {}
    q = query.lower()

    if "palindrome" in q or "palindromic" in q:
        filters["is_palindrome"] = True
    if "single word" in q or "one word" in q:
        filters["word_count"] = 1
    if match := re.search(r"longer than (\d+)", q):
        filters["min_length"] = int(match.group(1)) + 1
    if match := re.search(r"shorter than (\d+)", q):
        filters["max_length"] = int(match.group(1)) - 1
    if match := re.search(r"letter ([a-z])", q):
        filters["contains_character"] = match.group(1)
    
    return filters


def apply_filters(queryset, filters: dict):
    """Apply multiple filters to a queryset."""
    for key, value in filters.items():
        if key == "is_palindrome":
            queryset = [obj for obj in queryset if is_palindrome(obj.value)]
        elif key == "word_count":
            queryset = [obj for obj in queryset if len(obj.value.split()) == value]
        elif key == "min_length":
            queryset = [obj for obj in queryset if len(obj.value) >= value]
        elif key == "max_length":
            queryset = [obj for obj in queryset if len(obj.value) <= value]
        elif key == "contains_character":
            queryset = [obj for obj in queryset if value in normalize_string(obj.value)]
    return queryset


class StringAPIView(APIView):
    """
    Handles:
      - POST /strings/  → Create/Analyze string
      - GET /strings/<str:string_value>/ → Retrieve single string
      - DELETE /strings/<str:string_value>/ → Delete string
      - GET /strings/?query_params → Filter all strings
    """

    def get(self, request, string_value=None):
        if string_value:
            # Retrieve a specific string
            sha256_hash = hashlib.sha256(string_value.encode()).hexdigest()
            obj = get_object_or_404(StringRecord, sha256_hash=sha256_hash)
            data = {
                "id": obj.sha256_hash,
                "value": obj.value,
                "properties": {
                    "length": obj.length,
                    "is_palindrome": obj.is_palindrome,
                    "unique_characters": obj.unique_characters,
                    "word_count": obj.word_count,
                    "sha256_hash": obj.sha256_hash,
                    "character_frequency_map": obj.character_frequency_map,
                },
                "created_at": obj.created_at,
            }
            return Response(data, status=status.HTTP_200_OK)

        # List all strings with optional query filters
        queryset = list(StringRecord.objects.all())
        params = request.query_params
        filters = {}

        try:
            if "is_palindrome" in params:
                filters["is_palindrome"] = params["is_palindrome"].lower() == "true"
            if "min_length" in params:
                filters["min_length"] = int(params["min_length"])
            if "max_length" in params:
                filters["max_length"] = int(params["max_length"])
            if "word_count" in params:
                filters["word_count"] = int(params["word_count"])
            if "contains_character" in params:
                filters["contains_character"] = params["contains_character"].lower()
        except ValueError:
            return Response(
                {"error": "Invalid query parameter types."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = apply_filters(queryset, filters)

        serializer = StringRecordSerializer(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "count": len(queryset),
                "filters_applied": filters,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        value = request.data.get("value")
        if value is None:
            return Response(
                {"error": 'Missing "value" field.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(value, str):
            return Response(
                {"error": '"value" must be a string.'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        value = value.strip()
        sha256_hash = hashlib.sha256(value.encode()).hexdigest()

        if StringRecord.objects.filter(sha256_hash=sha256_hash).exists():
            return Response(
                {"error": "String already exists in the system."},
                status=status.HTTP_409_CONFLICT,
            )

        properties = {
            "length": len(value),
            "is_palindrome": is_palindrome(value),
            "unique_characters": len(set(value)),
            "word_count": len(value.split()),
            "sha256_hash": sha256_hash,
            "character_frequency_map": {c: value.count(c) for c in set(value)},
        }

        record = StringRecord.objects.create(value=value, **properties)
        response_data = {
            "id": record.sha256_hash,
            "value": record.value,
            "properties": properties,
            "created_at": record.created_at,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def delete(self, request, string_value=None):
        if not string_value:
            return Response(
                {"error": "String value required for deletion."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sha256_hash = hashlib.sha256(string_value.encode()).hexdigest()
        obj = StringRecord.objects.filter(sha256_hash=sha256_hash).first()
        if not obj:
            return Response(
                {"error": "String does not exist in the system."},
                status=status.HTTP_404_NOT_FOUND,
            )

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StringNaturalLanguageFilterAPIView(APIView):
    """
    Handles GET /strings/filter-by-natural-language/?query=...
    """

    def get(self, request):
        query = request.query_params.get("query", "")
        if not query:
            return Response(
                {"error": "Missing 'query' parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filters = parse_nl_filters(query)
        if not filters:
            return Response(
                {"error": "Unable to parse natural language query."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = list(StringRecord.objects.all())
        queryset = apply_filters(queryset, filters)

        serializer = StringRecordSerializer(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "count": len(queryset),
                "interpreted_query": {
                    "original": query,
                    "parsed_filters": filters,
                },
            },
            status=status.HTTP_200_OK,
        )
