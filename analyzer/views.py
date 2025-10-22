# import hashlib
# import re
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.shortcuts import get_object_or_404
# from .models import StringRecord
# from .serializers import StringRecordSerializer


# def normalize_string(s: str) -> str:
#     """Normalize string for comparison."""
#     return s.strip().lower()


# def is_palindrome(s: str) -> bool:
#     """Check if string is a palindrome ignoring spaces and case."""
#     normalized = normalize_string(s).replace(" ", "")
#     return normalized == normalized[::-1]


# def parse_nl_filters(query: str) -> dict:
#     """Parse a natural language query into multiple filters."""
#     filters = {}
#     q = query.lower()

#     if "palindrome" in q or "palindromic" in q:
#         filters["is_palindrome"] = True
#     if "single word" in q or "one word" in q:
#         filters["word_count"] = 1
#     if match := re.search(r"longer than (\d+)", q):
#         filters["min_length"] = int(match.group(1)) + 1
#     if match := re.search(r"shorter than (\d+)", q):
#         filters["max_length"] = int(match.group(1)) - 1
#     if match := re.search(r"letter ([a-z])", q):
#         filters["contains_character"] = match.group(1)
    
#     return filters


# def apply_filters(queryset, filters: dict):
#     """Apply multiple filters to a queryset."""
#     for key, value in filters.items():
#         if key == "is_palindrome":
#             queryset = [obj for obj in queryset if is_palindrome(obj.value)]
#         elif key == "word_count":
#             queryset = [obj for obj in queryset if len(obj.value.split()) == value]
#         elif key == "min_length":
#             queryset = [obj for obj in queryset if len(obj.value) >= value]
#         elif key == "max_length":
#             queryset = [obj for obj in queryset if len(obj.value) <= value]
#         elif key == "contains_character":
#             queryset = [obj for obj in queryset if value in normalize_string(obj.value)]
#     return queryset


# class StringAPIView(APIView):
#     """
#     Handles:
#       - POST /strings/  → Create/Analyze string
#       - GET /strings/<str:string_value>/ → Retrieve single string
#       - DELETE /strings/<str:string_value>/ → Delete string
#       - GET /strings/?query_params → Filter all strings
#     """

#     def get(self, request, string_value=None):
#         if string_value:
#             # Retrieve a specific string
#             sha256_hash = hashlib.sha256(string_value.encode()).hexdigest()
#             obj = get_object_or_404(StringRecord, sha256_hash=sha256_hash)
#             data = {
#                 "id": obj.sha256_hash,
#                 "value": obj.value,
#                 "properties": {
#                     "length": obj.length,
#                     "is_palindrome": obj.is_palindrome,
#                     "unique_characters": obj.unique_characters,
#                     "word_count": obj.word_count,
#                     "sha256_hash": obj.sha256_hash,
#                     "character_frequency_map": obj.character_frequency_map,
#                 },
#                 "created_at": obj.created_at,
#             }
#             return Response(data, status=status.HTTP_200_OK)

#         # List all strings with optional query filters
#         queryset = list(StringRecord.objects.all())
#         params = request.query_params
#         filters = {}

#         try:
#             if "is_palindrome" in params:
#                 filters["is_palindrome"] = params["is_palindrome"].lower() == "true"
#             if "min_length" in params:
#                 filters["min_length"] = int(params["min_length"])
#             if "max_length" in params:
#                 filters["max_length"] = int(params["max_length"])
#             if "word_count" in params:
#                 filters["word_count"] = int(params["word_count"])
#             if "contains_character" in params:
#                 filters["contains_character"] = params["contains_character"].lower()
#         except ValueError:
#             return Response(
#                 {"error": "Invalid query parameter types."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         queryset = apply_filters(queryset, filters)

#         serializer = StringRecordSerializer(queryset, many=True)
#         return Response(
#             {
#                 "data": serializer.data,
#                 "count": len(queryset),
#                 "filters_applied": filters,
#             },
#             status=status.HTTP_200_OK,
#         )

#     def post(self, request):
#         value = request.data.get("value")
#         if value is None:
#             return Response(
#                 {"error": 'Missing "value" field.'},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         if not isinstance(value, str):
#             return Response(
#                 {"error": '"value" must be a string.'},
#                 status=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             )

#         value = value.strip()
#         sha256_hash = hashlib.sha256(value.encode()).hexdigest()

#         if StringRecord.objects.filter(sha256_hash=sha256_hash).exists():
#             return Response(
#                 {"error": "String already exists in the system."},
#                 status=status.HTTP_409_CONFLICT,
#             )

#         properties = {
#             "length": len(value),
#             "is_palindrome": is_palindrome(value),
#             "unique_characters": len(set(value)),
#             "word_count": len(value.split()),
#             "sha256_hash": sha256_hash,
#             "character_frequency_map": {c: value.count(c) for c in set(value)},
#         }

#         record = StringRecord.objects.create(value=value, **properties)
#         response_data = {
#             "id": record.sha256_hash,
#             "value": record.value,
#             "properties": properties,
#             "created_at": record.created_at,
#         }
#         return Response(response_data, status=status.HTTP_201_CREATED)

#     def delete(self, request, string_value=None):
#         if not string_value:
#             return Response(
#                 {"error": "String value required for deletion."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         sha256_hash = hashlib.sha256(string_value.encode()).hexdigest()
#         obj = StringRecord.objects.filter(sha256_hash=sha256_hash).first()
#         if not obj:
#             return Response(
#                 {"error": "String does not exist in the system."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         obj.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class StringNaturalLanguageFilterAPIView(APIView):
#     """
#     Handles GET /strings/filter-by-natural-language/?query=...
#     """

#     def get(self, request):
#         query = request.query_params.get("query", "")
#         if not query:
#             return Response(
#                 {"error": "Missing 'query' parameter."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         filters = parse_nl_filters(query)
#         if not filters:
#             return Response(
#                 {"error": "Unable to parse natural language query."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         queryset = list(StringRecord.objects.all())
#         queryset = apply_filters(queryset, filters)

#         serializer = StringRecordSerializer(queryset, many=True)
#         return Response(
#             {
#                 "data": serializer.data,
#                 "count": len(queryset),
#                 "interpreted_query": {
#                     "original": query,
#                     "parsed_filters": filters,
#                 },
#             },
#             status=status.HTTP_200_OK,
#         )













































# ==============================================
# views.py (Corrected and Improved)
# ==============================================

import hashlib
import logging
import re
from typing import Dict, Any

from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import StringRecord
from .serializers import StringRecordSerializer

logger = logging.getLogger(__name__)

# ==============================================================
# ---------- Utility Functions ---------------------------------
# ==============================================================

def normalize_for_compare(s: str) -> str:
    """Strip and lowercase for safe comparisons."""
    return s.strip().lower()


def normalized_alphanumeric(s: str) -> str:
    """Remove whitespace and lowercase for palindrome checks."""
    return normalize_for_compare(s).replace(" ", "")


def is_palindrome(s: str) -> bool:
    """Return True if a string is palindrome (ignoring spaces/case)."""
    n = normalized_alphanumeric(s)
    return n == n[::-1]


def compute_properties(value: str) -> Dict[str, Any]:
    """Compute all string properties exactly as the spec expects."""
    v_stripped = value.strip()
    v_lower = v_stripped.lower()

    char_map = {}
    for ch in v_lower:
        char_map[ch] = char_map.get(ch, 0) + 1

    sha = hashlib.sha256(v_stripped.encode()).hexdigest()

    return {
        "length": len(v_stripped),
        "is_palindrome": is_palindrome(v_stripped),
        "unique_characters": len(set(v_lower)),
        "word_count": len(v_stripped.split()),
        "sha256_hash": sha,
        "character_frequency_map": char_map,
    }


def make_response_payload(record: StringRecord) -> Dict[str, Any]:
    """Return payload matching the spec for a single record."""
    properties = {
        "length": record.length,
        "is_palindrome": record.is_palindrome,
        "unique_characters": record.unique_characters,
        "word_count": record.word_count,
        "sha256_hash": record.sha256_hash,
        "character_frequency_map": record.character_frequency_map,
    }
    return {
        "id": record.sha256_hash,
        "value": record.value,
        "properties": properties,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }

# ==============================================================
# ---------- Generic Filter Application ------------------------
# ==============================================================


def apply_filters_to_iterable(iterable, filters: Dict[str, Any]):
    """Apply parsed filters to queryset or iterable of StringRecord."""
    results = list(iterable)
    logger.debug(f"Starting filter, total strings: {len(results)}")

    for key, val in filters.items():
        if key == "is_palindrome":
            if val:
                results = [r for r in results if r.is_palindrome]
            else:
                results = [r for r in results if not r.is_palindrome]
        elif key == "word_count":
            results = [r for r in results if r.word_count == int(val)]
        elif key == "min_length":
            results = [r for r in results if r.length >= int(val)]
        elif key == "max_length":
            results = [r for r in results if r.length <= int(val)]
        elif key == "contains_character":
            ch = str(val).lower()
            results = [r for r in results if ch in normalize_for_compare(r.value)]

        logger.debug(f"After filter '{key}={val}', remaining: {[r.value for r in results]}")

    return results




# def apply_filters_to_iterable(iterable, filters: Dict[str, Any]):
#     """Apply parsed filters to queryset or iterable of StringRecord."""
#     results = list(iterable)

#     for key, val in filters.items():
#         if key == "is_palindrome":
#             if val:
#                 results = [r for r in results if r.is_palindrome]
#             else:
#                 results = [r for r in results if not r.is_palindrome]
#         elif key == "word_count":
#             results = [r for r in results if r.word_count == int(val)]
#         elif key == "min_length":
#             results = [r for r in results if r.length >= int(val)]
#         elif key == "max_length":
#             results = [r for r in results if r.length <= int(val)]
#         elif key == "contains_character":
#             ch = str(val).lower()
#             results = [r for r in results if ch in normalize_for_compare(r.value)]



#     return results

# ==============================================================
# ---------- Main String API -----------------------------------
# ==============================================================

class StringAPIView(APIView):
    """
    POST   /strings         -> create/analyze
    GET    /strings         -> list (+ filters)
    GET    /strings/<val>   -> retrieve
    DELETE /strings/<val>   -> delete
    """

    def get(self, request, string_value=None):
        try:
            # ---- GET specific string ----
            if string_value:
                sha = hashlib.sha256(string_value.encode()).hexdigest()
                obj = StringRecord.objects.filter(sha256_hash=sha).first()
                if not obj:
                    return Response(
                        {"detail": "String does not exist in the system."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                payload = make_response_payload(obj)
                return Response(payload, status=status.HTTP_200_OK)

            # ---- GET list with filters ----
            params = request.query_params
            filters = {}

            if "is_palindrome" in params:
                val = params.get("is_palindrome", "").lower()
                if val not in ("true", "false"):
                    return Response(
                        {"error": "Invalid value for is_palindrome; must be true or false."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                filters["is_palindrome"] = (val == "true")

            for field in ["min_length", "max_length", "word_count"]:
                if field in params:
                    try:
                        filters[field] = int(params.get(field))
                    except (ValueError, TypeError):
                        return Response(
                            {"error": f"Invalid {field}; must be integer."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

            if "contains_character" in params:
                v = params.get("contains_character", "").strip()
                if not v:
                    return Response(
                        {"error": "contains_character must be a non-empty string."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                filters["contains_character"] = v.lower()

            queryset = StringRecord.objects.all()
            matched = apply_filters_to_iterable(queryset, filters)

            data = [make_response_payload(r) for r in matched]
            return Response(
                {
                    "data": data,
                    "count": len(data),
                    "filters_applied": filters,
                    "detail": "No strings matched the filters." if not data else "Strings retrieved successfully.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception("Unexpected error in GET /strings")
            return Response(
                {"error": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, string_value=None):
        """Create a new string record."""
        try:
            data = request.data
            if not isinstance(data, dict):
                return Response({"error": "Invalid request body."}, status=status.HTTP_400_BAD_REQUEST)

            value = data.get("value")
            if value is None:
                return Response({"error": 'Missing "value" field.'}, status=status.HTTP_400_BAD_REQUEST)
            if not isinstance(value, str):
                return Response({"error": '"value" must be a string.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            value = value.strip()
            if not value:
                return Response({"error": '"value" cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

            props = compute_properties(value)

            if StringRecord.objects.filter(sha256_hash=props["sha256_hash"]).exists():
                return Response(
                    {"error": "String already exists in the system."},
                    status=status.HTTP_409_CONFLICT,
                )

            try:
                record = StringRecord.objects.create(
                    value=value,
                    length=props["length"],
                    is_palindrome=props["is_palindrome"],
                    unique_characters=props["unique_characters"],
                    word_count=props["word_count"],
                    sha256_hash=props["sha256_hash"],
                    character_frequency_map=props["character_frequency_map"],
                )
            except IntegrityError:
                logger.exception("DB IntegrityError creating StringRecord")
                return Response({"error": "Database error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            payload = make_response_payload(record)
            return Response(payload, status=status.HTTP_201_CREATED)

        except Exception:
            logger.exception("Unexpected error in POST /strings")
            return Response(
                {"error": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, string_value=None):
        """Delete a specific string by value."""
        try:
            if not string_value:
                return Response({"error": "String value required for deletion."}, status=status.HTTP_400_BAD_REQUEST)

            sha = hashlib.sha256(string_value.encode()).hexdigest()
            obj = StringRecord.objects.filter(sha256_hash=sha).first()
            if not obj:
                return Response({"error": "String does not exist in the system."}, status=status.HTTP_404_NOT_FOUND)

            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception:
            logger.exception("Unexpected error in DELETE /strings")
            return Response(
                {"error": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# ==============================================================
# ---------- NLP Query Parsing Utilities ------------------------
# ==============================================================

def parse_nl_filters(query: str) -> Dict[str, Any]:
    """Parse simple natural language phrases into structured filters."""
    q = query.lower().strip()
    filters: Dict[str, Any] = {}

    # Detect palindromic context
    if "palindrome" in q or "palindromic" in q:
        filters["is_palindrome"] = True

    # Single-word / one-word
    if "single word" in q or "one word" in q:
        filters["word_count"] = 1

    # Length conditions
    if match := re.search(r"longer than (\d+)", q):
        filters["min_length"] = int(match.group(1)) + 1
    if match := re.search(r"shorter than (\d+)", q):
        filters["max_length"] = int(match.group(1)) - 1

    # Contains specific letter
    if match := re.search(r"letter (\w)", q):
        filters["contains_character"] = match.group(1).lower()

    # “contain the first vowel”
    if "first vowel" in q:
        filters.setdefault("contains_character", "a")

    return filters

# ==============================================================
# ---------- NLP Endpoint ---------------------------------------
# ==============================================================

class StringNaturalLanguageFilterAPIView(APIView):
    """
    GET /strings/filter-by-natural-language?query=...
    """

    def get(self, request, string_value=None):
        try:
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

            if (
                "min_length" in filters
                and "max_length" in filters
                and filters["min_length"] > filters["max_length"]
            ):
                return Response(
                    {"error": "Conflicting filters detected."},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            queryset = StringRecord.objects.all()
            matched = apply_filters_to_iterable(queryset, filters)

            data = [make_response_payload(r) for r in matched]
            return Response(
                {
                    "data": data,
                    "count": len(data),
                    "interpreted_query": {
                        "original": query,
                        "parsed_filters": filters,
                    },
                    "detail": (
                        "No strings matched the applied natural-language filters."
                        if not data
                        else "Strings retrieved successfully."
                    ),
                },
                status=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception("Unexpected error in Natural Language Filter endpoint")
            return Response(
                {"error": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
