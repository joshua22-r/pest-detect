'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/lib/api-client';
import {
  Users,
  Leaf,
  BarChart3,
  Plus,
  Edit,
  Trash2,
  TrendingUp,
} from 'lucide-react';

interface Disease {
  id: string;
  name: string;
  affectedCount: number;
  treatmentNotes: string;
}

interface SystemStats {
  totalUsers: number;
  totalScans: number;
  averageAccuracy: number;
  commonDiseases: Array<{ name: string; count: number }>;
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  const [stats, setStats] = useState<SystemStats | null>(null);
  const [diseases, setDiseases] = useState<Disease[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'stats' | 'diseases' | 'users'>(
    'stats'
  );
  const [newDisease, setNewDisease] = useState({ name: '', treatmentNotes: '' });
  const [isAddingDisease, setIsAddingDisease] = useState(false);

  useEffect(() => {
    // Check if user is admin
    if (user && profile?.user_type !== 'admin') {
      router.push('/');
      return;
    }

    // Load real data from API
    const loadData = async () => {
      try {
        const [statsData, diseasesData] = await Promise.all([
          apiClient.getSystemStats(),
          apiClient.getDiseases()
        ]);

        setStats({
          totalUsers: 0, // TODO: Add user count to API
          totalScans: statsData.total_scans,
          averageAccuracy: 94.2, // TODO: Calculate from API
          commonDiseases: statsData.diseases_detected ? [{ name: 'Detected Diseases', count: statsData.diseases_detected }] : [],
        });

        setDiseases(diseasesData.map(disease => ({
          id: disease.id,
          name: disease.name,
          affectedCount: 0, // TODO: Add affected count to API
          treatmentNotes: disease.treatment,
        })));
      } catch (error) {
        console.error('Failed to load admin data:', error);
        toast({
          title: 'Failed to load data',
          description: 'Please try refreshing the page',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [user, router]);

  const handleAddDisease = async () => {
    if (!newDisease.name.trim()) {
      toast({
        title: 'Validation error',
        description: 'Please enter a disease name',
        variant: 'destructive',
      });
      return;
    }

    try {
      const disease: Disease = {
        id: Date.now().toString(),
        name: newDisease.name,
        affectedCount: 0,
        treatmentNotes: newDisease.treatmentNotes,
      };

      setDiseases([...diseases, disease]);
      setNewDisease({ name: '', treatmentNotes: '' });
      setIsAddingDisease(false);

      toast({
        title: 'Disease added',
        description: `${disease.name} has been added to the database`,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to add disease',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteDisease = (id: string) => {
    if (confirm('Are you sure you want to delete this disease?')) {
      setDiseases(diseases.filter((d) => d.id !== id));
      toast({
        title: 'Deleted',
        description: 'Disease has been removed',
      });
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex items-center justify-center py-8 px-4">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-green-200 border-t-green-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-64px)] py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="w-8 h-8 text-purple-600" />
            <h1 className="text-4xl font-bold text-gray-900">Admin Dashboard</h1>
          </div>
          <p className="text-lg text-gray-600">
            Manage system, diseases, and users
          </p>
        </div>

        {/* System Stats */}
        {stats && (
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.totalUsers}</p>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-600">Total Scans</p>
                <Leaf className="w-5 h-5 text-green-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.totalScans}</p>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-600">Avg Accuracy</p>
                <TrendingUp className="w-5 h-5 text-purple-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">
                {stats.averageAccuracy}%
              </p>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-600">Diseases DB</p>
                <BarChart3 className="w-5 h-5 text-orange-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">{diseases.length}</p>
            </Card>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b">
          <button
            onClick={() => setActiveTab('stats')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'stats'
                ? 'text-green-600 border-green-600'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            Statistics
          </button>
          <button
            onClick={() => setActiveTab('diseases')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'diseases'
                ? 'text-green-600 border-green-600'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            Disease Management
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'users'
                ? 'text-green-600 border-green-600'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            Users
          </button>
        </div>

        {/* Content */}
        {activeTab === 'stats' && stats && (
          <div>
            <Card className="p-6">
              <h2 className="text-xl font-bold mb-4 text-gray-900">
                Top Diseases
              </h2>
              <div className="space-y-3">
                {stats.commonDiseases.map((disease, idx) => (
                  <div key={idx} className="flex items-center justify-between pb-3 border-b last:border-0">
                    <span className="font-medium text-gray-900">
                      {idx + 1}. {disease.name}
                    </span>
                    <span className="text-lg font-bold text-green-600">
                      {disease.count} scans
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'diseases' && (
          <div className="space-y-6">
            {isAddingDisease ? (
              <Card className="p-6 border-2 border-green-200">
                <h3 className="text-lg font-bold mb-4 text-gray-900">
                  Add New Disease
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Disease Name
                    </label>
                    <Input
                      placeholder="e.g., Powdery Mildew"
                      value={newDisease.name}
                      onChange={(e) =>
                        setNewDisease({ ...newDisease, name: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Treatment Notes
                    </label>
                    <textarea
                      placeholder="Enter treatment recommendations..."
                      value={newDisease.treatmentNotes}
                      onChange={(e) =>
                        setNewDisease({
                          ...newDisease,
                          treatmentNotes: e.target.value,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      rows={4}
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={handleAddDisease}
                      className="bg-green-600 hover:bg-green-700 text-white"
                    >
                      Add Disease
                    </Button>
                    <Button
                      onClick={() => {
                        setIsAddingDisease(false);
                        setNewDisease({ name: '', treatmentNotes: '' });
                      }}
                      variant="outline"
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </Card>
            ) : (
              <Button
                onClick={() => setIsAddingDisease(true)}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add New Disease
              </Button>
            )}

            <div className="grid gap-4">
              {diseases.map((disease) => (
                <Card key={disease.id} className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">
                        {disease.name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Affected in {disease.affectedCount} scans
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-blue-600 border-blue-600 hover:bg-blue-50"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-red-600 border-red-600 hover:bg-red-50"
                        onClick={() => handleDeleteDisease(disease.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <p className="text-gray-700">{disease.treatmentNotes}</p>
                </Card>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <Card className="p-6 text-center bg-gray-50">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 font-medium">User Management</p>
            <p className="text-sm text-gray-500 mt-1">
              Advanced user management features coming soon
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}
