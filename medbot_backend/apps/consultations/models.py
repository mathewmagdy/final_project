from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
import uuid


class Consultation(models.Model):
    """
    Patient consultation sessions for symptom analysis.
    """
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('analyzing', 'Analyzing Symptoms'),
        ('completed', 'Analysis Completed'),
        ('scheduled', 'Appointment Scheduled'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consultations'
    )
    healthcare_system = models.ForeignKey(
        'healthcare_systems.HealthcareSystem',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Symptom input
    symptom_description = models.TextField()
    symptom_duration = models.CharField(max_length=100, blank=True)
    pain_level = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    additional_info = models.TextField(blank=True)

    # AI Analysis results
    recommended_department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        validators=[MinValueValidator(0.0000), MaxValueValidator(1.0000)]
    )
    urgency_level = models.CharField(max_length=20, null=True, blank=True)
    icd_suggestions = models.JSONField(default=list)
    alternative_departments = models.JSONField(default=list)

    # Workflow tracking
    n8n_execution_id = models.CharField(max_length=100, blank=True)
    analysis_start_time = models.DateTimeField(null=True, blank=True)
    analysis_end_time = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consultation {self.id} - {self.patient.get_full_name()}"

    @property
    def analysis_duration(self):
        if self.analysis_start_time and self.analysis_end_time:
            return self.analysis_end_time - self.analysis_start_time
        return None

    class Meta:
        db_table = 'consultations'
        ordering = ['-created_at']


class ConsultationFeedback(models.Model):
    """
    Patient feedback on consultation accuracy and helpfulness.
    """
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    accuracy_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    helpfulness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    speed_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comments = models.TextField(blank=True)
    would_recommend = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.consultation.id}"

    class Meta:
        db_table = 'consultation_feedback'


class Appointment(models.Model):
    """
    Scheduled appointments between patients and doctors.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]

    APPOINTMENT_TYPES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('routine_checkup', 'Routine Checkup'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE)
    healthcare_system = models.ForeignKey(
        'healthcare_systems.HealthcareSystem',
        on_delete=models.CASCADE
    )

    # Scheduling details
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    estimated_duration = models.IntegerField(default=20)  # minutes
    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPES)

    # Status and notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)

    # Integration tracking
    emr_appointment_id = models.CharField(max_length=100, blank=True)
    n8n_booking_execution_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment {self.id} - {self.patient.get_full_name()} with Dr. {self.doctor.get_full_name()}"

    class Meta:
        db_table = 'appointments'
        unique_together = ['doctor', 'scheduled_date', 'scheduled_time']
        ordering = ['scheduled_date', 'scheduled_time']


class AppointmentReminder(models.Model):
    """
    Reminders for upcoming appointments.
    """
    REMINDER_TYPES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('call', 'Phone Call'),
    ]

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES)
    scheduled_time = models.DateTimeField()
    sent_time = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    n8n_execution_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reminder_type} reminder for {self.appointment.id}"

    class Meta:
        db_table = 'appointment_reminders'
