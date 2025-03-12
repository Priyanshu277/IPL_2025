from django.urls import path
from .views import prediction_page, predict_match_winner

urlpatterns = [
    path("", prediction_page, name="prediction_page"),  # UI Page
    path("predict/", predict_match_winner, name="predict_match_winner"),  # API Endpoint
]