'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Lock, Zap } from 'lucide-react';

interface TrialCounterProps {
  trialsUsed: number;
  maxTrials: number;
  onSubscribe?: () => void;
  isDemo?: boolean;
}

export function TrialCounter({
  trialsUsed,
  maxTrials,
  onSubscribe,
  isDemo = false,
}: TrialCounterProps) {
  const trialsRemaining = maxTrials - trialsUsed;
  const percentageUsed = (trialsUsed / maxTrials) * 100;
  const isExpired = trialsRemaining <= 0;

  // Color based on remaining trials
  const getProgressColor = () => {
    if (trialsRemaining <= 0) return 'bg-red-500';
    if (trialsRemaining <= 1) return 'bg-red-500';
    if (trialsRemaining <= 2) return 'bg-orange-500';
    return 'bg-green-500';
  };

  const getHeaderColor = () => {
    if (trialsRemaining <= 0) return 'text-red-900';
    if (trialsRemaining <= 1) return 'text-orange-900';
    return 'text-green-900';
  };

  const getCardBg = () => {
    if (trialsRemaining <= 0) return 'bg-red-50 border-red-200';
    if (trialsRemaining <= 1) return 'bg-orange-50 border-orange-200';
    return 'bg-green-50 border-green-200';
  };

  return (
    <Card className={`p-6 border-2 transition-all ${getCardBg()}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-4xl">
              {isExpired ? '🔒' : '🆓'}
            </div>
            <div>
              <h3 className={`text-xl font-bold ${getHeaderColor()}`}>
                {isExpired ? 'Trial Expired' : 'Trial Demo Mode'}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {isExpired
                  ? 'You have used all your free trials'
                  : `${trialsRemaining} ${trialsRemaining === 1 ? 'trial' : 'trials'} remaining`}
              </p>
            </div>
          </div>

          {/* Trial Count Display */}
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900">
              {trialsUsed}
              <span className="text-lg text-gray-600">/{maxTrials}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">used</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full ${getProgressColor()} transition-all duration-500 ease-out`}
              style={{ width: `${percentageUsed}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-600">
            <span>Free attempts used</span>
            <span>{Math.round(percentageUsed)}%</span>
          </div>
        </div>

        {/* Trial Counter Dots */}
        <div className="flex gap-2 justify-center">
          {Array.from({ length: maxTrials }).map((_, index) => (
            <div
              key={index}
              className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                index < trialsUsed
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {index + 1}
            </div>
          ))}
        </div>

        {/* Status Message and Action */}
        <div className="pt-4 border-t">
          {isExpired ? (
            <>
              <p className="text-sm text-gray-700 mb-4">
                ✨ Unlock unlimited scans with a subscription! Choose from daily, weekly, or monthly plans and pay using MTN Mobile Money or Airtel Money.
              </p>
              <Button
                onClick={onSubscribe}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold"
              >
                <Lock className="w-4 h-4 mr-2" />
                Subscribe Now to Continue
              </Button>
            </>
          ) : trialsRemaining <= 2 ? (
            <>
              <p className="text-sm text-gray-700 mb-4">
                ⚠️ You're running out of free trials! Get a subscription soon to continue using unlimited scans.
              </p>
              <Button
                onClick={onSubscribe}
                variant="outline"
                className="w-full border-orange-500 text-orange-600 hover:bg-orange-50"
              >
                <Zap className="w-4 h-4 mr-2" />
                Upgrade to Premium
              </Button>
            </>
          ) : (
            <p className="text-sm text-gray-700 text-center">
              📸 You have {trialsRemaining} free scans remaining. Use them to test the detection system!
            </p>
          )}
        </div>
      </div>
    </Card>
  );
}
