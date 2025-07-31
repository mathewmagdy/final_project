from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging
from apps.consultations.models import Consultation, Appointment
from .models import N8NExecution

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def symptom_analysis_callback(request):
    """
    Handle symptom analysis results from n8n.
    """
    try:
        data = json.loads(request.body)
        consultation_id = data.get('consultation_id')
        execution_id = data.get('execution_id')
        results = data.get('results', {})

        logger.info(f"Received symptom analysis callback for consultation {consultation_id}")

        # Update consultation with results
        consultation = Consultation.objects.get(id=consultation_id)
        consultation.recommended_department_id = results.get('department_id')
        consultation.confidence_score = results.get('confidence_score')
        consultation.urgency_level = results.get('urgency_level')
        consultation.icd_suggestions = results.get('icd_codes', [])
        consultation.alternative_departments = results.get('alternatives', [])
        consultation.status = 'completed'
        consultation.analysis_end_time = timezone.now()
        consultation.save()

        # Update execution record
        try:
            execution = N8NExecution.objects.get(n8n_execution_id=execution_id)
            execution.output_data = results
            execution.status = 'success'
            execution.end_time = timezone.now()
            execution.save()
        except N8NExecution.DoesNotExist:
            logger.warning(f"N8N execution {execution_id} not found")

        return JsonResponse({
            'status': 'success',
            'message': 'Results processed successfully'
        })

    except Consultation.DoesNotExist:
        logger.error(f"Consultation {consultation_id} not found")
        return JsonResponse({
            'status': 'error',
            'message': 'Consultation not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error processing symptom analysis callback: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def appointment_booking_callback(request):
    """
    Handle appointment booking results from n8n.
    """
    try:
        data = json.loads(request.body)
        booking_result = data.get('booking_result', {})
        execution_id = data.get('execution_id')

        logger.info(f"Received appointment booking callback for execution {execution_id}")

        if booking_result.get('success'):
            # Update appointment record if it exists
            appointment_id = booking_result.get('appointment_id')
            if appointment_id:
                appointment = Appointment.objects.get(id=appointment_id)
                appointment.emr_appointment_id = booking_result.get('emr_appointment_id')
                appointment.status = 'confirmed'
                appointment.save()
                logger.info(f"Appointment {appointment_id} confirmed")

        return JsonResponse({
            'status': 'success',
            'message': 'Booking result processed'
        })

    except Appointment.DoesNotExist:
        logger.error(f"Appointment {appointment_id} not found")
        return JsonResponse({
            'status': 'error',
            'message': 'Appointment not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error processing booking callback: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def workflow_error_callback(request):
    """
    Handle workflow errors from n8n.
    """
    try:
        data = json.loads(request.body)
        execution_id = data.get('execution_id')
        error_message = data.get('error_message')

        logger.error(f"Workflow error for execution {execution_id}: {error_message}")

        # Update execution record
        try:
            execution = N8NExecution.objects.get(n8n_execution_id=execution_id)
            execution.status = 'error'
            execution.error_message = error_message
            execution.end_time = timezone.now()
            execution.save()

            # Handle specific error cases
            if execution.consultation:
                execution.consultation.status = 'error'
                execution.consultation.save()
                logger.info(f"Consultation {execution.consultation.id} marked as error")

        except N8NExecution.DoesNotExist:
            logger.warning(f"N8N execution {execution_id} not found")

        return JsonResponse({
            'status': 'success',
            'message': 'Error logged successfully'
        })

    except Exception as e:
        logger.error(f"Error processing workflow error callback: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
