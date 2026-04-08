'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/auth-context';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Leaf, ImagePlus, History, TrendingUp, Bug, Zap, User } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface Stats {
  totalScans: number;
  plantScans: number;
  animalScans: number;
  commonDiseases: Array<{ name: string; count: number }>;
}

export default function Home() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    // Load real stats from API
    if (isAuthenticated) {
      const loadStats = async () => {
        try {
          const statsData = await apiClient.getSystemStats();
          setStats({
            totalScans: statsData.total_scans,
            plantScans: statsData.plant_scans,
            animalScans: statsData.animal_scans,
            commonDiseases: statsData.diseases_detected ? [{ name: 'Total Diseases Detected', count: statsData.diseases_detected }] : [],
          });
        } catch (error) {
          console.error('Failed to load stats:', error);
          // Fallback to mock data if API fails
          setStats({
            totalScans: 0,
            plantScans: 0,
            animalScans: 0,
            commonDiseases: [],
          });
        }
      };
      loadStats();
    }
  }, [isAuthenticated]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Leaf className="w-12 h-12 text-green-600 animate-bounce mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-emerald-50">
        {/* Hero Section */}
        <section className="relative overflow-hidden py-20 px-4 sm:px-6 lg:px-8">
          <div className="absolute inset-0 bg-gradient-to-r from-green-400/10 to-blue-400/10"></div>
          <div className="relative max-w-7xl mx-auto text-center">
            <div className="mb-8 inline-flex items-center justify-center gap-4 bg-white/80 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <div className="flex gap-2">
                <Leaf className="w-8 h-8 text-green-600 animate-pulse" />
                <Zap className="w-8 h-8 text-blue-600 animate-pulse" />
              </div>
              <span className="text-lg font-semibold text-gray-700">BioGuard AI</span>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              AI-Powered Health Detection for
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-blue-600"> Plants & Livestock</span>
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
              Instantly detect diseases and pests in plants and livestock. Get real-time diagnosis, treatment recommendations, and prevention tips powered by advanced AI technology.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/auth/register">
                <Button size="lg" className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-8 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                  Get Started Free
                </Button>
              </Link>
              <Link href="/auth/login">
                <Button size="lg" variant="outline" className="border-2 border-green-600 text-green-600 hover:bg-green-50 px-8 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300">
                  Sign In
                </Button>
              </Link>
            </div>
            <div className="mt-12 flex justify-center">
              <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
                <p className="text-sm text-gray-600 mb-2">Trusted by farmers and veterinarians worldwide</p>
                <div className="flex items-center justify-center gap-4">
                  <div className="flex -space-x-2">
                    <div className="w-8 h-8 bg-green-500 rounded-full border-2 border-white"></div>
                    <div className="w-8 h-8 bg-blue-500 rounded-full border-2 border-white"></div>
                    <div className="w-8 h-8 bg-purple-500 rounded-full border-2 border-white"></div>
                    <div className="w-8 h-8 bg-orange-500 rounded-full border-2 border-white"></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700">10,000+ users</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
                Why Choose BioGuard AI?
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Advanced technology meets agricultural expertise to protect your crops and livestock
              </p>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
              <Card className="p-8 hover:shadow-xl transition-all duration-300 transform hover:scale-105 border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100">
                <div className="w-16 h-16 bg-green-600 rounded-2xl flex items-center justify-center mb-6">
                  <ImagePlus className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-gray-900">Instant Detection</h3>
                <p className="text-gray-600 leading-relaxed">
                  Upload a photo and get instant disease/pest identification in seconds for plants and livestock with our advanced AI algorithms.
                </p>
              </Card>
              <Card className="p-8 hover:shadow-xl transition-all duration-300 transform hover:scale-105 border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100">
                <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mb-6">
                  <TrendingUp className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-gray-900">Expert Accuracy</h3>
                <p className="text-gray-600 leading-relaxed">
                  Advanced AI model with 95%+ accuracy for disease and pest detection across all species, validated by agricultural experts.
                </p>
              </Card>
              <Card className="p-8 hover:shadow-xl transition-all duration-300 transform hover:scale-105 border-0 shadow-lg bg-gradient-to-br from-emerald-50 to-emerald-100">
                <div className="w-16 h-16 bg-emerald-600 rounded-2xl flex items-center justify-center mb-6">
                  <History className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-gray-900">Track Progress</h3>
                <p className="text-gray-600 leading-relaxed">
                  Keep detailed history of all scans with treatment tracking and prevention recommendations for better farm management.
                </p>
              </Card>
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-green-600 to-blue-600">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
              <div className="text-white">
                <div className="text-4xl font-bold mb-2">10,000+</div>
                <p className="text-green-100">Active Users</p>
              </div>
              <div className="text-white">
                <div className="text-4xl font-bold mb-2">500K+</div>
                <p className="text-green-100">Scans Completed</p>
              </div>
              <div className="text-white">
                <div className="text-4xl font-bold mb-2">95%</div>
                <p className="text-green-100">Accuracy Rate</p>
              </div>
              <div className="text-white">
                <div className="text-4xl font-bold mb-2">24/7</div>
                <p className="text-green-100">AI Support</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900 text-white">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl sm:text-4xl font-bold mb-6">
              Start Protecting Your Crops & Livestock Today
            </h2>
            <p className="text-lg mb-8 opacity-90 max-w-2xl mx-auto">
              Join thousands of farmers, veterinarians, and agricultural professionals using BioGuard AI to maintain healthy crops and livestock.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/auth/register">
                <Button size="lg" className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-8 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                  Create Free Account
                </Button>
              </Link>
              <Link href="/predict">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-gray-900 px-8 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300">
                  Try Demo
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="mb-6 lg:mb-0">
              <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-2">
                Welcome back, {user?.first_name || user?.username}!
              </h1>
              <p className="text-lg text-gray-600">
                Monitor your plant and livestock health with AI-powered disease detection
              </p>
            </div>
            <div className="flex gap-4">
              <Link href="/predict">
                <Button className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-6 py-3 font-semibold shadow-lg hover:shadow-xl transition-all duration-300">
                  <ImagePlus className="w-5 h-5 mr-2" />
                  New Scan
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Link href="/predict">
            <Card className="p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100">
              <div className="w-12 h-12 bg-green-600 rounded-xl flex items-center justify-center mb-4">
                <ImagePlus className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-gray-900">New Scan</h3>
              <p className="text-gray-600">
                Upload a plant or livestock image to detect diseases and pests
              </p>
            </Card>
          </Link>
          <Link href="/history">
            <Card className="p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100">
              <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mb-4">
                <History className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-gray-900">View History</h3>
              <p className="text-gray-600">
                Check your previous scans and track treatment progress
              </p>
            </Card>
          </Link>
          <Link href="/profile">
            <Card className="p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100 sm:col-span-2 lg:col-span-1">
              <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center mb-4">
                <User className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-gray-900">My Profile</h3>
              <p className="text-gray-600">
                View your account information and statistics
              </p>
            </Card>
          </Link>
        </div>

        {/* Statistics */}
        {stats && (
          <Card className="p-8 border-0 shadow-lg bg-white">
            <h2 className="text-2xl font-bold mb-6 text-gray-900 flex items-center">
              <TrendingUp className="w-6 h-6 mr-2 text-green-600" />
              Your Statistics
            </h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-xl">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  {stats.totalScans}
                </div>
                <p className="text-gray-600 font-medium">Total Scans</p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl">
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {stats.plantScans}
                </div>
                <p className="text-gray-600 font-medium">Plant Scans</p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl">
                <div className="text-3xl font-bold text-orange-600 mb-2">
                  {stats.animalScans}
                </div>
                <p className="text-gray-600 font-medium">Animal Scans</p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl">
                <div className="text-3xl font-bold text-purple-600 mb-2">
                  {stats.commonDiseases.length}
                </div>
                <p className="text-gray-600 font-medium">Diseases Detected</p>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
