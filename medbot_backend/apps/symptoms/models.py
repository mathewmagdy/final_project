from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class SymptomCategory(models.Model):
    """
    Categories for organizing symptoms (e.g., Respiratory, Cardiovascular, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'symptom_categories'
        verbose_name_plural = 'Symptom Categories'


class Symptom(models.Model):
    """
    Individual symptoms that patients can report.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        SymptomCategory,
        on_delete=models.CASCADE,
        related_name='symptoms'
    )
    keywords = models.JSONField(default=list)  # Alternative names/descriptions
    severity_indicators = models.JSONField(default=list)
    associated_departments = models.ManyToManyField(
        'departments.Department',
        through='SymptomDepartmentMapping'
    )
    icd_codes = models.JSONField(default=list)
    is_emergency_indicator = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'symptoms'
        ordering = ['name']


class SymptomDepartmentMapping(models.Model):
    """
    Mapping between symptoms and departments with confidence scores.
    """
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE)
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(0.0000), MaxValueValidator(1.0000)]
    )
    priority_order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symptom.name} -> {self.department.name} ({self.confidence_score})"

    class Meta:
        db_table = 'symptom_department_mappings'
        unique_together = ['symptom', 'department']
        ordering = ['priority_order']
