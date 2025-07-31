from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import Symptom, SymptomCategory
from apps.consultations.models import Consultation
from .serializers import (
    SymptomSerializer,
    SymptomCategorySerializer,
    SymptomAnalysisRequestSerializer,
    ConsultationSerializer,
    ConsultationResultSerializer
)
from apps.n8n_integration.services import N8NService
import logging

logger = logging.getLogger(__name__)


class SymptomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing symptoms and categories.
    """
    queryset = Symptom.objects.all()
    serializer_class = SymptomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__icontains=category)

        # Search by keyword
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(keywords__icontains=search)
            )

        return queryset.order_by('name')


class SymptomCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing symptom categories.
    """
    queryset = SymptomCategory.objects.all()
    serializer_class = SymptomCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class SymptomAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for symptom analysis and consultation management.
    """
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return consultations for the current user."""
        return Consultation.objects.filter(
            patient=self.request.user
        ).order_by('-created_at')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'analyze_symptoms':
            return SymptomAnalysisRequestSerializer
        elif self.action in ['retrieve', 'analysis_results']:
            return ConsultationResultSerializer
        return ConsultationSerializer

    @action(detail=False, methods=['post'])
    def analyze_symptoms(self, request):
        """
        Main endpoint for symptom analysis.
        Creates a consultation and triggers n8n workflow.
        """
        logger.info(f"Received symptom analysis request: {request.data}")
        serializer = SymptomAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create consultation record
            consultation = Consultation.objects.create(
                patient=request.user,
                symptom_description=serializer.validated_data['symptoms'],
                symptom_duration=serializer.validated_data.get('duration', ''),
                pain_level=serializer.validated_data.get('pain_level'),
                additional_info=serializer.validated_data.get('additional_info', ''),
                status='analyzing',
                analysis_start_time=timezone.now()
            )

            logger.info(f"Created consultation {consultation.id} for user {request.user.id}")

            # Prepare patient data for AI analysis
            patient_data = {
                'age': self._calculate_age(request.user.date_of_birth) if request.user.date_of_birth else None,
                'gender': request.user.gender,
                'medical_history': request.user.medical_history,
                'allergies': request.user.allergies,
                'current_medications': request.user.current_medications,
                'preferred_language': serializer.validated_data.get('preferred_language', 'en')
            }

            # Trigger n8n workflow for AI analysis
            n8n_service = N8NService()
            execution_id = n8n_service.trigger_symptom_analysis(
                consultation_id=consultation.id,
                symptoms=consultation.symptom_description,
                patient_data=patient_data
            )

            if execution_id:
                consultation.n8n_execution_id = execution_id
                consultation.save()

                return Response({
                    'consultation_id': str(consultation.id),
                    'execution_id': execution_id,
                    'status': 'analyzing',
                    'message': 'Symptom analysis initiated successfully',
                    'estimated_completion_time': '30-60 seconds'
                }, status=status.HTTP_202_ACCEPTED)
            else:
                # Fallback: mark as error and provide basic response
                consultation.status = 'error'
                consultation.save()

                return Response({
                    'consultation_id': str(consultation.id),
                    'status': 'error',
                    'message': 'AI analysis service temporarily unavailable',
                    'fallback_recommendation': 'Please consult with a healthcare provider'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            logger.error(f"Error in symptom analysis: {str(e)}")
            return Response({
                'error': 'Internal server error',
                'message': 'Please try again later'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def analysis_status(self, request, pk=None):
        """
        Check the status of symptom analysis.
        """
        try:
            consultation = self.get_object()

            # If analysis is still running, check n8n status
            if consultation.status == 'analyzing' and consultation.n8n_execution_id:
                n8n_service = N8NService()
                execution_status = n8n_service.get_execution_status(
                    consultation.n8n_execution_id
                )

                # Update consultation if n8n workflow completed
                if execution_status.get('status') == 'success':
                    self._update_consultation_results(consultation, execution_status.get('data', {}))

            return Response({
                'consultation_id': str(consultation.id),
                'status': consultation.status,
                'analysis_complete': consultation.status in ['completed', 'error'],
                'progress_message': self._get_progress_message(consultation.status),
                'results_available': consultation.status == 'completed'
            })

        except Exception as e:
            logger.error(f"Error checking analysis status: {str(e)}")
            return Response({
                'error': 'Unable to check status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def analysis_results(self, request, pk=None):
        """
        Get detailed analysis results for a completed consultation.
        """
        consultation = self.get_object()

        if consultation.status != 'completed':
            return Response({
                'error': 'Analysis not completed yet',
                'status': consultation.status
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ConsultationResultSerializer(consultation)
        return Response(serializer.data)

    def _calculate_age(self, birth_date):
        """Calculate age from birth date."""
        if not birth_date:
            return None

        today = timezone.now().date()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

    def _get_progress_message(self, status):
        """Get user-friendly progress message."""
        messages = {
            'initiated': 'Analysis request received',
            'analyzing': 'AI is analyzing your symptoms...',
            'completed': 'Analysis completed successfully',
            'error': 'Analysis encountered an error',
            'cancelled': 'Analysis was cancelled'
        }
        return messages.get(status, 'Unknown status')

    def _update_consultation_results(self, consultation, results_data):
        """Update consultation with AI analysis results."""
        try:
            # Get department by ID if provided
            department_id = results_data.get('department_id')
            if department_id:
                from apps.departments.models import Department
                try:
                    department = Department.objects.get(id=department_id)
                    consultation.recommended_department = department
                except Department.DoesNotExist:
                    logger.warning(f"Department with ID {department_id} not found")

            consultation.confidence_score = results_data.get('confidence_score')
            consultation.urgency_level = results_data.get('urgency_level')
            consultation.icd_suggestions = results_data.get('icd_codes', [])
            consultation.alternative_departments = results_data.get('alternatives', [])
            consultation.status = 'completed'
            consultation.analysis_end_time = timezone.now()
            consultation.save()

            logger.info(f"Updated consultation {consultation.id} with AI results")

        except Exception as e:
            logger.error(f"Error updating consultation results: {str(e)}")
            consultation.status = 'error'
            consultation.save()
