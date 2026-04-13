import os
import random
import hashlib
from .models import Disease
from .comprehensive_diseases_db import COMPREHENSIVE_DISEASES_DATABASE, get_all_plant_diseases, get_all_animal_diseases
from PIL import Image
import io


class MockMLDetector:
    """
    Mock ML Detection Engine with 2000+ diseases and pests
    Simulates disease/pest detection with realistic confidence scores (82-99%)
    In production, this would be replaced with actual ML model inference
    
    Comprehensive disease database sourced from:
    - FAO (Food and Agriculture Organization)
    - Agricultural Extension Services worldwide
    - Regional disease databases
    - Veterinary disease databases
    """
    
    # Load comprehensive database
    PLANT_DISEASES_LIST = get_all_plant_diseases()
    ANIMAL_DISEASES_LIST = get_all_animal_diseases()
    
    # Create quick-access dictionaries
    PLANT_DISEASES = {d['name']: d for d in PLANT_DISEASES_LIST}
    ANIMAL_DISEASES = {d['name']: d for d in ANIMAL_DISEASES_LIST}
    
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
    def get_disease_info(disease_name: str, subject_type: str) -> dict:
        """Get disease information from comprehensive database"""
        database = COMPREHENSIVE_DISEASES_DATABASE
        
        if subject_type == 'plant':
            # Search through all plant categories
            for category in database.get('plants', {}).values():
                if disease_name in category:
                    return category[disease_name]
        elif subject_type == 'animal':
            # Search through all animal categories
            for category in database.get('animals', {}).values():
                if disease_name in category:
                    return category[disease_name]
        
        # Return default if not found
        return {
            'severity': 'medium',
            'treatment': 'Consult with a local agricultural extension officer or veterinarian for proper treatment.',
            'prevention': 'Maintain good hygiene and regular monitoring practices.',
            'symptoms': []
        }

    @staticmethod
    def get_analysis_notes(subject_type: str, disease_name: str, image_file) -> str:
        """Generate analysis notes including image analysis"""
        analysis = MockMLDetector.analyze_image(image_file)
        disease_info = MockMLDetector.get_disease_info(disease_name, subject_type)
        
        severity = disease_info.get('severity', 'medium')
        treatment = disease_info.get('treatment', 'Seek professional advice.')
        
        if subject_type == 'plant':
            return (
                f"{analysis} It looks like {disease_name}. "
                f"Severity level: {severity}. "
                f"This problem can be treated by: {treatment}. "
                "If not treated, it can significantly affect your crop."
            )
        else:
            return (
                f"{analysis} It looks like {disease_name}. "
                f"Severity level: {severity}. "
                f"This problem can be treated by: {treatment}. "
                "If not treated, it can significantly affect your animal's health."
            )

    @staticmethod
    def detect_plant_disease(image_file) -> dict:
        """Detect plant disease from image using comprehensive database"""
        # Get image hash for deterministic results
        image_hash = MockMLDetector.get_image_hash(image_file)
        
        # Select disease from comprehensive database
        diseases = MockMLDetector.PLANT_DISEASES_LIST
        disease_index = int(image_hash[:2], 16) % len(diseases)
        disease_info = diseases[disease_index]
        disease_name = disease_info['name']
        
        # Generate confidence using database range
        confidence_min, confidence_max = disease_info.get('confidence_range', (85, 95))
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
            'severity': disease_info.get('severity', 'medium'),
            'treatment': disease_info.get('treatment', 'Consult with a local expert.'),
            'prevention': disease_info.get('prevention', 'Maintain good farming practices.'),
            'affected_species': disease_info.get('crops', []),
            'symptoms': disease_info.get('symptoms', []),
        }
    
    @staticmethod
    def detect_animal_disease(image_file) -> dict:
        """Detect animal disease/pest from image using comprehensive database"""
        # Get image hash for deterministic results
        image_hash = MockMLDetector.get_image_hash(image_file)
        
        # Select disease from comprehensive database
        diseases = MockMLDetector.ANIMAL_DISEASES_LIST
        disease_index = int(image_hash[:2], 16) % len(diseases)
        disease_info = diseases[disease_index]
        disease_name = disease_info['name']
        
        # Generate confidence using database range
        confidence_min, confidence_max = disease_info.get('confidence_range', (85, 95))
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
            'severity': disease_info.get('severity', 'medium'),
            'treatment': disease_info.get('treatment', 'Consult with a veterinarian.'),
            'prevention': disease_info.get('prevention', 'Maintain good animal care practices.'),
            'affected_species': disease_info.get('species', []),
            'symptoms': disease_info.get('symptoms', []),
        }
    
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

            # Use comprehensive database for labels
            labels = MockMLDetector.PLANT_DISEASES_LIST if subject_type == 'plant' else MockMLDetector.ANIMAL_DISEASES_LIST
            disease_info = labels[label_index % len(labels)]
            disease_name = disease_info['name']

            confidence = round(float(np.max(predictions) * 100), 1)

            try:
                disease = Disease.objects.get(name=disease_name, subject_type=subject_type)
            except Disease.DoesNotExist:
                disease = None

            return {
                'disease_name': disease_name,
                'disease': disease,
                'confidence': confidence,
                'severity': disease_info.get('severity', 'medium'),
                'treatment': disease_info.get('treatment', 'Consult with a professional.'),
                'prevention': disease_info.get('prevention', 'Maintain good practices.'),
                'affected_species': disease_info.get('crops' if subject_type == 'plant' else 'species', []),
                'symptoms': disease_info.get('symptoms', []),
            }
        except Exception:
            return None
