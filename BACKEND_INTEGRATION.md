# Backend Integration Guide - BioGuard AI

This guide explains how to integrate the BioGuard AI frontend with your Django REST API backend.

## Frontend Ready

The frontend is fully built and ready to connect to your backend API. No additional frontend changes are needed - just update the API URL and the API endpoints.

## Environment Configuration

### 1. Set API Base URL

Create or update `.env.local` file in the project root:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Required API Endpoints

Your Django backend should implement these endpoints:

### Authentication Endpoints

#### 1. Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123"
}

Response: 200 OK
{
  "id": "user-id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "access_token": "jwt-token"
}
```

#### 2. Login User
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "id": "user-id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "access_token": "jwt-token"
}
```

#### 3. Get Current User
```
GET /api/auth/me
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": "user-id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```

### Detection Endpoints

#### 4. Submit Image for Detection
```
POST /api/detect/
Content-Type: multipart/form-data
Authorization: Bearer <access_token>

Form Data:
- file: <binary image file>
- subject_type: "plant" | "animal"

Response: 200 OK
{
  "id": "scan-id",
  "disease": "Powdery Mildew",
  "confidence": 92.5,
  "severity": "medium",
  "subject_type": "plant",
  "treatment": "Apply sulfur-based fungicide...",
  "prevention": "Maintain adequate spacing...",
  "affected_plants": ["Roses", "Tomatoes"],
  "affected_animals": null,
  "timestamp": "2024-04-06T12:00:00Z"
}
```

### Scan History Endpoints

#### 5. Get User's Scans
```
GET /api/scans/
Authorization: Bearer <access_token>

Query Parameters:
- subject_type: "plant" | "animal" (optional)
- disease: "disease_name" (optional)
- page: 1 (optional, for pagination)
- limit: 20 (optional)

Response: 200 OK
{
  "count": 42,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "scan-id",
      "disease": "Powdery Mildew",
      "confidence": 92.5,
      "severity": "medium",
      "subject_type": "plant",
      "date": "2024-04-06T12:00:00Z",
      "image_url": "https://..."
    },
    ...
  ]
}
```

#### 6. Get Single Scan
```
GET /api/scans/{id}/
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": "scan-id",
  "disease": "Powdery Mildew",
  "confidence": 92.5,
  "severity": "medium",
  "subject_type": "plant",
  "treatment": "Apply sulfur-based fungicide...",
  "prevention": "Maintain adequate spacing...",
  "affected_plants": ["Roses", "Tomatoes"],
  "affected_animals": null,
  "date": "2024-04-06T12:00:00Z",
  "image_url": "https://..."
}
```

#### 7. Delete Scan
```
DELETE /api/scans/{id}/
Authorization: Bearer <access_token>

Response: 204 No Content
```

### User Profile Endpoints

#### 8. Get User Profile
```
GET /api/users/profile/
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": "user-id",
  "email": "user@example.com",
  "name": "John Doe",
  "total_scans": 42,
  "plant_scans": 28,
  "animal_scans": 14,
  "joined_date": "2024-01-15"
}
```

#### 9. Update User Profile
```
PUT /api/users/profile/
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "name": "John Smith",
  "email": "john.smith@example.com"
}

Response: 200 OK
{
  "id": "user-id",
  "email": "john.smith@example.com",
  "name": "John Smith"
}
```

#### 10. Change Password
```
POST /api/users/change-password/
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "old_password": "currentpassword",
  "new_password": "newpassword123"
}

Response: 200 OK
{
  "message": "Password changed successfully"
}
```

### Admin Endpoints

#### 11. Get System Statistics
```
GET /api/admin/stats/
Authorization: Bearer <admin-token>

Response: 200 OK
{
  "total_users": 150,
  "total_scans": 2345,
  "average_confidence": 89.5,
  "most_common_diseases": [
    {"disease": "Powdery Mildew", "count": 156},
    {"disease": "Leaf Spot", "count": 98}
  ],
  "most_analyzed_species": [
    {"species": "Tomato", "count": 267}
  ]
}
```

#### 12. Get All Scans (Admin)
```
GET /api/admin/scans/
Authorization: Bearer <admin-token>

Query Parameters:
- user_id: "user-id" (optional)
- disease: "disease_name" (optional)
- page: 1 (optional)
- limit: 50 (optional)

Response: 200 OK
{
  "count": 2345,
  "results": [...]
}
```

#### 13. Get Disease Database
```
GET /api/admin/diseases/
Authorization: Bearer <admin-token>

Response: 200 OK
{
  "results": [
    {
      "id": "disease-id",
      "name": "Powdery Mildew",
      "treatment": "Apply sulfur...",
      "prevention": "Maintain spacing...",
      "affected_species": ["Roses", "Tomatoes"],
      "severity": "medium"
    },
    ...
  ]
}
```

#### 14. Create Disease
```
POST /api/admin/diseases/
Content-Type: application/json
Authorization: Bearer <admin-token>

{
  "name": "New Disease",
  "treatment": "Treatment steps",
  "prevention": "Prevention steps",
  "affected_species": ["Species1", "Species2"],
  "severity": "high"
}

Response: 201 Created
{
  "id": "disease-id",
  "name": "New Disease",
  ...
}
```

#### 15. Update Disease
```
PUT /api/admin/diseases/{id}/
Content-Type: application/json
Authorization: Bearer <admin-token>

{
  "name": "Updated Disease",
  "treatment": "Updated treatment",
  ...
}

Response: 200 OK
```

#### 16. Delete Disease
```
DELETE /api/admin/diseases/{id}/
Authorization: Bearer <admin-token>

Response: 204 No Content
```

## Implementation Notes

### Authentication Flow

1. User registers/logs in on frontend
2. Backend returns JWT access token
3. Frontend stores token in localStorage
4. All subsequent requests include token in Authorization header
5. Token automatically added by API client

### Error Handling

Frontend expects standard HTTP error responses:

```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

### Image Upload

- Maximum file size: 5MB
- Supported formats: JPG, PNG, WebP
- Images are sent as multipart/form-data
- Backend should validate and store images

### Response Format

All successful responses should follow:

```json
{
  "success": true,
  "data": {...},
  "message": "Success message"
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error code",
  "message": "Error message"
}
```

## Django Implementation Example

Here's a quick example of implementing the detection endpoint:

```python
# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detect_disease(request):
    image = request.FILES['file']
    subject_type = request.data['subject_type']
    
    # Your ML model detection logic here
    result = run_detection_model(image, subject_type)
    
    # Save scan to database
    scan = Scan.objects.create(
        user=request.user,
        disease=result['disease'],
        confidence=result['confidence'],
        severity=result['severity'],
        subject_type=subject_type,
        image=image,
        treatment=result['treatment'],
        prevention=result['prevention']
    )
    
    return Response({
        'id': str(scan.id),
        'disease': scan.disease,
        'confidence': scan.confidence,
        'severity': scan.severity,
        'subject_type': scan.subject_type,
        'treatment': scan.treatment,
        'prevention': scan.prevention,
        'timestamp': scan.created_at
    })
```

## Testing the Integration

1. Start your Django backend on port 8000
2. Update `.env.local` with correct API URL
3. Start the Next.js frontend: `pnpm dev`
4. Register a new account
5. Test image upload and detection
6. Verify scans are saved in your database
7. Check admin dashboard statistics

## CORS Configuration

If your frontend and backend are on different domains, configure CORS:

```python
# Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com",
]
```

## Security Considerations

1. Always use HTTPS in production
2. Implement rate limiting on detection endpoint
3. Validate all file uploads
4. Use secure JWT secret keys
5. Implement CSRF protection
6. Sanitize all user inputs
7. Implement access control for admin endpoints

## Database Models Required

```python
# Core models needed
- User (Django auth)
- Scan
  - user (ForeignKey)
  - disease
  - confidence
  - severity
  - subject_type
  - image
  - treatment
  - prevention
  - created_at

- Disease
  - name
  - treatment
  - prevention
  - affected_species (JSON)
  - severity
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] API URL updated for production
- [ ] Database migrations run
- [ ] Static files collected
- [ ] CORS configured correctly
- [ ] JWT secret key changed
- [ ] SSL/HTTPS enabled
- [ ] Rate limiting implemented
- [ ] Logging configured
- [ ] Error tracking enabled
- [ ] API documentation ready

## Support

For issues with integration:
1. Check API error responses
2. Review browser console for errors
3. Check Django server logs
4. Verify request format matches specification
5. Ensure authentication token is valid

---

**Ready to integrate? Start with the authentication endpoints and work your way up!**
