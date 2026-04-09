'use client';

import { useState, useEffect } from 'react';
import { ImageUpload, SubjectType } from '@/components/image-upload';
import { DetectionResults, DetectionResult } from '@/components/detection-results';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { TrialButton } from '@/components/trial-button';
import { SubscriptionModal } from '@/components/subscription-modal';
import { Leaf, LogIn } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import Link from 'next/link';

const DEMO_TRIAL_KEY = 'pest_detect_demo_trials';
const MAX_DEMO_TRIALS = 5;

export default function PredictPage() {
  const [subjectType, setSubjectType] = useState<SubjectType>('plant');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [canPredict, setCanPredict] = useState(true);
  const [predictStatus, setPredictStatus] = useState<any>(null);
  const [isSubscriptionOpen, setIsSubscriptionOpen] = useState(false);
  const [trialStatus, setTrialStatus] = useState<any>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isDemo, setIsDemo] = useState(false);
  const [demoTrialsUsed, setDemoTrialsUsed] = useState(0);
  const { toast } = useToast();

  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    try {
      // Try to get current user
      const user = await apiClient.request<any>('/auth/user/');
      setIsAuthenticated(true);
      setIsDemo(false);
      // Only load trial status for authenticated users
      loadTrialStatus();
      checkPredictAccess();
    } catch (error) {
      // Not authenticated, use demo mode
      setIsAuthenticated(false);
      setIsDemo(true);
      loadDemoTrials();
    }
  };

  const loadDemoTrials = () => {
    if (typeof window !== 'undefined') {
      const savedTrials = localStorage.getItem(DEMO_TRIAL_KEY);
      const trials = savedTrials ? parseInt(savedTrials, 10) : 0;
      setDemoTrialsUsed(trials);
      setCanPredict(trials < MAX_DEMO_TRIALS);
    }
  };

  const incrementDemoTrial = () => {
    if (typeof window !== 'undefined') {
      const newCount = demoTrialsUsed + 1;
      localStorage.setItem(DEMO_TRIAL_KEY, String(newCount));
      setDemoTrialsUsed(newCount);
      setCanPredict(newCount < MAX_DEMO_TRIALS);
    }
  };

  const checkPredictAccess = async () => {
    try {
      const status = await apiClient.checkCanPredict();
      setCanPredict(status.can_predict);
      setPredictStatus(status);
    } catch (error) {
      console.error('Failed to check predict access:', error);
    }
  };

  const loadTrialStatus = async () => {
    try {
      // Check if user is authenticated
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      if (!token) {
        return;
      }

      const status = await apiClient.getTrialStatus();
      setTrialStatus(status);
    } catch (error) {
      // If not authenticated, skip
      console.error('Failed to load trial status:', error);
    }
  };

  const handleImageSelect = async (file: File, type: SubjectType) => {
    // For demo users
    if (isDemo) {
      if (demoTrialsUsed >= MAX_DEMO_TRIALS) {
        setIsSubscriptionOpen(true);
        return;
      }

      // Show demo result
      setSelectedFile(file);
      setIsAnalyzing(true);

      try {
        // Simulate ML detection with mock data
        await new Promise(resolve => setTimeout(resolve, 2000));

        const mockDiseases = {
          plant: {
            disease: 'Early Blight',
            confidence: Math.random() * 30 + 70,
            severity: 'medium',
            treatment: 'Apply fungicide treatments and remove infected leaves',
            prevention: 'Ensure proper plant spacing for air circulation',
          },
          animal: {
            disease: 'Mastitis',
            confidence: Math.random() * 30 + 70,
            severity: 'high',
            treatment: 'Antibiotic therapy and regular milking',
            prevention: 'Maintain proper udder hygiene',
          },
        };

        const mockResult =
          mockDiseases[type === 'plant' ? 'plant' : 'animal'];

        const transformedResult: DetectionResult = {
          id: `demo-${Date.now()}`,
          disease: mockResult.disease,
          confidence: mockResult.confidence,
          severity: mockResult.severity as 'low' | 'medium' | 'high',
          subjectType: type,
          treatment: mockResult.treatment,
          prevention: mockResult.prevention,
          affectedPlants: type === 'plant' ? ['Various plants'] : [],
          affectedAnimals: type === 'animal' ? ['Various animals'] : [],
          timestamp: new Date().toISOString(),
        };

        setResult(transformedResult);
        incrementDemoTrial();

        toast({
          title: 'Demo Analysis Complete!',
          description: `Demo attempt ${demoTrialsUsed + 1}/${MAX_DEMO_TRIALS}. Login to save results and use unlimited scans.`,
        });
      } catch (error) {
        console.error('Demo analysis error:', error);
        toast({
          title: 'Analysis failed',
          description: 'Please try again',
          variant: 'destructive',
        });
      } finally {
        setIsAnalyzing(false);
      }
      return;
    }

    // For authenticated users
    try {
      const accessCheck = await apiClient.checkCanPredict();
      if (!accessCheck.can_predict) {
        toast({
          title: 'Trial Ended',
          description: 'You have used all your trial attempts. Please subscribe to continue.',
          variant: 'destructive',
        });
        setIsSubscriptionOpen(true);
        return;
      }

      setSelectedFile(file);
      setIsAnalyzing(true);

      // Call real API
      const result = await apiClient.predict(file, type);

      // Increment trial attempts if using trial
      if (accessCheck.has_trial_access) {
        try {
          await apiClient.incrementTrialAttempts();
          await loadTrialStatus();
        } catch (error) {
          console.error('Failed to increment trial attempts:', error);
        }
      }

      // Transform API response to component format
      const transformedResult: DetectionResult = {
        id: result.id,
        disease: result.disease_name,
        confidence: result.confidence,
        severity: result.severity as 'low' | 'medium' | 'high',
        subjectType: result.subject_type,
        treatment: result.treatment,
        prevention: result.prevention,
        affectedPlants: result.subject_type === 'plant' ? ['Various plants'] : [],
        affectedAnimals: result.subject_type === 'animal' ? ['Various animals'] : [],
        timestamp: result.created_at,
      };

      setResult(transformedResult);
      toast({
        title: 'Analysis complete!',
        description: `${type === 'plant' ? 'Plant' : 'Livestock'} status: ${transformedResult.disease}`,
      });
    } catch (error) {
      console.error('Prediction error:', error);
      toast({
        title: 'Analysis failed',
        description: error instanceof Error ? error.message : 'Please try uploading the image again',
        variant: 'destructive',
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSaveResult = async () => {
    if (!result) return;

    setIsSaving(true);
    try {
      // The result is already saved when we call predict API
      // Just show success message
      toast({
        title: 'Saved successfully',
        description: 'Your scan has been saved to history',
      });

      // Reset form
      setSelectedFile(null);
      setResult(null);
    } catch (error) {
      toast({
        title: 'Save failed',
        description: 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)] py-8 px-4 bg-gradient-to-br from-green-100 via-blue-50 to-purple-100">
      <div className="max-w-4xl mx-auto">
        {/* Demo Mode Banner or Trial Button */}
        <div className="mb-6">
          {isDemo ? (
            <Card className={`p-4 ${demoTrialsUsed >= MAX_DEMO_TRIALS ? 'bg-green-50 border-green-200' : 'bg-green-50 border-green-200'}`}>
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="text-3xl">🆓</div>
                  <div>
                    <h3 className="font-bold text-green-900">
                      {demoTrialsUsed >= MAX_DEMO_TRIALS ? 'Demo Trial Ended' : 'Demo Mode'}
                    </h3>
                    <p className="text-sm text-green-700">
                      {demoTrialsUsed >= MAX_DEMO_TRIALS
                        ? 'You have used all your demo trials'
                        : `Free trials remaining: ${MAX_DEMO_TRIALS - demoTrialsUsed}/${MAX_DEMO_TRIALS}`}
                    </p>
                  </div>
                </div>
                {demoTrialsUsed >= MAX_DEMO_TRIALS ? (
                  <Button
                    onClick={() => setIsSubscriptionOpen(true)}
                    className="bg-green-600 hover:bg-green-700 flex items-center gap-2"
                  >
                    <Lock className="w-4 h-4" />
                    Subscribe Now
                  </Button>
                ) : (
                  <Link href="/auth/login">
                    <Button className="bg-green-600 hover:bg-green-700 flex items-center gap-2">
                      <LogIn className="w-4 h-4" />
                      Login to Save & Subscribe
                    </Button>
                  </Link>
                )}
              </div>
            </Card>
          ) : (
            <TrialButton
              onSubscriptionOpen={() => setIsSubscriptionOpen(true)}
            />
          )}
        </div>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            {subjectType === 'plant' ? (
              <Leaf className="w-8 h-8 text-green-600" />
            ) : (
              <Leaf className="w-8 h-8 text-blue-600" />
            )}
            <h1 className="text-4xl font-bold text-gray-900">
              {subjectType === 'plant' ? 'Detect Plant Disease' : 'Analyze Livestock Health'}
            </h1>
          </div>
          <p className="text-lg text-gray-600">
            {subjectType === 'plant'
              ? 'Upload a photo of your plant to get an instant disease diagnosis and treatment recommendations'
              : 'Upload a photo of your livestock to detect pests, diseases, and health issues'}
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Left Column - Upload */}
          <div>
            <Card className="p-6 shadow-lg">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">
                {subjectType === 'plant' ? 'Upload Plant Image' : 'Upload Livestock Photo'}
              </h2>
              <ImageUpload
                onImageSelect={handleImageSelect}
                isLoading={isAnalyzing}
                subjectType={subjectType}
                onSubjectTypeChange={setSubjectType}
              />

              {isAnalyzing && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
                    <div>
                      <p className="font-medium text-blue-900">Analyzing image...</p>
                      <p className="text-sm text-blue-700">
                        This may take a few moments
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {selectedFile && !isAnalyzing && (
                <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-sm font-medium text-green-900">
                    Ready to analyze: {selectedFile.name}
                  </p>
                </div>
              )}
            </Card>

            {/* Info Card */}
            <Card className="p-6 mt-6 bg-white shadow-lg">
              <h3 className="font-semibold text-gray-900 mb-3">
                {subjectType === 'plant' ? '🌿 Plant Tips for Best Results' : '🐄 Livestock Photography Tips'}
              </h3>
              <ul className="space-y-2 text-sm text-gray-700">
                {subjectType === 'plant' ? (
                  <>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600 font-bold">✓</span>
                      <span>Use clear, well-lit photos of affected areas</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600 font-bold">✓</span>
                      <span>Focus on leaves, stems, and any visible damage</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600 font-bold">✓</span>
                      <span>Avoid shadows and reflections</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600 font-bold">✓</span>
                      <span>Formats: JPG, PNG, WebP (Max 5MB)</span>
                    </li>
                  </>
                ) : (
                  <>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-600 font-bold">✓</span>
                      <span>Capture clear, close-up images of the affected area</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-600 font-bold">✓</span>
                      <span>Ensure good lighting to show skin/coat condition</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-600 font-bold">✓</span>
                      <span>Include visible pests, wounds, or skin abnormalities</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-600 font-bold">✓</span>
                      <span>Formats: JPG, PNG, WebP (Max 5MB)</span>
                    </li>
                  </>
                )}
              </ul>
            </Card>
          </div>

          {/* Right Column - Results */}
          <div>
            {result ? (
              <DetectionResults
                result={result}
                onSave={handleSaveResult}
                isSaving={isSaving}
              />
            ) : (
              <Card className="p-6 h-full flex items-center justify-center bg-white border-2 border-dashed border-gray-300 shadow-lg">
                <div className="text-center">
                  {subjectType === 'plant' ? (
                    <>
                      <Leaf className="w-12 h-12 text-green-400 mx-auto mb-3" />
                      <p className="text-gray-600 font-medium">
                        Upload a plant image to analyze
                      </p>
                    </>
                  ) : (
                    <>
                      <Leaf className="w-12 h-12 text-blue-400 mx-auto mb-3" />
                      <p className="text-gray-600 font-medium">
                        Upload a livestock photo to analyze
                      </p>
                    </>
                  )}
                  <p className="text-sm text-gray-500 mt-1">
                    Results will appear here with confidence scores and expert recommendations
                  </p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* Subscription Modal */}
      <SubscriptionModal
        isOpen={isSubscriptionOpen}
        onClose={() => setIsSubscriptionOpen(false)}
        onSuccess={() => {
          checkPredictAccess();
          loadTrialStatus();
        }}
        trialAttemptsUsed={trialStatus?.attempts_used || demoTrialsUsed}
        trialMaxAttempts={trialStatus?.max_attempts || MAX_DEMO_TRIALS}
      />
    </div>
  );
}
