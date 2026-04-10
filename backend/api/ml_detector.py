import os
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
    
    # Plant diseases and pests database
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
        'Aphid Infestation': {
            'confidence_range': (84, 91),
            'severity': 'medium',
            'affected_species': ['Tomatoes', 'Cabbage', 'Roses', 'Beans'],
        },
        'Spider Mites': {
            'confidence_range': (86, 93),
            'severity': 'medium',
            'affected_species': ['Tomatoes', 'Peppers', 'Cucumbers', 'Melons'],
        },
        'Whitefly Infestation': {
            'confidence_range': (85, 92),
            'severity': 'medium',
            'affected_species': ['Tomatoes', 'Cabbage', 'Eggplant', 'Cucumber'],
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
        'Worm Infection': {
            'confidence_range': (85, 93),
            'severity': 'medium',
            'affected_species': ['Cattle', 'Sheep', 'Goats', 'Pigs'],
        },
        'Skin Infection': {
            'confidence_range': (86, 94),
            'severity': 'medium',
            'affected_species': ['Cattle', 'Sheep', 'Pigs', 'Dogs'],
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
    def analyze_image(image_file) -> str:
        """Perform a simple visual analysis of the image"""
        try:
            image_file.seek(0)
            image = Image.open(image_file)
            grayscale = image.convert('L')
            histogram = grayscale.histogram()
            total_pixels = sum(histogram)
            if total_pixels == 0:
                return 'I checked the image and the visual analysis is complete.'
            brightness = sum(i * count for i, count in enumerate(histogram)) / total_pixels
            if brightness < 40:
                return 'The picture is a bit dark, but I still found signs of a problem.'
            if brightness > 220:
                return 'The picture is very bright, but I still found signs of a problem.'
            return 'The picture is clear enough for a basic analysis.'
        except Exception:
            return 'I checked the image and a quick visual analysis was completed.'

    @staticmethod
    def get_plant_cause(disease_name: str) -> str:
        causes = {
            'Powdery Mildew': 'a fungus that makes a white powder on leaves, stems, or flowers',
            'Leaf Spot': 'a fungus or bacteria that makes dark spots on leaves',
            'Rust': 'a fungus that makes orange or brown dust on leaves',
            'Early Blight': 'a fungus that attacks leaves and stems of tomatoes and potatoes',
            'Anthracnose': 'a fungus that causes dark sunken spots on fruit and leaves',
            'Downy Mildew': 'a fungus that causes yellow patches and fuzzy growth under leaves',
            'Aphid Infestation': 'small insects that suck sap from leaves and stems',
            'Spider Mites': 'tiny mites that feed on plant cells and make leaves look dusty',
            'Whitefly Infestation': 'small white insects that suck juice and make plants weak',
        }
        return causes.get(
            disease_name,
            'a pest or disease that damages leaves, stems, or fruit and makes the plant weak'
        )

    @staticmethod
    def get_animal_cause(disease_name: str) -> str:
        causes = {
            'Tick Infestation': 'small ticks that bite and suck blood from the animal',
            'Mite Infestation': 'tiny mites that live on the skin and cause itching',
            'Foot and Mouth Disease': 'a virus that causes sore mouths and feet',
            'Mastitis': 'an infection in the udder that makes milking painful',
            'Scabies': 'mites that make the skin itchy and scabby',
            'Coccidiosis': 'tiny parasites in the gut that cause diarrhea and weakness',
            'Bloat': 'too much gas in the stomach, making the animal uncomfortable',
            'Worm Infection': 'worms in the gut that make the animal weak and thin',
            'Skin Infection': 'germs on the skin that make sores or hair loss',
        }
        return causes.get(
            disease_name,
            'an infection or pest problem that makes the animal weak, itchy, or sick'
        )

    @staticmethod
    def get_analysis_notes(subject_type: str, disease_name: str, image_file) -> str:
        analysis = MockMLDetector.analyze_image(image_file)
        if subject_type == 'plant':
            cause = MockMLDetector.get_plant_cause(disease_name)
            return (
                f"{analysis} It looks like {disease_name}. "
                f"This problem is caused by {cause}. "
                "If it is not treated, it can make the plant weak and lower your harvest."
            )

        cause = MockMLDetector.get_animal_cause(disease_name)
        return (
            f"{analysis} It looks like {disease_name}. "
            f"This problem is caused by {cause}. "
            "If it is not treated, it can make the animal weak and stop it from eating well."
        )

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
            'Powdery Mildew': 'Spray with sulfur or a mildew treatment. Remove infected leaves. Keep plants dry and give good air flow.',
            'Leaf Spot': 'Remove spotted leaves and use copper or sulfur spray. Water at the base, not over the leaves.',
            'Rust': 'Remove rusty leaves and treat with a fungicide made for rust. Keep leaves dry while watering.',
            'Early Blight': 'Remove lower infected leaves and spray with a protective fungicide. Keep soil from splashing on leaves.',
            'Anthracnose': 'Remove infected fruit and leaves. Use copper spray and keep the area dry.',
            'Downy Mildew': 'Remove infected parts and treat with a mildew spray. Increase air flow and reduce humidity.',
            'Aphid Infestation': 'Spray with insecticidal soap or neem oil. Wash the insects off with water and repeat after a few days.',
            'Spider Mites': 'Use a miticide or strong water spray. Keep the plant cool and repeat treatment as needed.',
            'Whitefly Infestation': 'Spray with water, insecticidal soap, or neem oil. Remove badly damaged leaves and keep the plant clean.',
        }
        return treatments.get(
            disease_name,
            'Remove the damaged parts, keep the area clean, and use the right spray or treatment advised by a local expert.'
        )
    
    @staticmethod
    def get_plant_prevention(disease_name: str) -> str:
        """Get prevention recommendations for plant disease"""
        prevention = {
            'Powdery Mildew': 'Give plants space for air flow. Do not wet leaves. Check for white powder often and remove it early.',
            'Leaf Spot': 'Keep plants spaced apart, clean up fallen leaves, and water at the soil, not on leaves.',
            'Rust': 'Choose strong varieties. Keep plant leaves dry and remove dead material quickly.',
            'Early Blight': 'Rotate crops, use clean seed, and keep leaves from touching wet soil.',
            'Anthracnose': 'Keep the plant area clean, use good drainage, and do not let leaves stay wet.',
            'Downy Mildew': 'Place plants where air moves well. Do not water from above and remove sick leaves quickly.',
            'Aphid Infestation': 'Check plants often, use natural sprays, and remove weak plants that attract pests.',
            'Spider Mites': 'Keep humidity higher, inspect plants regularly, and remove dust or webs from leaves.',
            'Whitefly Infestation': 'Use sticky traps, remove weak plants, and keep leaves clean and dry.',
        }
        return prevention.get(
            disease_name,
            'Keep plants strong with clean soil, good spacing, clean water, and regular checks for pests or disease.'
        )
    
    @staticmethod
    def get_animal_treatment(disease_name: str) -> str:
        """Get treatment recommendations for animal disease/pest"""
        treatments = {
            'Tick Infestation': 'Use approved tick drops or sprays. Remove ticks by hand when possible and ask a vet for the right medicine.',
            'Mite Infestation': 'Treat with mite medicine or dips. Clean bedding and treat all animals in contact.',
            'Foot and Mouth Disease': 'Isolate sick animals and call a vet immediately. Clean the area and do not move the herd.',
            'Mastitis': 'Keep the udder clean and use medicine from a vet. Milk the animal regularly and use warm compresses.',
            'Scabies': 'Use skin treatment medicine. Clean the animal house and treat all animals that touched the sick one.',
            'Coccidiosis': 'Give medicine for gut parasites. Keep feed and water clean and change bedding often.',
            'Bloat': 'This is an emergency. Contact a vet quickly and do not wait. The animal needs help to release gas.',
            'Worm Infection': 'Give deworming medicine as directed. Keep grazing areas clean and dry.',
            'Skin Infection': 'Clean the affected skin and use medicine from a vet. Keep the area dry and separate sick animals.',
        }
        return treatments.get(
            disease_name,
            'If not listed, keep animals clean, feed them well, check them every day, and call your local vet for the best treatment plan.'
        )
    
    @staticmethod
    def get_animal_prevention(disease_name: str) -> str:
        """Get prevention recommendations for animal disease/pest"""
        prevention = {
            'Tick Infestation': 'Check animals often for ticks. Keep housing clean. Use prevention drops or collars regularly.',
            'Mite Infestation': 'Keep bedding clean and dry. Examine animals often and avoid crowding.',
            'Foot and Mouth Disease': 'Do not mix new animals with the herd before checking them. Keep visitors and vehicles away from your farm.',
            'Mastitis': 'Wash hands before milking. Keep udders clean and dry. Use clean tools and reduce stress.',
            'Scabies': 'Keep animals clean and separate sick animals. Check for itching and scabs often.',
            'Coccidiosis': 'Keep young animals in a dry, clean place. Use clean feed and water and avoid overcrowding.',
            'Bloat': 'Feed slowly and avoid too much wet grass at once. Give good roughage and watch animals after grazing.',
            'Worm Infection': 'Use clean water and keep grazing areas dry. Deworm animals when needed.',
            'Skin Infection': 'Keep skin clean and dry. Separate sick animals and avoid sharing bedding.',
        }
        return prevention.get(
            disease_name,
            'If this is not listed, keep animals clean, feed them well, separate sick animals, and contact your local vet or animal health officer for advice.'
        )
    
    @staticmethod
    def detect(image_file, subject_type: str, mode: str = 'mock') -> dict:
        """Main detection method"""
        if mode == 'real':
            real_result = RealMLDetector.detect(image_file, subject_type)
            if real_result is not None:
                real_result['notes'] = MockMLDetector.get_analysis_notes(subject_type, real_result['disease_name'], image_file)
                return real_result

        if subject_type == 'plant':
            result = MockMLDetector.detect_plant_disease(image_file)
        elif subject_type == 'animal':
            result = MockMLDetector.detect_animal_disease(image_file)
        else:
            raise ValueError("subject_type must be 'plant' or 'animal'")

        result['notes'] = MockMLDetector.get_analysis_notes(subject_type, result['disease_name'], image_file)
        return result


class RealMLDetector:
    """Adapter for a real trained model if one is available."""
    MODEL_PATH = os.environ.get('REAL_MODEL_PATH', 'backend/model/pest_model.h5')
    MODEL = None
    LOADED = False

    @classmethod
    def load_model(cls):
        if cls.LOADED:
            return

        cls.LOADED = True
        if not cls.MODEL_PATH or not os.path.exists(cls.MODEL_PATH):
            return

        try:
            import tensorflow as tf
            cls.MODEL = tf.keras.models.load_model(cls.MODEL_PATH)
        except Exception:
            cls.MODEL = None

    @classmethod
    def has_model(cls) -> bool:
        cls.load_model()
        return cls.MODEL is not None

    @classmethod
    def detect(cls, image_file, subject_type: str) -> dict | None:
        cls.load_model()
        if cls.MODEL is None:
            return None

        try:
            import numpy as np
            image_file.seek(0)
            image = Image.open(image_file).convert('RGB')
            input_shape = cls.MODEL.input_shape
            if input_shape and len(input_shape) >= 3:
                height, width = input_shape[1], input_shape[2]
            else:
                height, width = 224, 224

            image = image.resize((width, height))
            image_array = np.asarray(image, dtype=np.float32) / 255.0
            if image_array.ndim == 3:
                image_array = np.expand_dims(image_array, axis=0)

            predictions = cls.MODEL.predict(image_array)
            label_index = int(np.argmax(predictions, axis=-1)[0])

            labels = list(MockMLDetector.PLANT_DISEASES.keys()) if subject_type == 'plant' else list(MockMLDetector.ANIMAL_DISEASES.keys())
            disease_name = labels[label_index % len(labels)]

            disease_info = MockMLDetector.PLANT_DISEASES[disease_name] if subject_type == 'plant' else MockMLDetector.ANIMAL_DISEASES[disease_name]
            confidence = round(float(np.max(predictions) * 100), 1)

            try:
                disease = Disease.objects.get(name=disease_name, subject_type=subject_type)
            except Disease.DoesNotExist:
                disease = None

            return {
                'disease_name': disease_name,
                'disease': disease,
                'confidence': confidence,
                'severity': disease_info['severity'],
                'treatment': MockMLDetector.get_plant_treatment(disease_name) if subject_type == 'plant' else MockMLDetector.get_animal_treatment(disease_name),
                'prevention': MockMLDetector.get_plant_prevention(disease_name) if subject_type == 'plant' else MockMLDetector.get_animal_prevention(disease_name),
                'affected_species': disease_info['affected_species'],
            }
        except Exception:
            return None
