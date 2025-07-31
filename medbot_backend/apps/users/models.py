from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class User(AbstractUser):
    """
    Custom User model for MedBot system.
    Extends Django's AbstractUser to include healthcare-specific fields.
    """
    USER_TYPES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
        ('clinic_admin', 'Clinic Administrator'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='patient')
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    medical_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class PatientProfile(models.Model):
    """
    Extended profile for patients with insurance and healthcare preferences.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)
    primary_care_physician = models.CharField(max_length=100, blank=True)
    preferred_hospital = models.ForeignKey(
        'healthcare_systems.HealthcareSystem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Patient Profile: {self.user.get_full_name()}"

    class Meta:
        db_table = 'patient_profiles'


class DoctorProfile(models.Model):
    """
    Extended profile for doctors with professional information.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE
    )
    years_of_experience = models.IntegerField()
    education = models.TextField()
    certifications = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    available_hours = models.JSONField(default=dict)  # Store weekly schedule
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)]
    )
    total_consultations = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization.name}"

    class Meta:
        db_table = 'doctor_profiles'
