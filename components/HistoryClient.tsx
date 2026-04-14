'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Search, Calendar, TrendingUp, Trash2, Eye, Leaf, Zap, Loader } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface ScanRecord {
  id: string;
  disease: string;
  confidence: number;
  date: string;
  severity: 'low' | 'medium' | 'high';
  subjectType: 'plant' | 'animal';
  imageUrl?: string;
}

export default function HistoryClient() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [scans, setScans] = useState<ScanRecord[]>([]);
  const [filteredScans, setFilteredScans] = useState<ScanRecord[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDisease, setFilterDisease] = useState<string>('all');
  const [filterType, setFilterType] = useState<'all' | 'plant' | 'animal'>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedScan, setSelectedScan] = useState<ScanRecord | null>(null);
  const { toast } = useToast();

  // Check authentication
  useEffect(() => {
    if (!authLoading && !user) {
      setIsRedirecting(true);
      router.push('/auth/login?from=/history');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    const loadScans = async () => {
      try {
        const historyResponse = await apiClient.getDetectionHistory();
        const history = Array.isArray(historyResponse)
          ? historyResponse
          : (historyResponse as any).results || [];

        const transformedScans: ScanRecord[] = history.map((scan: any) => ({
          id: scan.id,
          disease: scan.disease_name,
          confidence: scan.confidence,
          date: scan.created_at,
          severity: scan.severity as 'low' | 'medium' | 'high',
          subjectType: scan.subject_type,
          imageUrl: scan.image,
        }));

        setScans(transformedScans);
        setFilteredScans(transformedScans);
      } catch (error) {
        console.error('Failed to load scan history:', error);
        toast({
          title: 'Failed to load history',
          description: 'Please try refreshing the page',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadScans();
  }, [toast]);

  useEffect(() => {
    let filtered = scans;

    if (filterType !== 'all') {
      filtered = filtered.filter((scan) => scan.subjectType === filterType);
    }

    if (filterDisease !== 'all') {
      filtered = filtered.filter((scan) =>
        scan.disease.toLowerCase() === filterDisease.toLowerCase()
      );
    }

    if (searchTerm) {
      filtered = filtered.filter((scan) =>
        scan.disease.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredScans(filtered);
  }, [searchTerm, filterDisease, filterType, scans]);

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this scan?')) {
      setScans(scans.filter((scan) => scan.id !== id));
      toast({
        title: 'Deleted',
        description: 'Scan has been deleted',
      });
    }
  };

  const handleExport = () => {
    const csv = [
      ['Disease', 'Confidence', 'Date', 'Severity'],
      ...filteredScans.map((scan) => [
        scan.disease,
        scan.confidence.toFixed(1),
        new Date(scan.date).toLocaleDateString(),
        scan.severity,
      ]),
    ]
      .map((row) => row.join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scan-history-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();

    toast({
      title: 'Exported',
      description: `${filteredScans.length} scans exported successfully`,
    });
  };

  const uniqueDiseases = Array.from(new Set(scans.map((s) => s.disease)));
  const severityColor = {
    low: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    medium: 'text-orange-600 bg-orange-50 border-orange-200',
    high: 'text-red-600 bg-red-50 border-red-200',
  };

  if (authLoading || isRedirecting) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex items-center justify-center py-8 px-4">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-green-600" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex items-center justify-center py-8 px-4">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-green-200 border-t-green-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading your scan history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-64px)] py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Calendar className="w-8 h-8 text-green-600" />
            <h1 className="text-4xl font-bold text-gray-900">Scan History</h1>
          </div>
          <p className="text-lg text-gray-600">
            View and manage all your plant disease and livestock health scans
          </p>
        </div>

        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className="p-4">
            <div className="text-3xl font-bold text-gray-800">{scans.length}</div>
            <p className="text-sm text-gray-600">Total Scans</p>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-2">
              <Leaf className="w-5 h-5 text-green-600" />
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {scans.filter((s) => s.subjectType === 'plant').length}
                </div>
                <p className="text-xs text-gray-600">Plant Scans</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-blue-600" />
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {scans.filter((s) => s.subjectType === 'animal').length}
                </div>
                <p className="text-xs text-gray-600">Livestock Scans</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="text-3xl font-bold text-orange-600">
              {scans.filter((s) => s.severity === 'high').length}
            </div>
            <p className="text-sm text-gray-600">High Severity</p>
          </Card>
        </div>

        <Card className="p-6 mb-6">
          <div className="space-y-4">
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setFilterType('all')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  filterType === 'all'
                    ? 'bg-gray-800 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All Scans
              </button>
              <button
                onClick={() => setFilterType('plant')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                  filterType === 'plant'
                    ? 'bg-green-600 text-white'
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
              >
                <Leaf className="w-4 h-4" /> Plants
              </button>
              <button
                onClick={() => setFilterType('animal')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                  filterType === 'animal'
                    ? 'bg-blue-600 text-white'
                    : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                }`}
              >
                <Zap className="w-4 h-4" /> Livestock
              </button>
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <Input
                  placeholder="Search disease..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <select
                value={filterDisease}
                onChange={(e) => setFilterDisease(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="all">All Diseases & Conditions</option>
                {uniqueDiseases.map((disease) => (
                  <option key={disease} value={disease}>
                    {disease}
                  </option>
                ))}
              </select>
              <Button
                onClick={handleExport}
                variant="outline"
                className="border-green-600 text-green-600 hover:bg-green-50"
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>
        </Card>

        {filteredScans.length === 0 ? (
          <Card className="p-12 text-center bg-gray-50">
            <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 font-medium mb-2">No scans found</p>
            <p className="text-sm text-gray-500">
              Try adjusting your filters or start a new scan
            </p>
          </Card>
        ) : (
          <div className="grid gap-4">
            {filteredScans.map((scan) => (
              <Card key={scan.id} className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="flex items-center gap-2">
                        {scan.subjectType === 'plant' ? (
                          <Leaf className="w-5 h-5 text-green-600" />
                        ) : (
                          <Zap className="w-5 h-5 text-blue-600" />
                        )}
                        <h3 className="text-lg font-semibold text-gray-900">
                          {scan.disease}
                        </h3>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
                        scan.subjectType === 'plant'
                          ? 'bg-green-50 text-green-700 border-green-200'
                          : 'bg-blue-50 text-blue-700 border-blue-200'
                      }`}>
                        {scan.subjectType === 'plant' ? '🌿 Plant' : '🐄 Livestock'}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium border ${severityColor[scan.severity]}`}>
                        {scan.severity}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>
                        {new Date(scan.date).toLocaleDateString()} at{' '}
                        {new Date(scan.date).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                      <span className="flex items-center gap-1">
                        <TrendingUp className="w-4 h-4 text-green-600" />
                        {scan.confidence.toFixed(1)}% confidence
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-blue-600 border-blue-600 hover:bg-blue-50"
                      onClick={() => setSelectedScan(scan)}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-red-600 border-red-600 hover:bg-red-50"
                      onClick={() => handleDelete(scan.id)}
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Delete
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {selectedScan && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedScan(null)}
          >
            <Card className="max-w-md w-full p-6" onClick={(e) => e.stopPropagation()}>
              <h2 className="text-2xl font-bold mb-4">{selectedScan.disease}</h2>
              <div className="space-y-2 mb-4">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Date:</span>{' '}
                  {new Date(selectedScan.date).toLocaleDateString()}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Confidence:</span> {selectedScan.confidence.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Severity:</span> {selectedScan.severity}
                </p>
              </div>
              <Button
                onClick={() => setSelectedScan(null)}
                className="w-full bg-green-600 hover:bg-green-700 text-white"
              >
                Close
              </Button>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
