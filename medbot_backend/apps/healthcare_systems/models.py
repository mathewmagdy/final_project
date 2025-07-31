from django.db import models
import uuid


class HealthcareSystem(models.Model):
    """
    Healthcare systems (hospitals, clinics, etc.) that use MedBot.
    """
    SYSTEM_TYPES = [
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('urgent_care', 'Urgent Care'),
        ('specialty_center', 'Specialty Center'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    system_type = models.CharField(max_length=20, choices=SYSTEM_TYPES)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)

    # Integration settings
    emr_system = models.CharField(max_length=50, blank=True)  # Epic, Cerner, etc.
    api_endpoint = models.URLField(blank=True)
    api_credentials = models.JSONField(default=dict)  # Encrypted

    # Operational details
    operating_hours = models.JSONField(default=dict)
    emergency_services = models.BooleanField(default=False)
    bed_capacity = models.IntegerField(null=True, blank=True)
    current_occupancy = models.IntegerField(default=0)

    # MedBot integration
    subscription_plan = models.CharField(max_length=50, default='basic')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.system_type})"

    class Meta:
        db_table = 'healthcare_systems'
        ordering = ['name']
