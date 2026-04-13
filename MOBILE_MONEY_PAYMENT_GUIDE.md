# Mobile Money Payment System - Implementation Guide

## Overview
The Pest Detect application now includes a fully integrated mobile money payment system that enables users to purchase subscriptions using Airtel Money. When users complete a subscription purchase, the payment is automatically processed and sent to the target Airtel account (0740345346).

## System Architecture

### Frontend Components
- **components/subscription-modal.tsx**: Handles subscription purchase UI with three steps:
  1. **Plans Selection**: Choose between Daily (3000 UGX), Weekly (10000 UGX), or Monthly (20000 UGX)
  2. **Payment Details**: Select payment method (Airtel) and enter mobile number
  3. **Success Confirmation**: Display successful payment confirmation

### Backend Services
- **backend/api/mobile_money_service.py**: Core service handling Airtel Money API integration
- **backend/api/views.py**: Updated subscription creation endpoint that processes payments
- **backend/api/models.py**: Subscription and Payment models for data persistence

## Backend Implementation

### Mobile Money Service

#### Key Features:
1. **Collection (Customer → App)**: Initiates payment collection from customer's mobile account
2. **Disbursement (App → Target Account)**: Sends collected payment to target Airtel number (0740345346)
3. **Subscription Processing**: Handles complete subscription workflow with payment confirmation

#### Configuration:
```python
class MobileMoneyService:
    # Airtel Money API Configuration
    AIRTEL_BASE_URL = "https://openapi.airtel.africa"
    AIRTEL_API_KEY = getattr(settings, 'AIRTEL_API_KEY', '')
    AIRTEL_API_SECRET = getattr(settings, 'AIRTEL_API_SECRET', '')
    AIRTEL_ENVIRONMENT = getattr(settings, 'AIRTEL_ENVIRONMENT', 'sandbox')
    
    # Target Airtel number for payments
    TARGET_AIRTEL_NUMBER = "0740345346"
```

#### Environment Variables Required:
```
AIRTEL_API_KEY=your_api_key_here
AIRTEL_API_SECRET=your_api_secret_here
AIRTEL_ENVIRONMENT=sandbox  # or 'production'
```

### API Endpoints

#### 1. Create Subscription with Payment
**Endpoint**: `POST /api/subscriptions/create/`

**Request Body**:
```json
{
  "plan": "monthly",
  "payment_method": "airtel",
  "mobile_number": "0740345346"
}
```

**Response (Success)**:
```json
{
  "subscription": {
    "id": "subscription_id",
    "plan": "monthly",
    "amount": 20000,
    "is_paid": true,
    "end_date": "2024-02-15T10:30:00Z"
  },
  "collection_transaction": {
    "status": "success",
    "transaction_id": "txn_collection_123",
    "amount": 20000,
    "currency": "UGX"
  },
  "disbursement_transaction": {
    "status": "success",
    "transaction_id": "txn_disbursement_456",
    "amount": 20000,
    "currency": "UGX"
  },
  "message": "Payment processed successfully! 20000 UGX sent to Airtel number 0740345346",
  "target_number": "0740345346"
}
```

#### 2. Pricing Structure

| Plan | Duration | Price | Currency |
|------|----------|-------|----------|
| Daily | 1 day | 3,000 | UGX |
| Weekly | 7 days | 10,000 | UGX |
| Monthly | 30 days | 20,000 | UGX |

## Frontend Implementation

### Subscription Modal Component

The subscription modal guides users through a 3-step payment process:

#### Step 1: Plan Selection
- Displays available plans with prices and duration
- User clicks "Select" to choose a plan
- Proceeds to payment details

#### Step 2: Payment Details
- Shows selected plan summary
- Payment method selection (Airtel only at this time)
- Mobile number input field
- Validation for mobile number format

#### Step 3: Success Confirmation
- Displays payment success message
- Shows transaction details
- Indicates subscription is immediately active
- Button to start using premium features

### Integration Example

```typescript
import { SubscriptionModal } from '@/components/subscription-modal';

export function MyComponent() {
  const [isSubscriptionOpen, setIsSubscriptionOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsSubscriptionOpen(true)}>
        Subscribe Now
      </button>
      
      <SubscriptionModal
        isOpen={isSubscriptionOpen}
        onClose={() => setIsSubscriptionOpen(false)}
        onSuccess={() => {
          // Handle successful subscription
          // Refresh user data, update UI, etc.
        }}
      />
    </>
  );
}
```

## Payment Flow Diagram

```
1. User selects plan and payment method
   ↓
2. Enters mobile number
   ↓
3. Frontend sends to backend: POST /subscriptions/create/
   ↓
4. Backend MobileMoneyService:
   a. Initiates collection from user's account (3000-20000 UGX)
   b. Receives confirmation
   c. Initiates disbursement to target account (0740345346)
   d. Creates subscription record
   d. Creates payment record
   ↓
5. Backend returns success response
   ↓
6. Frontend displays success screen
   ↓
7. User can now access premium features
```

## Database Models

### Subscription Model
```python
class Subscription(models.Model):
    user = ForeignKey(User)
    plan = CharField(choices=['daily', 'weekly', 'monthly'])
    payment_method = CharField(choices=['airtel', 'mtn'])
    mobile_number = CharField()
    amount = IntegerField()  # In UGX
    end_date = DateTimeField()
    is_paid = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Payment Model
```python
class Payment(models.Model):
    subscription = ForeignKey(Subscription)
    user = ForeignKey(User)
    amount = IntegerField()  # In UGX
    payment_method = CharField()
    mobile_number = CharField()
    status = CharField(choices=['pending', 'completed', 'failed'])
    transaction_id = CharField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Sandbox Testing

For development and testing, the system operates in **sandbox mode** by default:
- Set `AIRTEL_ENVIRONMENT='sandbox'` in your `.env` file
- Payment requests return simulated success responses
- Transactions are not actually processed or charged
- Useful for testing UI flows and error handling

### Testing Credentials
```
AIRTEL_API_KEY=sandbox_test_key
AIRTEL_API_SECRET=sandbox_test_secret
AIRTEL_ENVIRONMENT=sandbox
```

## Production Deployment

When deploying to production:

1. **Update Environment Variables**:
   ```
   AIRTEL_API_KEY=your_production_key
   AIRTEL_API_SECRET=your_production_secret
   AIRTEL_ENVIRONMENT=production
   ```

2. **Verify API Configuration**:
   - Confirm Airtel API credentials are correct
   - Test payment collection and disbursement
   - Verify target account receives payments (0740345346)

3. **Monitor Transactions**:
   - Check `/admin/payments/` endpoint for all payment records
   - Compare total collected vs disbursed amounts
   - Handle reconciliation with Airtel statements

## Error Handling

### Common Error Scenarios

**1. Invalid Mobile Number**:
- Response: 400 Bad Request
- Message: "Invalid mobile number format"

**2. Payment Collection Failed**:
- Response: 500 Internal Server Error
- Message: "Payment collection failed"
- User can retry or contact support

**3. Disbursement Failed**:
- Response: 500 Internal Server Error
- Message: "Payment processing failed"
- Collected amount is retained in app account pending retry

### Error Response Format
```json
{
  "error": "Descriptive error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "specific_error_info"
  }
}
```

## Admin Dashboard Features

Access admin features at `/admin/subscriptions/`:
- View all subscriptions with payment status
- Filter by user, plan, or status
- Export payment records for reconciliation
- Manage user access based on subscription status

## API Rate Limiting

- **Default Rate**: 100 requests per minute per user
- **Subscription Creation**: 5 per hour per user (prevents duplicate charges)
- **Exceeded**: Returns 429 Too Many Requests

## Security Considerations

1. **HMAC Signature**: All Airtel API requests are signed with HMAC-SHA256
2. **HTTPS Only**: All transactions use encrypted connections
3. **API Keys**: Stored in environment variables, never hardcoded
4. **Token Authentication**: Subscription endpoint requires JWT token

## Support and Troubleshooting

### Common Issues

**Issue**: Payment processed but subscription not created
- Check server logs for exceptions
- Verify database connection
- Ensure migrations are up to date

**Issue**: User charged but subscription inactive
- Check Payment model status field
- Manual subscription creation may be required
- Contact admin for account adjustment

**Issue**: Disbursement to target account fails
- Verify target number (0740345346) is correct
- Check Airtel account balance prerequisite
- Contact Airtel support for API issues

## Future Enhancements

1. **MTN Mobile Money Support**: Add MTN collection/disbursement
2. **Multiple Payment Methods**: Credit card, bank transfer
3. **Automated Renewal**: Recurring billing for subscriptions
4. **Refund Processing**: Handle payment reversals
5. **Advanced Analytics**: Payment processing metrics and insights
6. **Multi-currency Support**: Handle different currencies

## Contact and Support

For technical support or questions about the payment system:
- Email: support@pestdetect.com
- Documentation: See [SUBSCRIPTION_SYSTEM.md](./SUBSCRIPTION_SYSTEM.md)
- API Reference: See [API documentation](./DOCUMENTATION.md)
