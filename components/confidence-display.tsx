'use client';

interface ConfidenceDisplayProps {
  confidence: number;
}

export function ConfidenceDisplay({ confidence }: ConfidenceDisplayProps) {
  const getConfidenceColor = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 75) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 90) return 'Very High Confidence';
    if (score >= 75) return 'High Confidence';
    if (score >= 60) return 'Good Confidence';
    return 'Low Confidence';
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-700">
          Detection Confidence
        </span>
        <span className="text-2xl font-bold text-gray-900">
          {confidence.toFixed(1)}%
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full ${getConfidenceColor(confidence)} transition-all duration-500`}
          style={{ width: `${confidence}%` }}
        />
      </div>
      <p className="text-xs text-gray-600 mt-2">
        {getConfidenceLabel(confidence)}
      </p>
    </div>
  );
}
