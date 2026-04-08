'use client';

import { useState } from 'react';
import { ImageUpload, SubjectType } from '@/components/image-upload';
import { DetectionResults, DetectionResult } from '@/components/detection-results';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Leaf, Zap } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function PredictPage() {
  const [subjectType, setSubjectType] = useState<SubjectType>('plant');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const { toast } = useToast();

  const handleImageSelect = async (file: File, type: SubjectType) => {
    setSelectedFile(file);
    setIsAnalyzing(true);

    try {
      // Call real API
      const result = await apiClient.predict(file, type);

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
    <div className="min-h-[calc(100vh-64px)] py-8 px-4 bg-gradient-to-br from-blue-50 to-green-50">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            {subjectType === 'plant' ? (
              <Leaf className="w-8 h-8 text-green-600" />
            ) : (
              <Zap className="w-8 h-8 text-blue-600" />
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
                      <Zap className="w-12 h-12 text-blue-400 mx-auto mb-3" />
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
    </div>
  );
}
