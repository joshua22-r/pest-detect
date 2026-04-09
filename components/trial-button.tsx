'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/lib/api-client';
import { Zap, Lock } from 'lucide-react';

interface TrialButtonProps {
  onTrialExpired?: () => void;
  onSubscriptionOpen?: () => void;
}

export function TrialButton({ onTrialExpired, onSubscriptionOpen }: TrialButtonProps) {
  const [trialStatus, setTrialStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadTrialStatus();
  }, []);

  const loadTrialStatus = async () => {
    try {
      // Check if user is authenticated
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      if (!token) {
        setIsLoading(false);
        return;
      }

      const status = await apiClient.getTrialStatus();
      setTrialStatus(status);
    } catch (error) {
      console.error('Failed to load trial status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="animate-pulse h-24 bg-gray-200 rounded-lg" />;
  }

  if (!trialStatus) {
    return null;
  }

  const trialsRemaining = trialStatus.max_attempts - trialStatus.attempts_used;
  const trialExpired = trialsRemaining <= 0;

  return (
    <Card className={`p-4 ${trialExpired ? 'bg-green-50 border-green-200' : 'bg-blue-50 border-blue-200'}`}>
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-cent gap-3">
          <Zap className={`w-6 h-6 ${trialExpired ? 'text-green-600' : 'text-blue-600'}`} />
          <div>
            <h3 className={`font-bold ${trialExpired ? 'text-green-900' : 'text-blue-900'}`}>
              {trialExpired ? 'Trial Ended' : 'Trial Mode'}
            </h3>
            <p className={`text-sm ${trialExpired ? 'text-green-700' : 'text-blue-700'}`}>
              {trialExpired
                ? 'You have used all your trial attempts'
                : `${trialsRemaining} attempts remaining`}
            </p>
          </div>
        </div>

        {trialExpired ? (
          <Button
            onClick={onSubscriptionOpen}
            className="bg-green-600 hover:bg-green-700 flex items-center gap-2"
          >
            <Lock className="w-4 h-4" />
            Subscribe Now
          </Button>
        ) : (
          <div className="text-right">
            <p className="text-sm font-medium">
              {trialStatus.attempts_used}/{trialStatus.max_attempts}
            </p>
            <p className="text-xs text-gray-600">used</p>
          </div>
        )}
      </div>
    </Card>
  );
}
