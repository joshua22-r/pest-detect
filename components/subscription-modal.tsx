'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/lib/api-client';
import { CreditCard, Phone } from 'lucide-react';

interface SubscriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  trialAttemptsUsed?: number;
  trialMaxAttempts?: number;
}

export function SubscriptionModal({
  isOpen,
  onClose,
  onSuccess,
  trialAttemptsUsed = 0,
  trialMaxAttempts = 5,
}: SubscriptionModalProps) {
  const [step, setStep] = useState<'plans' | 'payment' | 'success'>('plans');
  const [selectedPlan, setSelectedPlan] = useState<'daily' | 'weekly' | 'monthly' | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<'mtn' | 'airtel' | null>(null);
  const [mobileNumber, setMobileNumber] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [subscriptionId, setSubscriptionId] = useState('');
  const [paymentId, setPaymentId] = useState('');
  const { toast } = useToast();

  const plans = [
    { id: 'daily', name: 'Daily', price: 3000, duration: '1 day', color: '#3b82f6' },
    { id: 'weekly', name: 'Weekly', price: 10000, duration: '7 days', color: '#8b5cf6' },
    { id: 'monthly', name: 'Monthly', price: 20000, duration: '30 days', color: '#ec4899' },
  ];

  const handleSelectPlan = (plan: 'daily' | 'weekly' | 'monthly') => {
    setSelectedPlan(plan);
    setStep('payment');
  };

  const handlePaymentMethodSelect = (method: 'mtn' | 'airtel') => {
    setPaymentMethod(method);
  };

  const handleCreateSubscription = async () => {
    if (!selectedPlan || !paymentMethod || !mobileNumber) {
      toast({
        title: 'Missing information',
        description: 'Please select a plan, payment method, and enter your mobile number',
        variant: 'destructive',
      });
      return;
    }

    // Validate phone number format
    const phoneRegex = /^(\+?256|0)?\d{9}$|^(\+?256|0)\d{7,15}$/;
    if (!phoneRegex.test(mobileNumber)) {
      toast({
        title: 'Invalid phone number',
        description: 'Please enter a valid Uganda phone number (e.g., 0700123456 or +256700123456)',
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

      if (response && response.subscription) {
        setSubscriptionId(response.subscription.id);
        setStep('success');

        toast({
          title: '✅ Payment processed successfully!',
          description: response.message || `Your ${selectedPlan} subscription is now active! Payment has been sent to the target account.`,
        });

        // Call onSuccess after a short delay to let user see the success message
        setTimeout(() => {
          onSuccess?.();
        }, 2000);
      } else {
        throw new Error('Unexpected response format from server');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Please try again';
      console.error('Subscription error:', error);
      
      toast({
        title: '❌ Error creating subscription',
        description: errorMessage.includes('Already subscribed')
          ? 'You already have an active subscription'
          : errorMessage,
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
    setSubscriptionId('');
    setPaymentId('');

    onClose();
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
          {/* Trial Info */}
          {trialAttemptsUsed < trialMaxAttempts && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-900">
                Trial attempts used: <strong>{trialAttemptsUsed}/{trialMaxAttempts}</strong>
              </p>
              <p className="text-xs text-blue-700 mt-1">
                {trialMaxAttempts - trialAttemptsUsed} attempts remaining. Subscribe to continue using the system.
              </p>
            </div>
          )}

          {/* Plans Selection */}
          {step === 'plans' && (
            <div className="grid grid-cols-3 gap-4">
              {plans.map((plan) => (
                <Card
                  key={plan.id}
                  className={`p-4 cursor-pointer transition-all ${
                    selectedPlan === plan.id
                      ? 'ring-2 ring-offset-2 ring-blue-500 bg-blue-50'
                      : 'hover:shadow-lg'
                  }`}
                  onClick={() => handleSelectPlan(plan.id as any)}
                >
                  <div className="text-center">
                    <h3 className="font-bold text-lg">{plan.name}</h3>
                    <p className="text-2xl font-bold mt-2">{plan.price.toLocaleString()}</p>
                    <p className="text-xs text-gray-600 mt-1">UGX</p>
                    <p className="text-sm text-gray-600 mt-2">{plan.duration}</p>
                    <Button
                      className="w-full mt-4"
                      onClick={() => handleSelectPlan(plan.id as any)}
                      variant={selectedPlan === plan.id ? 'default' : 'outline'}
                    >
                      Select
                    </Button>
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
                  {plans.find((p) => p.id === selectedPlan)?.name} -{' '}
                  {plans.find((p) => p.id === selectedPlan)?.price.toLocaleString()} UGX
                </p>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Payment Method</label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { id: 'mtn', name: 'MTN Mobile Money', icon: '📱' },
                    { id: 'airtel', name: 'Airtel Mobile Money', icon: '📞' },
                  ].map((method) => (
                    <Card
                      key={method.id}
                      className={`p-4 cursor-pointer transition-all ${
                        paymentMethod === method.id
                          ? 'ring-2 ring-offset-2 ring-blue-500 bg-blue-50'
                          : 'hover:shadow-lg'
                      }`}
                      onClick={() => handlePaymentMethodSelect(method.id as any)}
                    >
                      <div className="text-center">
                        <div className="text-2xl mb-2">{method.icon}</div>
                        <p className="text-sm font-medium">{method.name}</p>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Mobile Number</label>
                <div className="flex gap-2">
                  <Input
                    type="text"
                    placeholder="e.g., 0700123456"
                    value={mobileNumber}
                    onChange={(e) => setMobileNumber(e.target.value)}
                    className="flex-1"
                  />
                  <Phone className="w-5 h-5 text-gray-400 mt-3" />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {paymentMethod === 'mtn' && 'MTN number format: 0700-0799'}
                  {paymentMethod === 'airtel' && 'Airtel number format: 0750-0759'}
                </p>
              </div>

              <Button
                onClick={handleCreateSubscription}
                disabled={isLoading || !paymentMethod || !mobileNumber}
                className="w-full"
              >
                {isLoading ? 'Processing...' : 'Proceed to Payment'}
              </Button>

              <Button
                onClick={() => {
                  setStep('plans');
                  setSelectedPlan(null);
                }}
                variant="outline"
                className="w-full"
              >
                Back
              </Button>
            </div>
          )}

          {/* Confirm Payment */}
          {step === 'success' && (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="text-2xl">✅</div>
                  <div>
                    <p className="font-medium text-green-900">Payment Processed Successfully!</p>
                    <p className="text-sm text-green-700">
                      Your subscription is now active and payment has been sent to the target account.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Plan:</span>
                  <span className="font-medium">
                    {plans.find((p) => p.id === selectedPlan)?.name}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Amount:</span>
                  <span className="font-medium">
                    {plans
                      .find((p) => p.id === selectedPlan)
                      ?.price.toLocaleString()}{' '}
                    UGX
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Method:</span>
                  <span className="font-medium">{paymentMethod?.toUpperCase()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Mobile:</span>
                  <span className="font-medium">{mobileNumber}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className="font-medium text-green-600">Active</span>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">
                  <strong>What happens next:</strong>
                </p>
                <ul className="text-sm text-blue-800 list-disc list-inside mt-2 space-y-1">
                  <li>Your subscription is immediately active</li>
                  <li>You can now use all premium features</li>
                  <li>Payment has been processed and sent to the service account</li>
                  <li>You'll receive a confirmation SMS shortly</li>
                </ul>
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
