from django.db import models
import uuid


class Department(models.Model):
    """
    Medical departments/specialties in healthcare systems.
    """
    URGENCY_LEVELS = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('emergency', 'Emergency'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    specialization_keywords = models.JSONField(default=list)  # For AI matching
    icd_code_ranges = models.JSONField(default=list)  # Associated ICD-10 ranges
    urgency_level = models.CharField(max_length=20, choices=URGENCY_LEVELS)
    average_wait_time = models.IntegerField(default=30)  # minutes
    consultation_duration = models.IntegerField(default=20)  # minutes
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'departments'
        ordering = ['name']
