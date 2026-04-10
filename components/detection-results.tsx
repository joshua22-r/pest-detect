'use client';

import { AlertCircle, CheckCircle, AlertTriangle, Pill, Zap } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ConfidenceDisplay } from './confidence-display';
import { SubjectType } from './image-upload';

export interface DetectionResult {
  id: string;
  disease: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high';
  treatment: string;
  prevention: string;
  affectedPlants?: string[];
  affectedAnimals?: string[];
  subjectType: SubjectType;
  timestamp: string;
}

interface DetectionResultsProps {
  result: DetectionResult;
  onSave?: () => void;
  isSaving?: boolean;
}

export function DetectionResults({
  result,
  onSave,
  isSaving = false,
}: DetectionResultsProps) {
  const isHealthy = result.disease.toLowerCase() === 'healthy';
  const isPlant = result.subjectType === 'plant';
  const severityColor = {
    low: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    medium: 'text-orange-600 bg-orange-50 border-orange-200',
    high: 'text-red-600 bg-red-50 border-red-200',
  };
  const borderColor = isPlant ? 'border-l-green-600' : 'border-l-blue-600';

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <Card className={`p-6 border-l-4 ${borderColor}`}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-4">
            {isHealthy ? (
              <CheckCircle className={`w-8 h-8 flex-shrink-0 mt-1 ${isPlant ? 'text-green-600' : 'text-blue-600'}`} />
            ) : (
              <AlertCircle className="w-8 h-8 text-orange-600 flex-shrink-0 mt-1" />
            )}
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-2xl font-bold text-gray-900">
                  {result.disease}
                </h2>
                <span className="text-xs px-2 py-1 bg-gray-200 rounded-full text-gray-700 font-medium">
                  {isPlant ? '🌿 Plant' : '🐄 Livestock'}
                </span>
              </div>
              <p className="text-sm text-gray-500">
                Detected at {new Date(result.timestamp).toLocaleDateString()}
              </p>
            </div>
          </div>
          {!isHealthy && (
            <span className={`px-3 py-1 rounded-full text-sm font-medium border ${severityColor[result.severity]}`}>
              {result.severity.charAt(0).toUpperCase() + result.severity.slice(1)} Severity
            </span>
          )}
        </div>

        {/* Confidence Score */}
        <div className="mb-6">
          <ConfidenceDisplay confidence={result.confidence} />
        </div>

        {/* Disease Description */}
        {!isHealthy && (
          <p className="text-gray-700 mb-6">
            Your {isPlant ? 'plant' : 'livestock'} shows signs of {result.disease}. Early intervention is important to prevent spread.
          </p>
        )}

        {/* Analysis Feedback */}
        {result.notes && (
          <div className="mb-6 p-4 bg-slate-50 rounded border border-slate-200">
            <p className="text-sm font-medium text-slate-900 mb-2">What this means</p>
            <p className="text-gray-700">{result.notes}</p>
          </div>
        )}

        {/* Affected Items */}
        {!isHealthy && (
          <div className="pt-4 border-t">
            <p className="text-sm font-medium text-gray-700 mb-2">
              Commonly affects:
            </p>
            <div className="flex flex-wrap gap-2">
              {isPlant && result.affectedPlants?.map((plant) => (
                <span key={plant} className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                  {plant}
                </span>
              ))}
              {!isPlant && result.affectedAnimals?.map((animal) => (
                <span key={animal} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                  {animal}
                </span>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Treatment Information */}
      {!isHealthy && (
        <Card className="p-6 bg-blue-50 border-l-4 border-l-blue-600">
          <div className="flex items-start gap-3 mb-3">
            <Zap className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <h3 className="text-lg font-semibold text-gray-900">What to do next</h3>
          </div>
          <div className="bg-white p-4 rounded border border-blue-200">
            <p className="text-gray-700">{result.treatment}</p>
          </div>
        </Card>
      )}

      {/* Prevention Information */}
      <Card className="p-6 bg-amber-50 border-l-4 border-l-amber-600">
        <div className="flex items-start gap-3 mb-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <h3 className="text-lg font-semibold text-gray-900">Prevention & Best Practices</h3>
        </div>
        <div className="bg-white p-4 rounded border border-amber-200">
          <p className="text-gray-700">{result.prevention}</p>
        </div>
      </Card>

      {/* Action Button */}
      {onSave && (
        <Button
          onClick={onSave}
          disabled={isSaving}
          className="w-full bg-green-600 hover:bg-green-700 text-white"
        >
          {isSaving ? 'Saving...' : 'Save to History'}
        </Button>
      )}
    </div>
  );
}
