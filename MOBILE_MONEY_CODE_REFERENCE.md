# Mobile Money Payment System - Code Reference

## Backend Implementation

### 1. Mobile Money Service (backend/api/mobile_money_service.py)

```python
class MobileMoneyService:
    """Service for handling Mobile Money payments (Airtel)"""
    
    AIRTEL_BASE_URL = "https://openapi.airtel.africa"
    AIRTEL_API_KEY = getattr(settings, 'AIRTEL_API_KEY', '')
    AIRTEL_API_SECRET = getattr(settings, 'AIRTEL_API_SECRET', '')
    AIRTEL_ENVIRONMENT = getattr(settings, 'AIRTEL_ENVIRONMENT', 'sandbox')
    TARGET_AIRTEL_NUMBER = "0740345346"
    
    @staticmethod
    def process_subscription_payment(user, plan_data):
        """Process subscription payment via mobile money"""
        amount = plan_data['amount']
        mobile_number = plan_data['mobile_number']
        plan = plan_data['plan']
        
        # Generate unique reference
        reference = f"sub_{user.id}_{plan}_{int(timezone.now().timestamp())}"
        
        # Step 1: Collect payment from customer
        collection_result = MobileMoneyService.initiate_collection(
            amount, mobile_number, reference
        )
        
        if collection_result['status'] == 'success':
            # Step 2: Disburse to target Airtel number
            disbursement_reference = f"disburse_{reference}"
            disbursement_result = MobileMoneyService.initiate_disbursement(
                amount, MobileMoneyService.TARGET_AIRTEL_NUMBER, 
                disbursement_reference
            )
            
            # Calculate subscription end date
            start_date = timezone.now()
            if plan == 'daily':
                end_date = start_date + timezone.timedelta(days=1)
            elif plan == 'weekly':
                end_date = start_date + timezone.timedelta(weeks=1)
            elif plan == 'monthly':
                end_date = start_date + timezone.timedelta(days=30)
            
            # Create subscription record
            subscription = Subscription.objects.create(
                user=user,
                plan=plan,
                payment_method='airtel',
                mobile_number=mobile_number,
                amount=amount,
                end_date=end_date,
                is_paid=True,
            )
            
            # Create payment record
            Payment.objects.create(
                subscription=subscription,
                user=user,
                amount=amount,
                payment_method='airtel',
                mobile_number=mobile_number,
                status='completed',
                transaction_id=collection_result['transaction_id'],
            )
            
            return {
                'subscription': subscription,
                'collection_transaction': collection_result,
                'disbursement_transaction': disbursement_result
            }
        else:
            raise ValueError("Payment collection failed")
```

### 2. Subscription Endpoint (backend/api/views.py)

```python
from api.mobile_money_service import MobileMoneyService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription(request):
    """Create a new subscription with mobile money payment"""
    plan = request.data.get('plan')
    payment_method = request.data.get('payment_method')
    mobile_number = request.data.get('mobile_number')

    if not plan or not payment_method or not mobile_number:
        return Response(
            {'error': 'Plan, payment method, and mobile number are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if plan not in ['daily', 'weekly', 'monthly']:
        return Response(
            {'error': 'Invalid plan'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Calculate amount based on plan
    if plan == 'daily':
        amount = 3000
    elif plan == 'weekly':
        amount = 10000
    else:  # monthly
        amount = 20000

    plan_data = {
        'plan': plan,
        'payment_method': payment_method,
        'mobile_number': mobile_number,
        'amount': amount
    }

    try:
        # Process payment via mobile money
        result = MobileMoneyService.process_subscription_payment(
            request.user, plan_data
        )
        subscription = result['subscription']
        serializer = SubscriptionSerializer(subscription)

        return Response({
            'subscription': serializer.data,
            'collection_transaction': result['collection_transaction'],
            'disbursement_transaction': result['disbursement_transaction'],
            'message': f'Payment processed successfully! {amount} UGX sent to Airtel number 0740345346',
            'target_number': MobileMoneyService.TARGET_AIRTEL_NUMBER
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f'Failed to create subscription: {str(e)}')
        return Response(
            {'error': f'Payment processing failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

## Frontend Implementation

### 3. Subscription Modal (components/subscription-modal.tsx)

```typescript
export function SubscriptionModal({
  isOpen,
  onClose,
  onSuccess,
}: SubscriptionModalProps) {
  const [step, setStep] = useState<'plans' | 'payment' | 'success'>('plans');
  const [selectedPlan, setSelectedPlan] = useState<'daily' | 'weekly' | 'monthly' | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<'airtel' | null>(null);
  const [mobileNumber, setMobileNumber] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const plans = [
    { id: 'daily', name: 'Daily', price: 3000, duration: '1 day' },
    { id: 'weekly', name: 'Weekly', price: 10000, duration: '7 days' },
    { id: 'monthly', name: 'Monthly', price: 20000, duration: '30 days' },
  ];

  const handleCreateSubscription = async () => {
    if (!selectedPlan || !paymentMethod || !mobileNumber) {
      toast({
        title: 'Missing information',
        description: 'Please select a plan and enter your mobile number',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiClient.createSubscription({
        plan: selectedPlan,
        payment_method: paymentMethod,
        mobile_number: mobileNumber,
      });

      setStep('success');

      toast({
        title: 'Payment processed successfully!',
        description: response.message,
      });
    } catch (error) {
      toast({
        title: 'Error processing payment',
        description: error instanceof Error ? error.message : 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setStep('plans');
    setSelectedPlan(null);
    setPaymentMethod(null);
    setMobileNumber('');
    onClose();
    onSuccess?.();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {step === 'plans' && 'Choose Your Subscription Plan'}
            {step === 'payment' && 'Enter Payment Details'}
            {step === 'success' && 'Payment Successful!'}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Plans Selection */}
          {step === 'plans' && (
            <div className="grid grid-cols-3 gap-4">
              {plans.map((plan) => (
                <Card
                  key={plan.id}
                  className={`p-4 cursor-pointer transition-all ${
                    selectedPlan === plan.id
                      ? 'ring-2 ring-blue-500 bg-blue-50'
                      : 'hover:shadow-lg'
                  }`}
                  onClick={() => {
                    setSelectedPlan(plan.id as any);
                    setStep('payment');
                  }}
                >
                  <div className="text-center">
                    <h3 className="font-bold text-lg">{plan.name}</h3>
                    <p className="text-2xl font-bold mt-2">{plan.price.toLocaleString()}</p>
                    <p className="text-xs text-gray-600 mt-1">UGX</p>
                    <p className="text-sm text-gray-600 mt-2">{plan.duration}</p>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Payment Details */}
          {step === 'payment' && selectedPlan && (
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Selected Plan:</p>
                <p className="text-lg font-bold">
                  {plans.find((p) => p.id === selectedPlan)?.name} - 
                  {plans.find((p) => p.id === selectedPlan)?.price.toLocaleString()} UGX
                </p>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Mobile Number</label>
                <Input
                  type="text"
                  placeholder="e.g., 0740123456"
                  value={mobileNumber}
                  onChange={(e) => setMobileNumber(e.target.value)}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Airtel number format: 0750-0759
                </p>
              </div>

              <Button
                onClick={handleCreateSubscription}
                disabled={isLoading || !mobileNumber}
                className="w-full"
              >
                {isLoading ? 'Processing...' : 'Proceed to Payment'}
              </Button>

              <Button
                onClick={() => setStep('plans')}
                variant="outline"
                className="w-full"
              >
                Back
              </Button>
            </div>
          )}

          {/* Success Confirmation */}
          {step === 'success' && (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="text-2xl">✅</div>
                  <div>
                    <p className="font-medium text-green-900">Payment Successful!</p>
                    <p className="text-sm text-green-700">
                      Your subscription is active and payment sent to service account.
                    </p>
                  </div>
                </div>
              </div>

              <Button
                onClick={handleClose}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                Start Using Premium Features
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

## API Client Integration

### 4. API Client (lib/api-client.ts)

```typescript
async createSubscription(data: {
  plan: 'daily' | 'weekly' | 'monthly';
  payment_method: 'airtel';
  mobile_number: string;
}): Promise<any> {
  return this.request<any>('/subscriptions/create/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
```

## Database Models

### 5. Models (backend/api/models.py)

```python
class Subscription(models.Model):
    PLAN_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('airtel', 'Airtel Money'),
        ('mtn', 'MTN Money'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    mobile_number = models.CharField(max_length=20)
    amount = models.IntegerField()  # UGX
    end_date = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()  # UGX
    payment_method = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Environment Configuration

### 6. Environment Variables (.env)

```bash
# Airtel Money API Configuration
AIRTEL_API_KEY=your_api_key_here
AIRTEL_API_SECRET=your_api_secret_here
AIRTEL_ENVIRONMENT=sandbox  # or 'production'

# Other settings
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings
```

---

## API Request/Response Examples

### Request: Create Subscription

```bash
curl -X POST http://localhost:8000/api/subscriptions/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {jwt_token}" \
  -d '{
    "plan": "monthly",
    "payment_method": "airtel",
    "mobile_number": "0740123456"
  }'
```

### Response: Success

```json
{
  "subscription": {
    "id": 5,
    "user": 1,
    "plan": "monthly",
    "payment_method": "airtel",
    "mobile_number": "0740123456",
    "amount": 20000,
    "end_date": "2024-02-15T10:30:00Z",
    "is_paid": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "collection_transaction": {
    "status": "success",
    "transaction_id": "txn_col_123456",
    "amount": 20000,
    "currency": "UGX"
  },
  "disbursement_transaction": {
    "status": "success",
    "transaction_id": "txn_dis_789012",
    "amount": 20000,
    "currency": "UGX"
  },
  "message": "Payment processed successfully! 20000 UGX sent to Airtel number 0740345346",
  "target_number": "0740345346"
}
```

---

## Testing Examples

### Unit Test: Mobile Money Service

```python
from django.test import TestCase
from api.mobile_money_service import MobileMoneyService

class TestMobileMoneyService(TestCase):
    def test_process_subscription_payment(self):
        user = User.objects.create(username='testuser')
        plan_data = {
            'plan': 'monthly',
            'payment_method': 'airtel',
            'mobile_number': '0740123456',
            'amount': 20000
        }
        
        result = MobileMoneyService.process_subscription_payment(user, plan_data)
        
        self.assertIn('subscription', result)
        self.assertIn('collection_transaction', result)
        self.assertIn('disbursement_transaction', result)
        self.assertEqual(result['subscription'].plan, 'monthly')
```

---

This code reference provides all the essential code snippets for the mobile money payment system implementation. Refer to the full files for complete implementations.
