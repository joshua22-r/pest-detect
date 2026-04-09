# Pest Detect - Subscription & Trial System Documentation

## Overview

The Pest Detect application now includes a comprehensive trial and subscription system that allows users to try the disease detection feature for free with a limited number of attempts, and then upgrade to a paid subscription plan for continuous access.

## Features

### 1. Trial System
- **Duration**: 5 free prediction attempts per user
- **Auto-tracking**: Trial attempts are automatically tracked on first login
- **Trial Status**: Users can view their remaining attempts on the predict page
- **Trial Button**: Visible on the predict page showing remaining attempts and trial status

### 2. Subscription Plans
Three affordable subscription plans are available:

| Plan | Price | Duration | Code |
|------|-------|----------|------|
| Daily | 3,000 UGX | 24 hours | `daily` |
| Weekly | 10,000 UGX | 7 days | `weekly` |
| Monthly | 20,000 UGX | 30 days | `monthly` |

### 3. Payment Methods
Users can pay via:
- **MTN Mobile Money**: Number format 0700-0799
- **Airtel Mobile Money**: Number format 0750-0759

### 4. Admin Controls
Admins can:
- View all payments and their status (pending, completed, failed)
- View all subscriptions and their status (active, expired, cancelled)
- Allow users to use the system without subscription (bypass payment)
- Track payment history and subscription details

## User Flow

### For New Users (Trial)
1. User signs up and gets 5 free trial attempts
2. User can upload images and get disease predictions (counts against trial attempts)
3. After 5 attempts, user must either:
   - Subscribe to a plan
   - Get admin approval to continue using the system

### For Paid Users (Subscription)
1. User selects a subscription plan
2. User enters mobile number
3. Selects payment method (MTN or Airtel)
4. Payment prompt is sent to their mobile number
5. User completes payment on their phone
6. Subscription is activated, and user has unlimited predictions until expiration

### For Admin (Management)
1. Admin can view all payments in the Payments tab
2. Admin can view all subscriptions in the Subscriptions tab
3. Admin can allow users to use the system without subscription
4. Admin can revoke subscription access if needed

## Database Models

### Trial Model
```
- user (OneToOne relationship with User)
- attempts_used (default: 0)
- max_attempts (default: 5)
- status (active, expired, converted, default: active)
- created_at
- updated_at
```

### Subscription Model
```
- user (ForeignKey to User)
- plan (daily, weekly, monthly)
- status (active, expired, cancelled)
- payment_method (mtn, airtel)
- mobile_number (string)
- amount (integer in UGX)
- end_date (datetime)
- is_paid (boolean, default: False)
- start_date
- created_at
- updated_at
```

### Payment Model
```
- subscription (ForeignKey to Subscription)
- user (ForeignKey to User)
- amount (integer in UGX)
- payment_method (string)
- mobile_number (string)
- status (pending, completed, failed)
- transaction_id (string, unique)
- created_at
- updated_at
```

## API Endpoints

### Trial Endpoints
- `GET /api/trial/status/` - Get user's trial status
- `POST /api/trial/increment/` - Increment trial attempts (called after successful prediction)

### Subscription Endpoints
- `GET /api/predict/check/` - Check if user can make predictions
- `POST /api/subscriptions/create/` - Create a new subscription
- `POST /api/subscriptions/confirm-payment/` - Confirm payment and activate subscription
- `GET /api/subscriptions/` - Get user's subscriptions

### Admin Endpoints
- `GET /api/admin/payments/` - List all payments (filters: `?status=completed`)
- `GET /api/admin/subscriptions/` - List all subscriptions (filters: `?status=active&paid=true`)
- `POST /api/admin/allow-access/` - Allow user to use system without subscription

## Frontend Components

### TrialButton Component
Displays at the top of the predict page:
- Shows remaining trial attempts
- Shows status (active or expired)
- Opens subscription modal when trial is expired

### SubscriptionModal Component
Multi-step modal for subscribing:
1. **Step 1**: Select plan (daily, weekly, monthly)
2. **Step 2**: Select payment method and enter mobile number
3. **Step 3**: Confirm payment and wait for completion

## Implementation Details

### Backend Access Control (views.py)
The predict endpoint checks:
1. Does user have remaining trial attempts?
2. Does user have an active, paid subscription?
3. Has admin allowed user access without subscription?

If none of these conditions are true, the prediction is blocked with a 403 error.

### Frontend Access Control (page.tsx)
Before allowing a prediction:
1. Calls `/api/predict/check/` to verify access
2. If denied, opens subscription modal
3. If allowed via trial, increments trial attempts after successful prediction

### Trial Lifecycle
New user → Get Trial (5 attempts) → Use Attempts → Trial Expires → Must Subscribe OR Get Admin Approval

## Payment Processing (Simulated)

**Note**: The payment processing is currently simulated. In production, you would need to integrate with:
- MTN Mobile Money API
- Airtel Mobile Money API
- Payment gateway webhooks for confirmation

Current workflow:
1. User submits payment info
2. Payment record is created with status "pending"
3. Frontend shows instructions to check mobile for payment prompt
4. User enters PIN on their phone
5. Frontend confirms payment → Status changes to "completed"
6. Subscription is activated

## Configuration

### Django Settings
Add these to your `.env` or settings:
```
# Mobile Money API Keys (if integrating real payment)
MTN_API_KEY=your-key
AIRTEL_API_KEY=your-key

# Trial Settings
TRIAL_MAX_ATTEMPTS=5

# Subscription Settings
DAILY_SUBSCRIPTION_PRICE=3000
WEEKLY_SUBSCRIPTION_PRICE=10000
MONTHLY_SUBSCRIPTION_PRICE=20000
```

## Testing

### Manual Testing Steps

1. **Test Trial System**:
   - Create new user account
   - Navigate to predict page
   - Verify trial button shows 5 attempts
   - Upload 5 images and verify counter decreases
   - On 6th upload, subscription modal should appear

2. **Test Subscription**:
   - In subscription modal, select plan
   - Select payment method and enter mobile number
   - Click "Proceed to Payment"
   - Verify payment details are displayed
   - Click "Complete Payment"
   - Verify subscription is activated

3. **Test Admin Controls**:
   - Login as admin
   - Go to admin dashboard
   - Click "Payments" tab
   - Click "Subscriptions" tab
   - Verify user's subscription and payment info appears
   - Test "Allow" and "Revoke" buttons

4. **Test Access Control**:
   - Create new user
   - Verify can make 5 predictions
   - After 5, try to predict (should be blocked)
   - Admin allows user access
   - Verify user can now predict without subscription

## Security Considerations

1. **Payment Security**: Currently simulated. In production:
   - Use HTTPS for all API calls
   - Validate payment via provider webhooks
   - Store transaction IDs for reconciliation
   - Implement payment retry logic

2. **Access Control**:
   - Trial/Subscription status checked on every prediction
   - Server-side validation (not just frontend)
   - Admin-allowed access is stored in database

3. **User Data**:
   - Mobile numbers are stored encrypted in production
   - Payment records should be secured
   - Audit trail for admin actions

## Future Enhancements

1. **Real Payment Integration**:
   - Integrate MTN Mobile Money API
   - Integrate Airtel Mobile Money API
   - Implement webhook handling for payment confirmation
   - Add transaction reconciliation reports

2. **Advanced Features**:
   - Auto-renewal for recurring subscriptions
   - Bulk purchasing/gifting subscriptions
   - Referral program (give trial time to referred users)
   - Family/group subscription plans
   - Usage analytics and reports

3. **Admin Features**:
   - Subscription analytics and reports
   - Revenue tracking
   - Automated renewal emails
   - Custom discount codes
   - Bulk user management

4. **User Features**:
   - Cancel subscription
   - Pause subscription
   - Upgrade/downgrade plan
   - Usage dashboard
   - Billing history

## Troubleshooting

### Trial Not Tracking
- Verify Trial object is created for user in database
- Check trial status endpoint returns correct data
- Verify increment endpoint is called after each prediction

### Payment Not Completing
- Check Payment records in admin
- Verify subscription end_date is set correctly
- Confirm payment status is updated to "completed"

### User Can't Predict with Active Subscription
- Verify subscription status is "active"
- Check end_date is in future
- Verify is_paid is True
- Check admin_allowed_access is not interfering

### Admin Can't See Payments
- Verify user is_staff is True
- Check admin endpoint permissions
- Verify payments exist in database for given time period

## Credits

Subscription system designed and implemented for the Pest Detect application.
Uganda pricing: 3,000-20,000 UGX per plan
Mobile Money: MTN & Airtel support
