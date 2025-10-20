import hashlib
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import StringRecord
from .serializers import StringRecordSerializer


class StringAPIView(APIView):
    """
    Handles:
      - POST /strings/  → Create/Analyze string
      - GET /strings/<str:string_value>/ → Retrieve single string
      - DELETE /strings/<str:string_value>/ → Delete string
      - GET /strings/?query_params → Filter all strings
    """

    def get(self, request, string_value=None):
        """
        Handles:
        - GET /strings/ → Get all with optional query filters
        - GET /strings/<string_value>/ → Get one
        """
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

        # Otherwise: list all strings with optional filters
        queryset = StringRecord.objects.all()
        params = request.query_params

        try:
            if "is_palindrome" in params:
                val = params["is_palindrome"].lower()
                queryset = queryset.filter(is_palindrome=(val == "true"))
            if "min_length" in params:
                queryset = queryset.filter(length__gte=int(params["min_length"]))
            if "max_length" in params:
                queryset = queryset.filter(length__lte=int(params["max_length"]))
            if "word_count" in params:
                queryset = queryset.filter(word_count=int(params["word_count"]))
            if "contains_character" in params:
                queryset = queryset.filter(value__icontains=params["contains_character"])
        except ValueError:
            return Response(
                {"error": "Invalid query parameter types."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StringRecordSerializer(queryset, many=True)
        filters = {k: v for k, v in params.items() if v}
        return Response(
            {
                "data": serializer.data,
                "count": queryset.count(),
                "filters_applied": filters,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """
        Handles POST /strings/ → Analyze and create a new string record
        """
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

        # Compute properties
        properties = {
            "length": len(value),
            "is_palindrome": value.lower() == value[::-1].lower(),
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
        """
        Handles DELETE /strings/<string_value>/ → Delete a string record
        """
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

        query = query.lower()
        filters = {}

        # Simple NLP heuristic
        if "palindromic" in query or "palindrome" in query:
            filters["is_palindrome"] = True
        if "single word" in query or "one word" in query:
            filters["word_count"] = 1
        if match := re.search(r"longer than (\d+)", query):
            filters["min_length"] = int(match.group(1)) + 1
        if match := re.search(r"shorter than (\d+)", query):
            filters["max_length"] = int(match.group(1)) - 1
        if match := re.search(r"letter ([a-z])", query):
            filters["contains_character"] = match.group(1)

        if not filters:
            return Response(
                {"error": "Unable to parse natural language query."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = StringRecord.objects.all()
        if "is_palindrome" in filters:
            queryset = queryset.filter(is_palindrome=filters["is_palindrome"])
        if "word_count" in filters:
            queryset = queryset.filter(word_count=filters["word_count"])
        if "min_length" in filters:
            queryset = queryset.filter(length__gte=filters["min_length"])
        if "max_length" in filters:
            queryset = queryset.filter(length__lte=filters["max_length"])
        if "contains_character" in filters:
            queryset = queryset.filter(value__icontains=filters["contains_character"])

        serializer = StringRecordSerializer(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "count": queryset.count(),
                "interpreted_query": {
                    "original": query,
                    "parsed_filters": filters,
                },
            },
            status=status.HTTP_200_OK,
        )
