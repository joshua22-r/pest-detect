export const APP_NAME = 'PlantGuard';
export const APP_DESCRIPTION = 'AI-powered plant disease detection system';

export const DISEASES = [
  { id: 1, name: 'Powdery Mildew', confidence: 95 },
  { id: 2, name: 'Leaf Spot', confidence: 92 },
  { id: 3, name: 'Rust', confidence: 88 },
  { id: 4, name: 'Blight', confidence: 90 },
  { id: 5, name: 'Mosaic Virus', confidence: 87 },
  { id: 6, name: 'Healthy', confidence: 98 },
];

export const ROUTES = {
  HOME: '/',
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  PREDICT: '/predict',
  HISTORY: '/history',
  PROFILE: '/profile',
  ADMIN: '/admin/dashboard',
} as const;

export const ROLE_PERMISSIONS = {
  user: ['predict', 'history', 'profile'],
  admin: ['predict', 'history', 'profile', 'admin'],
  expert: ['predict', 'history', 'profile', 'admin', 'validate'],
} as const;
