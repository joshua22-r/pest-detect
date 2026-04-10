// Django Backend API Client
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== 'undefined' ? `${window.location.origin}/api` : 'http://localhost:8000/api');

console.log('[API Client] Initialized with API_BASE_URL:', API_BASE_URL);

export interface AuthResponse {
  user: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  access: string;
  refresh: string;
}

export interface UserProfile {
  user: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  user_type: string;
  phone: string;
  location: string;
  bio: string;
  total_scans: number;
}

export interface DetectionResponse {
  id: string;
  user: {
    id: number;
    username: string;
    email: string;
  };
  image: string;
  subject_type: 'plant' | 'animal';
  disease_name: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high';
  treatment: string;
  prevention: string;
  notes: string;
  created_at: string;
}

export interface SystemStats {
  total_scans: number;
  total_users: number;
  plant_scans: number;
  animal_scans: number;
  diseases_detected: number;
  updated_at: string;
}

export class APIError extends Error {
  status?: number;
  data?: any;
  originalError?: string;

  constructor(message: string, status?: number, data?: any, originalError?: string) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
    this.originalError = originalError;
  }
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private setTokens(access: string, refresh: string) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  private clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getToken();

    const headers: HeadersInit = {
      ...options.headers,
    };

    // Only set Content-Type if we're not sending FormData
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        // Token expired, try to refresh
        const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;
        if (refreshToken) {
          try {
            await this.refreshToken(refreshToken);
            // Retry the request with new token
            return this.request<T>(endpoint, options);
          } catch (error) {
            this.clearTokens();
            throw new Error('Session expired. Please login again.');
          }
        }
      }

      if (!response.ok) {
        const contentType = response.headers.get('content-type');
        let errorData: any = {};

        if (contentType?.includes('application/json')) {
          try {
            errorData = await response.json();
          } catch (e) {
            // Ignore JSON parsing errors for error responses
          }
        }

        const errorMessage = errorData.error || errorData.detail || `API error: ${response.status} ${response.statusText}`;
        throw new Error(errorMessage);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/json')) {
        console.log('[API Client] Non-JSON response, returning empty object');
        return {} as T;
      }

      const data = await response.json();
      console.log('[API Client] JSON parsed successfully');
      return data;
    } catch (error) {
      console.error('[API Client] Request failed:', error, { url, options });

      // Create a simple error message
      let errorMessage = 'API request failed';
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        errorMessage = `Failed to fetch API at ${url}. Is the backend running and reachable?`;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      } else if (error && typeof error === 'object') {
        errorMessage = JSON.stringify(error) || 'Unknown error';
      }

      throw new Error(errorMessage);
    }
  }

  // Auth methods
  async register(
    username: string,
    email: string,
    password: string,
    first_name?: string,
    last_name?: string,
    autoLogin: boolean = false
  ): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify({
        username,
        email,
        password,
        first_name: first_name || '',
        last_name: last_name || '',
      }),
    });

    if (autoLogin) {
      this.setTokens(response.access, response.refresh);
    }
    return response;
  }

  async createAdminUser(payload: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    user_type?: string;
    is_staff?: boolean;
  }): Promise<any> {
    return this.request('/admin/users/', {
      method: 'POST',
      body: JSON.stringify({
        username: payload.username,
        email: payload.email,
        password: payload.password,
        first_name: payload.first_name || '',
        last_name: payload.last_name || '',
        user_type: payload.user_type || 'admin',
        is_staff: payload.is_staff ?? true,
      }),
    });
  }

  async login(username: string, password: string): Promise<AuthResponse> {
    console.log('[API Client] Attempting login for:', username);
    console.log('[API Client] API URL:', API_BASE_URL);
    console.log('[API Client] Request payload:', { username, password });

    try {
      const response = await this.request<AuthResponse>('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });

      console.log('[API Client] Login successful, response:', response);
      this.setTokens(response.access, response.refresh);
      return response;
    } catch (error) {
      console.error('[API Client] Login failed:', error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      await this.request('/auth/logout/', { method: 'POST' });
    } finally {
      this.clearTokens();
    }
  }

  async getCurrentUser(): Promise<UserProfile> {
    const response = await this.request<{ user: any; profile: UserProfile }>('/auth/user/');
    return response.profile;
  }

  private async refreshToken(refreshToken: string): Promise<void> {
    const response = await this.request<{ access: string }>('/auth/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh: refreshToken }),
    });

    const newRefreshToken = refreshToken;
    this.setTokens(response.access, newRefreshToken);
  }

  // Prediction/Detection methods
  async predict(image: File, subjectType: 'plant' | 'animal'): Promise<DetectionResponse> {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('subject_type', subjectType);

    return this.request<DetectionResponse>('/predict/', {
      method: 'POST',
      body: formData,
    });
  }

  async getDetectionHistory(): Promise<DetectionResponse[]> {
    return this.request<DetectionResponse[]>('/detections/my_scans/');
  }

  async getPlantScans(): Promise<DetectionResponse[]> {
    return this.request<DetectionResponse[]>('/detections/plant_scans/');
  }

  async getAnimalScans(): Promise<DetectionResponse[]> {
    return this.request<DetectionResponse[]>('/detections/animal_scans/');
  }

  async getDetection(id: string): Promise<DetectionResponse> {
    return this.request<DetectionResponse>(`/detections/${id}/`);
  }

  async deleteDetection(id: string): Promise<void> {
    return this.request<void>(`/detections/${id}/`, {
      method: 'DELETE',
    });
  }

  // Profile methods
  async getProfile(): Promise<UserProfile> {
    return this.request<UserProfile>('/profiles/my_profile/');
  }

  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    return this.request<UserProfile>('/profiles/update_profile/', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Statistics methods
  async getSystemStats(): Promise<SystemStats> {
    return this.request<SystemStats>('/statistics/stats/');
  }

  // Admin methods
  async getAdminStats(): Promise<SystemStats> {
    return this.request<SystemStats>('/admin/stats/');
  }

  async getAdminUsers(): Promise<any[]> {
    return this.request<any[]>('/admin/users/');
  }

  async createAdminUser(data: any): Promise<any> {
    return this.request<any>('/admin/users/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAdminUser(id: string, data: any): Promise<any> {
    return this.request<any>(`/admin/users/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteAdminUser(id: string): Promise<void> {
    return this.request<void>(`/admin/users/${id}/`, {
      method: 'DELETE',
    });
  }

  // Disease methods
  async getPlantDiseases(): Promise<any[]> {
    return this.request<any[]>('/diseases/plant_diseases/');
  }

  async getAnimalDiseases(): Promise<any[]> {
    return this.request<any[]>('/diseases/animal_diseases/');
  }

  async getDiseases(): Promise<any[]> {
    return this.request<any[]>('/diseases/');
  }

  async createDisease(data: any): Promise<any> {
    return this.request<any>('/diseases/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateDisease(id: string, data: any): Promise<any> {
    return this.request<any>(`/diseases/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteDisease(id: string): Promise<void> {
    return this.request<void>(`/diseases/${id}/`, {
      method: 'DELETE',
    });
  }

  // Trial and Subscription Methods
  async getTrialStatus(): Promise<any> {
    return this.request<any>('/trial/status/');
  }

  async incrementTrialAttempts(): Promise<any> {
    return this.request<any>('/trial/increment/', {
      method: 'POST',
    });
  }

  async checkCanPredict(): Promise<any> {
    return this.request<any>('/predict/check/');
  }

  async createSubscription(data: {
    plan: 'daily' | 'weekly' | 'monthly';
    payment_method: 'mtn' | 'airtel';
    mobile_number: string;
  }): Promise<any> {
    return this.request<any>('/subscriptions/create/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async confirmPayment(data: {
    payment_id: string;
    transaction_id?: string;
  }): Promise<any> {
    return this.request<any>('/subscriptions/confirm-payment/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getSubscriptions(): Promise<any[]> {
    return this.request<any[]>('/subscriptions/');
  }

  // Admin methods
  async getAdminPayments(status?: string): Promise<any[]> {
    const url = status ? `/admin/payments/?status=${status}` : '/admin/payments/';
    return this.request<any[]>(url);
  }

  async getAdminSubscriptions(filters?: {
    status?: string;
    paid?: boolean;
  }): Promise<any[]> {
    let url = '/admin/subscriptions/';
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.paid !== undefined) params.append('paid', String(filters.paid));
    if (params.toString()) url += `?${params.toString()}`;
    return this.request<any[]>(url);
  }

  async allowUserAccess(userId: number, allow: boolean): Promise<any> {
    return this.request<any>('/admin/allow-access/', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, allow }),
    });
  }
}

export const apiClient = new APIClient();
