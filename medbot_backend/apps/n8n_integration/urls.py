from django.urls import path
from .views import (
    symptom_analysis_callback,
    appointment_booking_callback,
    workflow_error_callback
)

urlpatterns = [
    # n8n webhook callbacks
    path('symptom-analysis/', symptom_analysis_callback, name='symptom-analysis-callback'),
    path('appointment-booking/', appointment_booking_callback, name='appointment-booking-callback'),
    path('workflow-error/', workflow_error_callback, name='workflow-error-callback'),
]
