import random
import hashlib
from .models import Disease
from PIL import Image
import io


class MockMLDetector:
    """
    Mock ML Detection Engine
    Simulates disease/pest detection with realistic confidence scores (85-98%)
    In production, this would be replaced with actual ML model inference
    """
    
    # Plant diseases database
    PLANT_DISEASES = {
        'Powdery Mildew': {
            'confidence_range': (88, 95),
            'severity': 'medium',
            'affected_species': ['Roses', 'Tomatoes', 'Grapes', 'Cucumbers', 'Squash'],
        },
        'Leaf Spot': {
            'confidence_range': (85, 92),
            'severity': 'low',
            'affected_species': ['Tomatoes', 'Peppers', 'Lettuce', 'Spinach'],
        },
        'Rust': {
            'confidence_range': (87, 94),
            'severity': 'medium',
            'affected_species': ['Beans', 'Wheat', 'Corn', 'Roses'],
        },
        'Early Blight': {
            'confidence_range': (89, 96),
            'severity': 'high',
            'affected_species': ['Tomatoes', 'Potatoes'],
        },
        'Anthracnose': {
            'confidence_range': (86, 93),
            'severity': 'medium',
            'affected_species': ['Peppers', 'Cucumbers', 'Melons'],
        },
        'Downy Mildew': {
            'confidence_range': (87, 94),
            'severity': 'medium',
            'affected_species': ['Grapes', 'Lettuce', 'Cucumbers'],
        },
    }
    
    # Animal diseases/pests database
    ANIMAL_DISEASES = {
        'Tick Infestation': {
            'confidence_range': (87, 95),
            'severity': 'medium',
            'affected_species': ['Cattle', 'Sheep', 'Goats', 'Horses', 'Dogs'],
        },
        'Mite Infestation': {
            'confidence_range': (85, 93),
            'severity': 'high',
            'affected_species': ['Cattle', 'Sheep', 'Poultry', 'Dogs'],
        },
        'Foot and Mouth Disease': {
            'confidence_range': (91, 98),
            'severity': 'high',
            'affected_species': ['Cattle', 'Sheep', 'Goats', 'Pigs'],
        },
        'Mastitis': {
            'confidence_range': (88, 96),
            'severity': 'high',
            'affected_species': ['Cattle', 'Sheep', 'Goats'],
        },
        'Scabies': {
            'confidence_range': (86, 94),
            'severity': 'medium',
            'affected_species': ['Sheep', 'Goats', 'Pigs', 'Dogs'],
        },
        'Coccidiosis': {
            'confidence_range': (87, 95),
            'severity': 'medium',
            'affected_species': ['Poultry', 'Cattle', 'Sheep'],
        },
        'Bloat': {
            'confidence_range': (84, 92),
            'severity': 'high',
            'affected_species': ['Cattle', 'Sheep', 'Goats'],
        },
    }
    
    @staticmethod
    def get_image_hash(image_file) -> str:
        """Generate hash from image for deterministic results in testing"""
        try:
            image_file.seek(0)
            image_data = image_file.read()
            return hashlib.md5(image_data).hexdigest()
        except:
            return ""
    
    @staticmethod
    def detect_plant_disease(image_file) -> dict:
        """Detect plant disease from image"""
        # Get image hash for deterministic results
        image_hash = MockMLDetector.get_image_hash(image_file)
        
        # Use hash to select disease (deterministic but pseudo-random)
        diseases = list(MockMLDetector.PLANT_DISEASES.keys())
        disease_index = int(image_hash[:2], 16) % len(diseases)
        disease_name = diseases[disease_index]
        
        disease_info = MockMLDetector.PLANT_DISEASES[disease_name]
        
        # Generate confidence (seeded by hash for reproducibility)
        confidence_min, confidence_max = disease_info['confidence_range']
        seed_value = int(image_hash[:4], 16)
        random.seed(seed_value)
        confidence = round(random.uniform(confidence_min, confidence_max), 1)
        
        # Get or create disease in database
        try:
            disease = Disease.objects.get(name=disease_name, subject_type='plant')
        except Disease.DoesNotExist:
            disease = None
        
        return {
            'disease_name': disease_name,
            'disease': disease,
            'confidence': confidence,
            'severity': disease_info['severity'],
            'treatment': MockMLDetector.get_plant_treatment(disease_name),
            'prevention': MockMLDetector.get_plant_prevention(disease_name),
            'affected_species': disease_info['affected_species'],
        }
    
    @staticmethod
    def detect_animal_disease(image_file) -> dict:
        """Detect animal disease/pest from image"""
        # Get image hash for deterministic results
        image_hash = MockMLDetector.get_image_hash(image_file)
        
        # Use hash to select disease
        diseases = list(MockMLDetector.ANIMAL_DISEASES.keys())
        disease_index = int(image_hash[:2], 16) % len(diseases)
        disease_name = diseases[disease_index]
        
        disease_info = MockMLDetector.ANIMAL_DISEASES[disease_name]
        
        # Generate confidence (seeded by hash)
        confidence_min, confidence_max = disease_info['confidence_range']
        seed_value = int(image_hash[:4], 16)
        random.seed(seed_value)
        confidence = round(random.uniform(confidence_min, confidence_max), 1)
        
        # Get or create disease in database
        try:
            disease = Disease.objects.get(name=disease_name, subject_type='animal')
        except Disease.DoesNotExist:
            disease = None
        
        return {
            'disease_name': disease_name,
            'disease': disease,
            'confidence': confidence,
            'severity': disease_info['severity'],
            'treatment': MockMLDetector.get_animal_treatment(disease_name),
            'prevention': MockMLDetector.get_animal_prevention(disease_name),
            'affected_species': disease_info['affected_species'],
        }
    
    @staticmethod
    def get_plant_treatment(disease_name: str) -> str:
        """Get treatment recommendations for plant disease"""
        treatments = {
            'Powdery Mildew': 'Apply sulfur-based fungicide every 7-10 days. Ensure good air circulation. Remove affected leaves. Consider baking soda spray (1 tbsp per gallon water) for organic approach.',
            'Leaf Spot': 'Remove affected leaves immediately. Apply copper fungicide or sulfur. Avoid overhead watering. Ensure proper spacing and ventilation.',
            'Rust': 'Remove infected leaves and branches. Apply fungicide with rust action. Improve air circulation. Avoid wetting foliage during watering.',
            'Early Blight': 'Remove lower infected leaves. Apply mancozeb or chlorothalonil fungicide. Water at soil level only. Prune for better air circulation.',
            'Anthracnose': 'Apply copper-based fungicide. Remove and destroy infected fruit/leaves. Improve drainage. Avoid overhead watering.',
            'Downy Mildew': 'Apply metalaxyl or mefenoxam fungicide. Ensure good drainage. Remove infected leaves. Improve air circulation and reduce humidity.',
        }
        return treatments.get(disease_name, 'Consult with local agricultural extension service for specific treatment recommendations.')
    
    @staticmethod
    def get_plant_prevention(disease_name: str) -> str:
        """Get prevention recommendations for plant disease"""
        prevention = {
            'Powdery Mildew': 'Maintain adequate spacing between plants. Ensure proper ventilation. Avoid overhead watering. Monitor regularly during warm, humid weather. Remove diseased plants promptly.',
            'Leaf Spot': 'Practice crop rotation. Use disease-resistant varieties. Water at soil level. Remove plant debris. Avoid working with plants when wet.',
            'Rust': 'Choose resistant varieties. Ensure proper spacing. Water early in morning. Remove infected plant material. Keep area free of weeds.',
            'Early Blight': 'Practice crop rotation (3-year minimum). Use certified disease-free seeds. Mulch to prevent soil splash. Monitor closely during growing season.',
            'Anthracnose': 'Use resistant varieties. Practice crop rotation. Maintain clean tools. Remove infected plant material immediately. Ensure proper drainage.',
            'Downy Mildew': 'Improve air circulation. Reduce humidity through proper ventilation. Use resistant varieties. Avoid overhead irrigation. Remove affected plants early.',
        }
        return prevention.get(disease_name, 'Implement good cultural practices: crop rotation, proper spacing, sanitation, and resistant varieties.')
    
    @staticmethod
    def get_animal_treatment(disease_name: str) -> str:
        """Get treatment recommendations for animal disease/pest"""
        treatments = {
            'Tick Infestation': 'Use approved acaricide treatments (ivermectin, permethrin). Apply topical anti-tick medications. Consult veterinarian for proper dosage. May require repeated applications every 2-4 weeks.',
            'Mite Infestation': 'Administer anti-mite medications per veterinary guidance. Apply topical treatments if available. Provide supportive care. May require multiple treatments over weeks.',
            'Foot and Mouth Disease': 'IMMEDIATE veterinary care required. Contact animal health authorities. Isolate infected animals. Practice strict biosecurity. Disinfect facilities and equipment.',
            'Mastitis': 'Administer antibiotics as prescribed by veterinarian. Perform frequent milking/drainage. Apply warm compress before milking. Pain management. May require systemic antibiotics.',
            'Scabies': 'Use approved acaricides (sulfur dips, injectable solutions). Repeat treatment as recommended (typically every 10-14 days). Treat all contact animals. Disinfect housing.',
            'Coccidiosis': 'Administer anticoccidial medication (amprolium, sulfamethoxazole). Ensure clean water and feed. Improve sanitation. May use preventive medications in young animals.',
            'Bloat': 'EMERGENCY treatment required. Contact veterinarian immediately. May need trocar puncture or decompression. Provide mineral oil or probiotics. Monitor closely for shock.',
        }
        return treatments.get(disease_name, 'Consult with veterinarian for proper diagnosis and treatment plan.')
    
    @staticmethod
    def get_animal_prevention(disease_name: str) -> str:
        """Get prevention recommendations for animal disease/pest"""
        prevention = {
            'Tick Infestation': 'Regular grooming and inspection. Use preventative tick collars or medications. Maintain clean housing and pasture. Check animals daily during tick season. Rotate pastures.',
            'Mite Infestation': 'Maintain good hygiene in housing. Regular parasite screening. Use preventative treatments. Separate infected animals. Keep bedding clean and dry.',
            'Foot and Mouth Disease': 'Maintain strict biosecurity. Screen animals before introduction. Control movements. Use quarantine procedures. Consult authorities on vaccination protocols.',
            'Mastitis': 'Maintain proper milking hygiene. Regular udder cleaning. Inspect for abnormalities. Use clean equipment. Ensure proper nutrition and avoid stress. Dry cow therapy if recommended.',
            'Scabies': 'Regular inspection for symptoms. Quarantine new arrivals. Maintain clean housing. Avoid crowding. Provide preventative treatments as recommended by veterinarian.',
            'Coccidiosis': 'Maintain excellent sanitation. Avoid overcrowding. Provide clean water and feed. Use bedding management to reduce moisture. Implement preventative medication protocols for young stock.',
            'Bloat': 'Provide gradual diet changes. Avoid feeding on wet pasture. Ensure proper pasture variety. Provide bloat drench before grazing. Monitor animals closely. Avoid overeating concentrated feeds.',
        }
        return prevention.get(disease_name, 'Implement good management practices: proper nutrition, hygiene, regular monitoring, and stress reduction.')
    
    @staticmethod
    def detect(image_file, subject_type: str) -> dict:
        """Main detection method"""
        if subject_type == 'plant':
            return MockMLDetector.detect_plant_disease(image_file)
        elif subject_type == 'animal':
            return MockMLDetector.detect_animal_disease(image_file)
        else:
            raise ValueError("subject_type must be 'plant' or 'animal'")
