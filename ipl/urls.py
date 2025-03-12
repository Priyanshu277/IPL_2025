from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('predictor/', include('Predictor.urls')),
    path('match-stats/', views.match_stats, name='match_stats'),
    path('venue-stats/', views.venue_stats, name='venue_stats'),
    path('performance-stats/', views.performance_stats, name='performance_stats'),
]
