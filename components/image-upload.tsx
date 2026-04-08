'use client';

import { useRef, useState } from 'react';
import { Upload, Camera, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export type SubjectType = 'plant' | 'animal';

interface ImageUploadProps {
  onImageSelect: (file: File, subjectType: SubjectType) => void;
  isLoading?: boolean;
  subjectType: SubjectType;
  onSubjectTypeChange: (type: SubjectType) => void;
}

export function ImageUpload({ onImageSelect, isLoading = false, subjectType, onSubjectTypeChange }: ImageUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');

  const handleFileSelect = (file: File | null) => {
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    setFileName(file.name);
    onImageSelect(file, subjectType);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const clearPreview = () => {
    setPreview(null);
    setFileName('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  if (preview) {
    return (
      <div className="space-y-4">
        <Card className="p-6 bg-gray-50">
          <div className="relative">
            <img
              src={preview}
              alt="Preview"
              className="w-full h-64 object-cover rounded-lg"
            />
            <button
              onClick={clearPreview}
              className="absolute top-2 right-2 bg-white rounded-full p-2 hover:bg-gray-100"
              disabled={isLoading}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <p className="mt-4 text-sm text-gray-600 text-center">
            File: {fileName}
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Subject Type Selection */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => onSubjectTypeChange('plant')}
          className={`p-4 rounded-lg border-2 transition-all ${
            subjectType === 'plant'
              ? 'border-green-600 bg-green-50'
              : 'border-gray-200 bg-white hover:border-green-300'
          }`}
        >
          <div className="text-2xl mb-2">🌿</div>
          <div className="font-semibold text-sm text-gray-900">Plant</div>
          <div className="text-xs text-gray-600">Disease Detection</div>
        </button>
        <button
          onClick={() => onSubjectTypeChange('animal')}
          className={`p-4 rounded-lg border-2 transition-all ${
            subjectType === 'animal'
              ? 'border-blue-600 bg-blue-50'
              : 'border-gray-200 bg-white hover:border-blue-300'
          }`}
        >
          <div className="text-2xl mb-2">🐄</div>
          <div className="font-semibold text-sm text-gray-900">Livestock</div>
          <div className="text-xs text-gray-600">Health & Pest Check</div>
        </button>
      </div>
      {/* Drag and Drop Area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-green-300 rounded-lg p-8 bg-green-50 hover:bg-green-100 transition-colors cursor-pointer"
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="text-center">
          <Upload className="w-12 h-12 text-green-600 mx-auto mb-3" />
          <p className="text-lg font-semibold text-gray-900 mb-1">
            Drag and drop your image
          </p>
          <p className="text-sm text-gray-600">
            or click to select from your device
          </p>
          <p className="text-xs text-gray-500 mt-2">
            Supported formats: JPG, PNG, WebP (Max 5MB)
          </p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={(e) => handleFileSelect(e.target.files?.[0] || null)}
          className="hidden"
          disabled={isLoading}
        />
      </div>

      {/* Alternative Actions */}
      <div className="grid md:grid-cols-2 gap-4">
        <Button
          variant="outline"
          className="border-green-600 text-green-600 hover:bg-green-50"
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
        >
          <Upload className="w-4 h-4 mr-2" />
          Choose Image
        </Button>
        <Button
          variant="outline"
          className="border-blue-600 text-blue-600 hover:bg-blue-50"
          onClick={() => cameraInputRef.current?.click()}
          disabled={isLoading}
        >
          <Camera className="w-4 h-4 mr-2" />
          Take Photo
        </Button>
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={(e) => handleFileSelect(e.target.files?.[0] || null)}
          className="hidden"
          disabled={isLoading}
        />
      </div>
    </div>
  );
}
