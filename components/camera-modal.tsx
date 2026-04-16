'use client';

import { useRef, useState, useEffect } from 'react';
import { Camera, X, RotateCcw, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface CameraModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPhotoCapture: (file: File) => void;
  isLoading?: boolean;
}

export function CameraModal({ isOpen, onClose, onPhotoCapture, isLoading = false }: CameraModalProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');

  // Initialize camera when modal opens
  useEffect(() => {
    if (!isOpen) {
      stopCamera();
      return;
    }

    const initCamera = async () => {
      try {
        setCameraError(null);
        setIsCameraReady(false);
        setCapturedImage(null);

        // Stop existing stream before requesting new one
        stopCamera();

        const constraints: MediaStreamConstraints = {
          video: {
            facingMode: { ideal: facingMode },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
          audio: false,
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        streamRef.current = stream;

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play().catch((err) => {
            console.error('Failed to play video:', err);
            setCameraError('Failed to start camera preview. Please try again.');
          });
          setIsCameraReady(true);
        }
      } catch (error: any) {
        console.error('Camera access error:', error);
        if (error.name === 'NotAllowedError') {
          setCameraError('Camera permission denied. Please allow camera access in your browser settings.');
        } else if (error.name === 'NotFoundError') {
          setCameraError('No camera device found on your device.');
        } else if (error.name === 'OverconstrainedError') {
          setCameraError('Requested camera constraints not supported. Please try the other camera.');
        } else {
          setCameraError('Unable to access camera. Please check your device and permissions.');
        }
        setIsCameraReady(false);
      }
    };

    initCamera();

    return () => {
      stopCamera();
    };
  }, [isOpen, facingMode]);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setIsCameraReady(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    try {
      const context = canvasRef.current.getContext('2d');
      if (!context) {
        setCameraError('Failed to capture image. Please try again.');
        return;
      }

      const videoWidth = videoRef.current.videoWidth;
      const videoHeight = videoRef.current.videoHeight;

      if (videoWidth === 0 || videoHeight === 0) {
        setCameraError('Video is not ready. Please wait a moment and try again.');
        return;
      }

      // Set canvas dimensions to match video
      canvasRef.current.width = videoWidth;
      canvasRef.current.height = videoHeight;

      // Draw video frame to canvas
      context.drawImage(videoRef.current, 0, 0);

      // Get image data and set as preview
      const imageData = canvasRef.current.toDataURL('image/jpeg', 0.95);
      setCapturedImage(imageData);
    } catch (error) {
      console.error('Error capturing photo:', error);
      setCameraError('Failed to capture image. Please try again.');
    }
  };

  const resetCapture = () => {
    setCapturedImage(null);
  };

  const toggleFacingMode = () => {
    setFacingMode((prev) => (prev === 'environment' ? 'user' : 'environment'));
  };

  const confirmCapture = async () => {
    if (!capturedImage) return;

    try {
      // Convert data URL to blob directly
      const response = await fetch(capturedImage);
      const blob = await response.blob();

      if (blob.size === 0) {
        setCameraError('Captured image is empty. Please try again.');
        return;
      }

      const file = new File([blob], `plant-photo-${Date.now()}.jpg`, {
        type: 'image/jpeg',
      });

      onPhotoCapture(file);
      setCapturedImage(null);
      onClose();
    } catch (error) {
      console.error('Error processing photo:', error);
      setCameraError('Failed to process captured image. Please try again.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl bg-white shadow-xl">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Take Photo</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={isLoading}
            >
              <X className="w-6 h-6 text-gray-600" />
            </button>
          </div>

          {/* Camera Error */}
          {cameraError && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{cameraError}</p>
              <p className="text-red-600 text-xs mt-2">
                Try using "Choose Image" to upload a photo instead, or check your browser permissions.
              </p>
            </div>
          )}

          {/* Camera View or Captured Image */}
          <div className="relative bg-black rounded-lg overflow-hidden mb-6 aspect-video">
            {!capturedImage ? (
              <>
                <video
                  ref={videoRef}
                  className="w-full h-full object-cover"
                  playsInline
                  style={{ transform: facingMode === 'user' ? 'scaleX(-1)' : 'scaleX(1)' }}
                />
                {!isCameraReady && !cameraError && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75">
                    <div className="text-center">
                      <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                      <p className="text-white">Initializing camera...</p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <img
                src={capturedImage}
                alt="Captured"
                className="w-full h-full object-cover"
              />
            )}
            <canvas ref={canvasRef} className="hidden" />
          </div>

          {/* Instructions */}
          {!capturedImage && isCameraReady && (
            <p className="text-center text-sm text-gray-600 mb-6">
              💡 Position your plant leaf or pest clearly in the center and tap "Capture"
            </p>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 flex-wrap">
            {!capturedImage ? (
              <>
                <Button
                  onClick={capturePhoto}
                  disabled={!isCameraReady || isLoading}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                >
                  <Camera className="w-4 h-4 mr-2" />
                  Capture Photo
                </Button>
                {/* Flip Camera Button - Only show if multiple cameras exist */}
                <Button
                  onClick={toggleFacingMode}
                  disabled={!isCameraReady || isLoading}
                  variant="outline"
                  className="border-blue-600 text-blue-600 hover:bg-blue-50"
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Flip
                </Button>
              </>
            ) : (
              <>
                <Button
                  onClick={resetCapture}
                  disabled={isLoading}
                  variant="outline"
                  className="flex-1"
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Retake
                </Button>
                <Button
                  onClick={confirmCapture}
                  disabled={isLoading}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                >
                  <Check className="w-4 h-4 mr-2" />
                  Use Photo
                </Button>
              </>
            )}
          </div>

          {/* Mobile Instructions */}
          <p className="text-xs text-gray-500 mt-6 text-center">
            💻 Desktop tip: Grant camera permission when prompted by your browser
          </p>
        </div>
      </Card>
    </div>
  );
}
