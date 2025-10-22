# from django.urls import path
# from .views import StringAPIView, StringNaturalLanguageFilterAPIView

# urlpatterns = [
#     path("strings/", StringAPIView.as_view(), name="string-analyzer"),
#     path("strings/<str:string_value>/", StringAPIView.as_view(), name="string-detail"),
#     path("strings/filter-by-natural-language", StringNaturalLanguageFilterAPIView.as_view(), name="nlp-filter"),
# ]






# from django.urls import re_path
# from .views import StringAPIView, StringNaturalLanguageFilterAPIView

# urlpatterns = [
#     # /strings/  → handled here
#     re_path(r"^$", StringAPIView.as_view(), name="string-analyzer"),

#     # /strings/<string_value>/  → handled here
#     re_path(r"^(?P<string_value>[^/]+)/?$", StringAPIView.as_view(), name="string-detail"),

#     # /strings/filter-by-natural-language/  → handled here
#     re_path(r"^filter-by-natural-language/?$", StringNaturalLanguageFilterAPIView.as_view(), name="nlp-filter"),
# ]





from django.urls import re_path
from .views import StringAPIView, StringNaturalLanguageFilterAPIView

urlpatterns = [
    # /strings/filter-by-natural-language/  → must come first!
    re_path(r"^filter-by-natural-language/?$", StringNaturalLanguageFilterAPIView.as_view(), name="nlp-filter"),

    # /strings/  → base endpoint for POST and GET list
    re_path(r"^$", StringAPIView.as_view(), name="string-analyzer"),

    # /strings/<string_value>/  → retrieve or delete
    re_path(r"^(?P<string_value>[^/]+)/?$", StringAPIView.as_view(), name="string-detail"),
]
