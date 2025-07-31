from django.db import models
import uuid


class N8NWorkflow(models.Model):
    """
    n8n workflows used in the MedBot system.
    """
    WORKFLOW_TYPES = [
        ('symptom_analysis', 'Symptom Analysis'),
        ('voice_processing', 'Voice Processing'),
        ('appointment_booking', 'Appointment Booking'),
        ('emr_integration', 'EMR Integration'),
        ('notification', 'Notification'),
        ('analytics', 'Analytics'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    workflow_type = models.CharField(max_length=30, choices=WORKFLOW_TYPES)
    n8n_workflow_id = models.CharField(max_length=100, unique=True)
    version = models.CharField(max_length=20)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    webhook_url = models.URLField()
    configuration = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.workflow_type})"

    class Meta:
        db_table = 'n8n_workflows'
        ordering = ['name']


class N8NExecution(models.Model):
    """
    Execution records for n8n workflows.
    """
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('waiting', 'Waiting'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        N8NWorkflow,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    n8n_execution_id = models.CharField(max_length=100, unique=True)

    # Related objects
    consultation = models.ForeignKey(
        'consultations.Consultation',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='n8n_executions'
    )
    appointment = models.ForeignKey(
        'consultations.Appointment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='n8n_executions'
    )

    # Execution details
    input_data = models.JSONField()
    output_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    error_message = models.TextField(blank=True)

    # Performance metrics
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    execution_time = models.DurationField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Execution {self.n8n_execution_id} - {self.workflow.name}"

    def save(self, *args, **kwargs):
        # Calculate execution time if both start and end times are available
        if self.start_time and self.end_time:
            self.execution_time = self.end_time - self.start_time
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'n8n_executions'
        ordering = ['-created_at']
