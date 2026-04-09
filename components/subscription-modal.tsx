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
  const [step, setStep] = useState<'plans' | 'payment' | 'confirm'>('plans');
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

    setIsLoading(true);
    try {
      const response = await apiClient.createSubscription({
        plan: selectedPlan,
        payment_method: paymentMethod,
        mobile_number: mobileNumber,
      });

      setPaymentId(response.payment_id);
      setSubscriptionId(response.subscription.id);
      setStep('confirm');

      toast({
        title: 'Subscription created',
        description: `Please complete the payment of ${response.subscription.amount} UGX`,
      });
    } catch (error) {
      toast({
        title: 'Error creating subscription',
        description: error instanceof Error ? error.message : 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmPayment = async () => {
    setIsLoading(true);
    try {
      await apiClient.confirmPayment({
        payment_id: paymentId,
      });

      toast({
        title: 'Payment confirmed!',
        description: 'Your subscription is now active',
      });

      // Reset form
      setStep('plans');
      setSelectedPlan(null);
      setPaymentMethod(null);
      setMobileNumber('');
      setPaymentId('');
      setSubscriptionId('');

      onClose();
      onSuccess?.();
    } catch (error) {
      toast({
        title: 'Error confirming payment',
        description: error instanceof Error ? error.message : 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {step === 'plans' && 'Choose Your Subscription Plan'}
            {step === 'payment' && 'Enter Payment Details'}
            {step === 'confirm' && 'Confirm Payment'}
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
          {step === 'confirm' && (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <CreditCard className="w-6 h-6 text-green-600" />
                  <div>
                    <p className="font-medium text-green-900">Payment Sent</p>
                    <p className="text-sm text-green-700">
                      Payment request has been sent to your mobile money account
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg space-y-2">
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
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">
                  <strong>Instructions:</strong>
                </p>
                <ol className="text-sm text-blue-800 list-decimal list-inside mt-2 space-y-1">
                  <li>Check your mobile phone for payment prompt</li>
                  <li>Enter your mobile money PIN to confirm</li>
                  <li>Once confirmed, click "Complete Payment" below</li>
                </ol>
              </div>

              <Button
                onClick={handleConfirmPayment}
                disabled={isLoading}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                {isLoading ? 'Confirming...' : 'Complete Payment'}
              </Button>

              <Button
                onClick={() => {
                  setStep('plans');
                  setSelectedPlan(null);
                  setPaymentMethod(null);
                  setMobileNumber('');
                }}
                variant="outline"
                className="w-full"
              >
                Cancel
              </Button>

              <p className="text-xs text-gray-500 text-center">
                If your subscription doesn't activate within a few minutes, we'll notify you
              </p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
