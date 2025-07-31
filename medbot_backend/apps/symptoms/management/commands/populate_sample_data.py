from django.core.management.base import BaseCommand
from apps.departments.models import Department
from apps.symptoms.models import SymptomCategory, Symptom
from apps.healthcare_systems.models import HealthcareSystem
from apps.users.models import User, DoctorProfile
from datetime import date


class Command(BaseCommand):
    help = 'Populate database with sample medical data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample medical data...')
        
        # Create departments
        departments_data = [
            {
                'name': 'Internal Medicine',
                'description': 'General internal medicine and primary care',
                'urgency_level': 'medium',
                'average_wait_time': 30,
                'specialization_keywords': ['general', 'primary care', 'internal', 'fever', 'fatigue']
            },
            {
                'name': 'Cardiology',
                'description': 'Heart and cardiovascular conditions',
                'urgency_level': 'high',
                'average_wait_time': 45,
                'specialization_keywords': ['heart', 'chest pain', 'cardiac', 'cardiovascular']
            },
            {
                'name': 'Neurology',
                'description': 'Brain and nervous system disorders',
                'urgency_level': 'high',
                'average_wait_time': 60,
                'specialization_keywords': ['headache', 'migraine', 'seizure', 'neurological']
            },
            {
                'name': 'Orthopedics',
                'description': 'Bone, joint, and muscle conditions',
                'urgency_level': 'medium',
                'average_wait_time': 40,
                'specialization_keywords': ['bone', 'joint', 'muscle', 'fracture', 'pain']
            },
            {
                'name': 'Dermatology',
                'description': 'Skin conditions and disorders',
                'urgency_level': 'low',
                'average_wait_time': 25,
                'specialization_keywords': ['skin', 'rash', 'acne', 'dermatitis']
            },
            {
                'name': 'Emergency Medicine',
                'description': 'Emergency and urgent care',
                'urgency_level': 'emergency',
                'average_wait_time': 15,
                'specialization_keywords': ['emergency', 'urgent', 'trauma', 'critical']
            }
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults=dept_data
            )
            departments[dept_data['name']] = dept
            if created:
                self.stdout.write(f'Created department: {dept.name}')
        
        # Create symptom categories
        categories_data = [
            {'name': 'Cardiovascular', 'description': 'Heart and blood vessel related symptoms'},
            {'name': 'Respiratory', 'description': 'Breathing and lung related symptoms'},
            {'name': 'Neurological', 'description': 'Brain and nervous system symptoms'},
            {'name': 'Musculoskeletal', 'description': 'Bone, joint, and muscle symptoms'},
            {'name': 'Dermatological', 'description': 'Skin related symptoms'},
            {'name': 'Gastrointestinal', 'description': 'Digestive system symptoms'},
            {'name': 'General', 'description': 'General symptoms and systemic conditions'}
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = SymptomCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(f'Created category: {cat.name}')
        
        # Create symptoms
        symptoms_data = [
            {
                'name': 'Chest Pain',
                'description': 'Pain or discomfort in the chest area',
                'category': 'Cardiovascular',
                'keywords': ['chest pain', 'heart pain', 'cardiac pain'],
                'is_emergency_indicator': True,
                'icd_codes': ['R07.89']
            },
            {
                'name': 'Shortness of Breath',
                'description': 'Difficulty breathing or feeling breathless',
                'category': 'Respiratory',
                'keywords': ['breathless', 'dyspnea', 'breathing difficulty'],
                'is_emergency_indicator': True,
                'icd_codes': ['R06.02']
            },
            {
                'name': 'Headache',
                'description': 'Pain in the head or upper neck',
                'category': 'Neurological',
                'keywords': ['head pain', 'migraine', 'cephalgia'],
                'is_emergency_indicator': False,
                'icd_codes': ['R51']
            },
            {
                'name': 'Fever',
                'description': 'Elevated body temperature',
                'category': 'General',
                'keywords': ['high temperature', 'pyrexia', 'febrile'],
                'is_emergency_indicator': False,
                'icd_codes': ['R50.9']
            },
            {
                'name': 'Joint Pain',
                'description': 'Pain in joints',
                'category': 'Musculoskeletal',
                'keywords': ['arthralgia', 'joint ache', 'joint discomfort'],
                'is_emergency_indicator': False,
                'icd_codes': ['M25.50']
            },
            {
                'name': 'Skin Rash',
                'description': 'Skin irritation or eruption',
                'category': 'Dermatological',
                'keywords': ['rash', 'skin eruption', 'dermatitis'],
                'is_emergency_indicator': False,
                'icd_codes': ['R21']
            }
        ]
        
        for symptom_data in symptoms_data:
            category_name = symptom_data.pop('category')
            symptom_data['category'] = categories[category_name]
            
            symptom, created = Symptom.objects.get_or_create(
                name=symptom_data['name'],
                defaults=symptom_data
            )
            if created:
                self.stdout.write(f'Created symptom: {symptom.name}')
        
        # Create a sample healthcare system
        healthcare_system, created = HealthcareSystem.objects.get_or_create(
            name='MedBot General Hospital',
            defaults={
                'system_type': 'hospital',
                'address': '123 Healthcare Ave',
                'city': 'Medical City',
                'state': 'CA',
                'zip_code': '90210',
                'phone_number': '+1-555-MEDBOT',
                'email': 'info@medbothospital.com',
                'emergency_services': True,
                'bed_capacity': 200,
                'monthly_fee': 5000.00,
                'contract_start_date': date.today(),
                'contract_end_date': date(2025, 12, 31)
            }
        )
        if created:
            self.stdout.write(f'Created healthcare system: {healthcare_system.name}')
        
        # Create a sample doctor
        doctor_user, created = User.objects.get_or_create(
            username='dr.smith',
            defaults={
                'email': 'dr.smith@medbothospital.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'user_type': 'doctor',
                'phone_number': '+1-555-0123',
                'is_verified': True
            }
        )
        if created:
            doctor_user.set_password('doctor123')
            doctor_user.save()
            
            # Create doctor profile
            DoctorProfile.objects.create(
                user=doctor_user,
                license_number='MD123456',
                specialization=departments['Internal Medicine'],
                years_of_experience=10,
                education='MD from Medical University',
                consultation_fee=200.00,
                available_hours={'monday': '9:00-17:00', 'tuesday': '9:00-17:00'},
                is_available=True
            )
            self.stdout.write(f'Created doctor: Dr. {doctor_user.get_full_name()}')
        
        # Create a sample patient
        patient_user, created = User.objects.get_or_create(
            username='patient.doe',
            defaults={
                'email': 'patient@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'user_type': 'patient',
                'phone_number': '+1-555-0456',
                'date_of_birth': date(1990, 5, 15),
                'gender': 'F',
                'is_verified': True
            }
        )
        if created:
            patient_user.set_password('patient123')
            patient_user.save()
            self.stdout.write(f'Created patient: {patient_user.get_full_name()}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated sample data!')
        )
