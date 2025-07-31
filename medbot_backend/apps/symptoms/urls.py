from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SymptomViewSet, SymptomCategoryViewSet, SymptomAnalysisViewSet

router = DefaultRouter()
router.register(r'symptoms', SymptomViewSet, basename='symptoms')
router.register(r'categories', SymptomCategoryViewSet, basename='symptom-categories')
router.register(r'analysis', SymptomAnalysisViewSet, basename='symptom-analysis')

urlpatterns = [
    path('', include(router.urls)),
]
