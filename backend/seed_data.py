#!/usr/bin/env python
"""
Seed script to populate initial database with plants, animals, and diseases
Run: python manage.py shell < seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Plant, Animal, Disease
from django.contrib.auth.models import User

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✓ Created superuser: admin / admin123")

# Create plants
plants_data = [
    {'name': 'Tomato', 'scientific_name': 'Solanum lycopersicum'},
    {'name': 'Potato', 'scientific_name': 'Solanum tuberosum'},
    {'name': 'Corn', 'scientific_name': 'Zea mays'},
    {'name': 'Wheat', 'scientific_name': 'Triticum aestivum'},
    {'name': 'Rice', 'scientific_name': 'Oryza sativa'},
    {'name': 'Bean', 'scientific_name': 'Phaseolus vulgaris'},
    {'name': 'Pepper', 'scientific_name': 'Capsicum annuum'},
    {'name': 'Cucumber', 'scientific_name': 'Cucumis sativus'},
    {'name': 'Grape', 'scientific_name': 'Vitis vinifera'},
    {'name': 'Rose', 'scientific_name': 'Rosa sp.'},
]

for plant_data in plants_data:
    if not Plant.objects.filter(name=plant_data['name']).exists():
        Plant.objects.create(**plant_data)
        print(f"✓ Created plant: {plant_data['name']}")

# Create animals
animals_data = [
    {'name': 'Holstein Cattle', 'species': 'cattle'},
    {'name': 'Angus Cattle', 'species': 'cattle'},
    {'name': 'Merino Sheep', 'species': 'sheep'},
    {'name': 'Boer Goat', 'species': 'goat'},
    {'name': 'Thoroughbred Horse', 'species': 'horse'},
    {'name': 'Large Black Pig', 'species': 'pig'},
    {'name': 'Rhode Island Red Chicken', 'species': 'poultry'},
    {'name': 'German Shepherd Dog', 'species': 'dog'},
    {'name': 'Persian Cat', 'species': 'cat'},
]

for animal_data in animals_data:
    key = f"{animal_data['name']}_{animal_data['species']}"
    if not Animal.objects.filter(name=animal_data['name'], species=animal_data['species']).exists():
        Animal.objects.create(**animal_data)
        print(f"✓ Created animal: {animal_data['name']}")

# Create plant diseases
plant_diseases = [
    {
        'name': 'Powdery Mildew',
        'subject_type': 'plant',
        'scientific_name': 'Erysiphaceae',
        'description': 'Fungal disease that appears as white powder on plant surfaces',
        'symptoms': 'White powdery coating on leaves, stems, and flowers. Leaves may yellow and drop.',
        'treatment': 'Apply sulfur-based fungicide, improve air circulation, remove affected leaves',
        'prevention': 'Maintain spacing, ensure ventilation, avoid overhead watering',
        'severity': 'medium',
        'affected_plants_names': ['Roses', 'Tomatoes', 'Grapes', 'Cucumbers', 'Squash'],
    },
    {
        'name': 'Leaf Spot',
        'subject_type': 'plant',
        'scientific_name': 'Various fungi',
        'description': 'Fungal disease causing brown or black spots on leaves',
        'symptoms': 'Brown or black spots with yellow halos on leaves. Spots may enlarge and merge.',
        'treatment': 'Remove affected leaves, apply fungicide, improve drainage',
        'prevention': 'Avoid overhead watering, ensure proper spacing, remove debris',
        'severity': 'low',
        'affected_plants_names': ['Tomatoes', 'Peppers', 'Lettuce', 'Spinach'],
    },
    {
        'name': 'Rust',
        'subject_type': 'plant',
        'scientific_name': 'Pucciniales',
        'description': 'Fungal disease causing rust-colored pustules on leaves',
        'symptoms': 'Rust-colored powder on undersides of leaves, yellow spots on upper surface',
        'treatment': 'Apply fungicide, remove infected leaves, improve ventilation',
        'prevention': 'Choose resistant varieties, ensure good air circulation, remove infected material',
        'severity': 'medium',
        'affected_plants_names': ['Beans', 'Wheat', 'Corn', 'Roses'],
    },
    {
        'name': 'Early Blight',
        'subject_type': 'plant',
        'scientific_name': 'Alternaria solani',
        'description': 'Fungal disease affecting tomato and potato plants',
        'symptoms': 'Target-like lesions with concentric rings on lower leaves, yellowing and death',
        'treatment': 'Remove lower infected leaves, apply fungicide, water at soil level only',
        'prevention': 'Crop rotation, use resistant varieties, mulch to prevent soil splash',
        'severity': 'high',
        'affected_plants_names': ['Tomatoes', 'Potatoes'],
    },
]

for disease_data in plant_diseases:
    if not Disease.objects.filter(name=disease_data['name']).exists():
        affected_plants_names = disease_data.pop('affected_plants_names')
        disease = Disease.objects.create(**disease_data)
        
        # Add affected plants
        for plant_name in affected_plants_names:
            plant = Plant.objects.filter(name=plant_name).first()
            if plant:
                disease.affected_plants.add(plant)
        
        print(f"✓ Created disease: {disease_data['name']}")

# Create animal diseases
animal_diseases = [
    {
        'name': 'Tick Infestation',
        'subject_type': 'animal',
        'scientific_name': 'Acari',
        'description': 'External parasite infestation in livestock and pets',
        'symptoms': 'Visible ticks on skin, itching, hair loss, possible anemia',
        'treatment': 'Use acaricide treatments (ivermectin, permethrin), topical medications',
        'prevention': 'Regular inspection, preventative medications, clean housing, pasture rotation',
        'severity': 'medium',
        'affected_animals_species': ['cattle', 'sheep', 'goat', 'horse', 'dog'],
    },
    {
        'name': 'Mite Infestation',
        'subject_type': 'animal',
        'scientific_name': 'Acaridae',
        'description': 'Microscopic parasite causing skin disease',
        'symptoms': 'Severe itching, scabs, hair loss, skin thickening and wrinkles',
        'treatment': 'Anti-mite medications, topical treatments, supportive care',
        'prevention': 'Good hygiene, regular inspections, quarantine new arrivals, clean bedding',
        'severity': 'high',
        'affected_animals_species': ['cattle', 'sheep', 'poultry', 'dog'],
    },
    {
        'name': 'Mastitis',
        'subject_type': 'animal',
        'scientific_name': 'Streptococcus agalactiae',
        'description': 'Inflammation of mammary glands in dairy animals',
        'symptoms': 'Swollen udders, hot painful teats, discolored milk, fever',
        'treatment': 'Antibiotics, frequent milking/drainage, warm compress, pain management',
        'prevention': 'Proper milking hygiene, clean equipment, good nutrition, stress reduction',
        'severity': 'high',
        'affected_animals_species': ['cattle', 'sheep', 'goat'],
    },
    {
        'name': 'Coccidiosis',
        'subject_type': 'animal',
        'scientific_name': 'Coccidia',
        'description': 'Parasitic intestinal disease affecting young stock',
        'symptoms': 'Diarrhea (sometimes bloody), weakness, poor growth, loss of appetite',
        'treatment': 'Anticoccidial medications (amprolium, sulfamethoxazole), clean water',
        'prevention': 'Good sanitation, avoid overcrowding, clean water, preventative medication',
        'severity': 'medium',
        'affected_animals_species': ['poultry', 'cattle', 'sheep'],
    },
]

for disease_data in animal_diseases:
    if not Disease.objects.filter(name=disease_data['name']).exists():
        affected_animals_species = disease_data.pop('affected_animals_species')
        disease = Disease.objects.create(**disease_data)
        
        # Add affected animals
        for species in affected_animals_species:
            animals = Animal.objects.filter(species=species)
            for animal in animals:
                disease.affected_animals.add(animal)
        
        print(f"✓ Created disease: {disease_data['name']}")

print("\n✅ Database seeding completed successfully!")
