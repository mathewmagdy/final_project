from rest_framework import serializers
from .models import Symptom, SymptomCategory, SymptomDepartmentMapping
from apps.departments.models import Department
from apps.consultations.models import Consultation


class SymptomCategorySerializer(serializers.ModelSerializer):
    """Serializer for symptom categories."""
    
    class Meta:
        model = SymptomCategory
        fields = ['id', 'name', 'description', 'parent_category']


class SymptomSerializer(serializers.ModelSerializer):
    """Serializer for individual symptoms."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Symptom
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'keywords', 'severity_indicators', 'icd_codes', 'is_emergency_indicator'
        ]


class SymptomAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for symptom analysis requests."""
    symptoms = serializers.CharField(
        max_length=2000,
        help_text="Describe your symptoms in detail"
    )
    duration = serializers.CharField(
        max_length=100,
        required=False,
        help_text="How long have you had these symptoms?"
    )
    pain_level = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Rate your pain level from 1-10"
    )
    additional_info = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Any additional information"
    )
    preferred_language = serializers.CharField(
        max_length=10,
        default='en',
        help_text="Preferred language for analysis"
    )

    def validate_pain_level(self, value):
        """Custom validation for pain_level to handle string inputs."""
        if value is None or value == '' or value == 'null':
            return None

        try:
            # Convert string to integer
            if isinstance(value, str):
                value = value.strip()
                if value == '':
                    return None
                value = int(value)

            # Validate range
            if not (1 <= value <= 10):
                raise serializers.ValidationError("Pain level must be between 1 and 10.")

            return value
        except (ValueError, TypeError):
            raise serializers.ValidationError("Pain level must be a valid number between 1 and 10.")


class ConsultationSerializer(serializers.ModelSerializer):
    """Serializer for consultation records."""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    recommended_department_name = serializers.CharField(
        source='recommended_department.name', 
        read_only=True
    )
    analysis_duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'patient', 'patient_name', 'symptom_description',
            'symptom_duration', 'pain_level', 'additional_info',
            'recommended_department', 'recommended_department_name',
            'confidence_score', 'urgency_level', 'icd_suggestions',
            'alternative_departments', 'status', 'analysis_start_time',
            'analysis_end_time', 'analysis_duration_seconds', 'created_at'
        ]
        read_only_fields = [
            'id', 'patient', 'recommended_department', 'confidence_score',
            'urgency_level', 'icd_suggestions', 'alternative_departments',
            'status', 'analysis_start_time', 'analysis_end_time', 'created_at'
        ]
    
    def get_analysis_duration_seconds(self, obj):
        """Get analysis duration in seconds."""
        if obj.analysis_duration:
            return obj.analysis_duration.total_seconds()
        return None


class ConsultationResultSerializer(serializers.ModelSerializer):
    """Serializer for consultation results with detailed information."""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    recommended_department_info = serializers.SerializerMethodField()
    alternative_departments_info = serializers.SerializerMethodField()
    urgency_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'patient_name', 'symptom_description', 'symptom_duration',
            'pain_level', 'recommended_department_info', 'confidence_score',
            'urgency_level', 'urgency_info', 'icd_suggestions',
            'alternative_departments_info', 'status', 'created_at'
        ]
    
    def get_recommended_department_info(self, obj):
        """Get detailed information about recommended department."""
        if obj.recommended_department:
            return {
                'id': str(obj.recommended_department.id),
                'name': obj.recommended_department.name,
                'description': obj.recommended_department.description,
                'average_wait_time': obj.recommended_department.average_wait_time,
                'urgency_level': obj.recommended_department.urgency_level
            }
        return None
    
    def get_alternative_departments_info(self, obj):
        """Get detailed information about alternative departments."""
        if obj.alternative_departments:
            departments = Department.objects.filter(
                id__in=[dept['id'] for dept in obj.alternative_departments]
            )
            return [
                {
                    'id': str(dept.id),
                    'name': dept.name,
                    'description': dept.description,
                    'confidence': next(
                        (alt['confidence'] for alt in obj.alternative_departments 
                         if alt['id'] == str(dept.id)), 
                        None
                    )
                }
                for dept in departments
            ]
        return []
    
    def get_urgency_info(self, obj):
        """Get urgency level information with recommendations."""
        urgency_map = {
            'low': {
                'level': 'Low Priority',
                'description': 'Non-urgent condition that can be scheduled normally',
                'recommended_action': 'Schedule an appointment within 1-2 weeks'
            },
            'medium': {
                'level': 'Medium Priority',
                'description': 'Condition that should be addressed soon',
                'recommended_action': 'Schedule an appointment within 2-3 days'
            },
            'high': {
                'level': 'High Priority',
                'description': 'Urgent condition requiring prompt attention',
                'recommended_action': 'Seek medical attention within 24 hours'
            },
            'emergency': {
                'level': 'Emergency',
                'description': 'Critical condition requiring immediate attention',
                'recommended_action': 'Seek emergency care immediately'
            }
        }
        
        return urgency_map.get(obj.urgency_level, {
            'level': 'Unknown',
            'description': 'Urgency level not determined',
            'recommended_action': 'Consult with healthcare provider'
        })
