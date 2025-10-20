from django.urls import path
from .views import StringAPIView, StringNaturalLanguageFilterAPIView

urlpatterns = [
    path("strings/", StringAPIView.as_view(), name="string-analyzer"),
    path("strings/<str:string_value>/", StringAPIView.as_view(), name="string-detail"),
    path("strings/filter-by-natural-language", StringNaturalLanguageFilterAPIView.as_view(), name="nlp-filter"),
]
