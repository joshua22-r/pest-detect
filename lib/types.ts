// Detection Types
export type SubjectType = 'plant' | 'animal';
export type Severity = 'low' | 'medium' | 'high';

export interface DetectionResult {
  id: string;
  disease: string;
  confidence: number;
  severity: Severity;
  treatment: string;
  prevention: string;
  affectedPlants?: string[];
  affectedAnimals?: string[];
  subjectType: SubjectType;
  timestamp: string;
}

export interface ScanRecord {
  id: string;
  disease: string;
  confidence: number;
  date: string;
  severity: Severity;
  subjectType: SubjectType;
  imageUrl?: string;
}

// Plant Disease Detection
export const PLANT_DISEASES = {
  'Powdery Mildew': {
    treatment: 'Apply sulfur-based fungicide every 7-10 days. Ensure good air circulation by removing affected leaves. Avoid overhead watering. For organic gardening, use baking soda spray (1 tbsp per gallon of water).',
    prevention: 'Maintain adequate spacing between plants. Ensure proper ventilation. Avoid wetting foliage. Remove infected leaves promptly. Water at soil level only.',
    affectedPlants: ['Roses', 'Tomatoes', 'Grapes', 'Cucumbers', 'Beans'],
  },
  'Leaf Spot': {
    treatment: 'Remove infected leaves immediately. Apply copper or sulfur fungicides. Improve air circulation by pruning lower branches. Avoid overhead watering.',
    prevention: 'Water plants at the base only. Ensure good spacing for air circulation. Remove fallen leaves. Sterilize pruning tools between cuts.',
    affectedPlants: ['Roses', 'Tomatoes', 'Strawberries', 'Lettuce'],
  },
  'Rust': {
    treatment: 'Apply sulfur-based fungicides weekly during growing season. Remove infected leaves and destroy them. Improve air circulation.',
    prevention: 'Space plants adequately for air flow. Avoid wetting foliage. Remove infected leaves promptly. Choose resistant varieties.',
    affectedPlants: ['Roses', 'Beans', 'Carnations', 'Hollyhocks'],
  },
};

// Livestock Health & Pest Detection
export const ANIMAL_CONDITIONS = {
  'Tick Infestation': {
    treatment: 'Use approved acaricide treatment. Apply topical anti-tick medications (e.g., ivermectin). Consider dip or spray treatments for severe cases. Consult a veterinarian for proper dosage and application.',
    prevention: 'Regular grooming and inspection. Use preventative tick collars or medications. Maintain clean housing and pasture rotation. Check animals daily during tick season.',
    affectedAnimals: ['Cattle', 'Sheep', 'Goats', 'Horses', 'Dogs'],
  },
  'Mite Infestation': {
    treatment: 'Apply prescribed acaricides to affected areas. Use medicated shampoos or dips. Treat all animals in contact. Consult veterinarian for proper treatment protocol.',
    prevention: 'Regular skin checks and grooming. Maintain clean housing and bedding. Isolate affected animals. Rotate pastures regularly.',
    affectedAnimals: ['Cattle', 'Sheep', 'Goats', 'Pigs', 'Chickens'],
  },
  'Skin Infection': {
    treatment: 'Apply topical antibacterial or antifungal treatments. Isolate animal to prevent spread. Follow veterinary guidance. May require systemic antibiotics.',
    prevention: 'Maintain good hygiene in housing. Regular skin inspections. Proper wound care. Good nutrition and stress management.',
    affectedAnimals: ['Cattle', 'Sheep', 'Horses', 'Pigs', 'Dogs'],
  },
};

export const SUPPORTED_SPECIES = {
  plant: [
    'Roses',
    'Tomatoes',
    'Grapes',
    'Cucumbers',
    'Beans',
    'Strawberries',
    'Lettuce',
    'Peppers',
    'Potatoes',
    'Cabbage',
  ],
  animal: [
    'Cattle',
    'Sheep',
    'Goats',
    'Horses',
    'Pigs',
    'Chickens',
    'Ducks',
    'Turkeys',
    'Dogs',
    'Cats',
  ],
};
