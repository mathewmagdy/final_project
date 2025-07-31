import requests
import json
from django.conf import settings
from django.utils import timezone
from .models import N8NWorkflow, N8NExecution
import logging

logger = logging.getLogger(__name__)


class N8NService:
    """
    Service class for interacting with n8n workflows.
    Handles AI workflow orchestration and execution tracking.
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'N8N_BASE_URL', 'http://localhost:5678')
        self.api_key = getattr(settings, 'N8N_API_KEY', 'development-key')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = 30
    
    def trigger_symptom_analysis(self, consultation_id, symptoms, patient_data):
        """
        Trigger symptom analysis workflow in n8n.
        
        Args:
            consultation_id: UUID of the consultation
            symptoms: Patient's symptom description
            patient_data: Patient demographic and medical data
            
        Returns:
            str: n8n execution ID if successful, None if failed
        """
        try:
            # Get active symptom analysis workflow
            workflow = N8NWorkflow.objects.filter(
                workflow_type='symptom_analysis',
                is_active=True
            ).first()
            
            if not workflow:
                logger.error("No active symptom analysis workflow found")
                return self._mock_analysis_response(consultation_id, symptoms, patient_data)
            
            # Prepare payload for n8n
            payload = {
                'consultation_id': str(consultation_id),
                'symptoms': symptoms,
                'patient_data': patient_data,
                'timestamp': timezone.now().isoformat(),
                'callback_url': f"{settings.ALLOWED_HOSTS[0]}/webhooks/n8n/symptom-analysis/"
            }
            
            # Make request to n8n webhook
            response = requests.post(
                workflow.webhook_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                execution_id = result.get('execution_id', f"exec_{consultation_id}")
                
                # Create execution record
                N8NExecution.objects.create(
                    workflow=workflow,
                    n8n_execution_id=execution_id,
                    consultation_id=consultation_id,
                    input_data=payload,
                    status='running',
                    start_time=timezone.now()
                )
                
                logger.info(f"Triggered n8n symptom analysis: {execution_id}")
                return execution_id
            else:
                logger.error(f"n8n workflow trigger failed: {response.status_code} - {response.text}")
                return self._mock_analysis_response(consultation_id, symptoms, patient_data)
                
        except requests.RequestException as e:
            logger.error(f"Network error triggering n8n workflow: {str(e)}")
            return self._mock_analysis_response(consultation_id, symptoms, patient_data)
        except Exception as e:
            logger.error(f"Error triggering symptom analysis: {str(e)}")
            return None
    
    def trigger_appointment_booking(self, consultation_id, department_id, preferred_date, preferred_time, patient_id):
        """
        Trigger appointment booking workflow in n8n.
        
        Returns:
            dict: Booking result with success status and details
        """
        try:
            workflow = N8NWorkflow.objects.filter(
                workflow_type='appointment_booking',
                is_active=True
            ).first()
            
            if not workflow:
                logger.error("No active appointment booking workflow found")
                return self._mock_booking_response()
            
            payload = {
                'consultation_id': str(consultation_id),
                'department_id': str(department_id),
                'preferred_date': preferred_date,
                'preferred_time': preferred_time,
                'patient_id': str(patient_id),
                'timestamp': timezone.now().isoformat()
            }
            
            response = requests.post(
                workflow.webhook_url,
                headers=self.headers,
                json=payload,
                timeout=60  # Booking might take longer
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Create execution record
                N8NExecution.objects.create(
                    workflow=workflow,
                    n8n_execution_id=result.get('execution_id', f"book_{consultation_id}"),
                    consultation_id=consultation_id,
                    input_data=payload,
                    output_data=result,
                    status='success' if result.get('success') else 'error',
                    start_time=timezone.now(),
                    end_time=timezone.now()
                )
                
                return result
            else:
                logger.error(f"n8n booking workflow failed: {response.status_code} - {response.text}")
                return {'success': False, 'error_message': 'Booking workflow failed'}
                
        except Exception as e:
            logger.error(f"Error triggering appointment booking: {str(e)}")
            return {'success': False, 'error_message': str(e)}
    
    def get_execution_status(self, execution_id):
        """
        Get execution status from n8n.
        
        Args:
            execution_id: n8n execution ID
            
        Returns:
            dict: Execution status and data
        """
        try:
            # For development, return mock status if n8n not available
            if self.base_url == 'http://localhost:5678':
                return self._mock_execution_status(execution_id)
            
            url = f"{self.base_url}/api/v1/executions/{execution_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                execution_data = response.json()
                
                # Update local execution record
                try:
                    execution = N8NExecution.objects.get(n8n_execution_id=execution_id)
                    execution.status = execution_data.get('status', 'unknown')
                    execution.output_data = execution_data.get('data', {})
                    if execution_data.get('status') in ['success', 'error']:
                        execution.end_time = timezone.now()
                    execution.save()
                except N8NExecution.DoesNotExist:
                    pass
                
                return execution_data
            else:
                logger.error(f"Failed to get execution status: {response.status_code}")
                return {'status': 'unknown'}
                
        except Exception as e:
            logger.error(f"Error getting execution status: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def trigger_notification_workflow(self, notification_type, recipient_data, message_data):
        """
        Trigger notification workflow for appointments, reminders, etc.
        
        Returns:
            bool: True if notification triggered successfully
        """
        try:
            workflow = N8NWorkflow.objects.filter(
                workflow_type='notification',
                is_active=True
            ).first()
            
            if not workflow:
                logger.warning("No active notification workflow found")
                return False
            
            payload = {
                'notification_type': notification_type,
                'recipient_data': recipient_data,
                'message_data': message_data,
                'timestamp': timezone.now().isoformat()
            }
            
            response = requests.post(
                workflow.webhook_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error triggering notification: {str(e)}")
            return False
    
    def _mock_analysis_response(self, consultation_id, symptoms, patient_data):
        """
        Mock AI analysis response for development when n8n is not available.
        This simulates the AI analysis workflow.
        """
        import time
        import threading
        from apps.consultations.models import Consultation
        from apps.departments.models import Department
        
        def delayed_mock_response():
            """Simulate AI processing delay and callback."""
            time.sleep(2)  # Simulate processing time
            
            try:
                consultation = Consultation.objects.get(id=consultation_id)
                
                # Simple keyword-based department routing (mock AI)
                symptoms_lower = symptoms.lower()
                department_mapping = {
                    'chest pain|heart|cardiac': 'Cardiology',
                    'headache|migraine|head': 'Neurology',
                    'fever|cold|cough|flu': 'Internal Medicine',
                    'skin|rash|itch': 'Dermatology',
                    'bone|joint|muscle|pain': 'Orthopedics',
                    'eye|vision|sight': 'Ophthalmology',
                    'ear|hearing|throat': 'ENT',
                }
                
                recommended_dept = None
                for keywords, dept_name in department_mapping.items():
                    if any(keyword in symptoms_lower for keyword in keywords.split('|')):
                        recommended_dept = Department.objects.filter(name__icontains=dept_name).first()
                        break
                
                if not recommended_dept:
                    recommended_dept = Department.objects.filter(name__icontains='Internal Medicine').first()
                
                # Update consultation with mock results
                if recommended_dept:
                    consultation.recommended_department = recommended_dept
                consultation.confidence_score = 0.85
                consultation.urgency_level = 'medium'
                consultation.icd_suggestions = ['R50.9', 'R06.02']  # Mock ICD codes
                consultation.alternative_departments = []
                consultation.status = 'completed'
                consultation.analysis_end_time = timezone.now()
                consultation.save()
                
                logger.info(f"Mock analysis completed for consultation {consultation_id}")
                
            except Exception as e:
                logger.error(f"Error in mock analysis: {str(e)}")
        
        # Start mock processing in background
        thread = threading.Thread(target=delayed_mock_response)
        thread.daemon = True
        thread.start()
        
        return f"mock_exec_{consultation_id}"
    
    def _mock_booking_response(self):
        """Mock appointment booking response."""
        return {
            'success': True,
            'appointment_id': 'mock_appointment_123',
            'scheduled_date': '2024-01-15',
            'scheduled_time': '10:00',
            'doctor_id': 'mock_doctor_456',
            'healthcare_system_id': 'mock_hospital_789',
            'execution_id': 'mock_booking_exec'
        }
    
    def _mock_execution_status(self, execution_id):
        """Mock execution status for development."""
        from apps.departments.models import Department

        # Get a real department for the mock response
        dept = Department.objects.filter(name__icontains='Internal Medicine').first()
        dept_id = str(dept.id) if dept else None

        return {
            'status': 'success',
            'data': {
                'department_id': dept_id,
                'confidence_score': 0.85,
                'urgency_level': 'medium',
                'icd_codes': ['R50.9'],
                'alternatives': []
            }
        }
