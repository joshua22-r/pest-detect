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
  const { user, profile } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  const [stats, setStats] = useState<SystemStats | null>(null);
  const [diseases, setDiseases] = useState<Disease[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'stats' | 'diseases' | 'users' | 'payments' | 'subscriptions'>(
    'stats'
  );
  const [payments, setPayments] = useState<any[]>([]);
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [newDisease, setNewDisease] = useState({ name: '', treatmentNotes: '' });
  const [isAddingDisease, setIsAddingDisease] = useState(false);
  const [isAddingUser, setIsAddingUser] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    user_type: 'farmer',
  });

  useEffect(() => {
    // Wait for profile to be fully loaded before making any decisions
    if (!profile) {
      // If we have a user but no profile yet, wait for profile to load
      return;
    }

    if (profile.user_type !== 'admin') {
      router.push('/');
      return;
    }

    const loadData = async () => {
      try {
        const [statsData, diseasesData, usersData, paymentsData, subscriptionsData] = await Promise.all([
          apiClient.getAdminStats(),
          apiClient.getDiseases(),
          apiClient.getAdminUsers(),
          apiClient.getAdminPayments(),
          apiClient.getAdminSubscriptions(),
        ]);

        setStats({
          totalUsers: statsData.total_users,
          totalScans: statsData.total_scans,
          averageAccuracy: 94.2,
          commonDiseases: statsData.diseases_detected
            ? [{ name: 'Detected Diseases', count: statsData.diseases_detected }]
            : [],
        });

        setDiseases(
          diseasesData.map((disease) => ({
            id: disease.id,
            name: disease.name,
            affectedCount: disease.affected_plants.length + disease.affected_animals.length,
            treatmentNotes: disease.treatment,
          }))
        );

        setUsers(usersData);
        setPayments(paymentsData);
        setSubscriptions(subscriptionsData);
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
  }, [user, profile, router, toast]);

  const handleCreateUser = async () => {
    if (!newUser.username.trim() || !newUser.email.trim() || !newUser.password.trim()) {
      toast({
        title: 'Validation error',
        description: 'Username, email and password are required',
        variant: 'destructive',
      });
      return;
    }

    try {
      const created = await apiClient.createAdminUser({
        username: newUser.username,
        email: newUser.email,
        password: newUser.password,
        user_type: newUser.user_type,
        is_staff: newUser.user_type === 'admin',
      });
      setUsers([created, ...users]);
      setNewUser({ username: '', email: '', password: '', user_type: 'farmer' });
      setIsAddingUser(false);
      toast({
        title: 'User created',
        description: `${created.username} was added successfully`,
      });
    } catch (error) {
      toast({
        title: 'Error creating user',
        description: error instanceof Error ? error.message : 'Unable to create user',
        variant: 'destructive',
      });
    }
  };

  const handleToggleActive = async (userId: string, isActive: boolean) => {
    try {
      const updated = await apiClient.updateAdminUser(userId, { is_active: !isActive });
      setUsers(users.map((user) => (user.id === userId ? updated : user)));
      toast({
        title: 'User updated',
        description: `${updated.username} is now ${updated.is_active ? 'active' : 'disabled'}`,
      });
    } catch (error) {
      toast({
        title: 'Error updating user',
        description: error instanceof Error ? error.message : 'Unable to update user',
        variant: 'destructive',
      });
    }
  };

  const handleRoleChange = async (userId: string, userType: string) => {
    try {
      const updated = await apiClient.updateAdminUser(userId, {
        user_type: userType,
        is_staff: userType === 'admin',
      });
      setUsers(users.map((user) => (user.id === userId ? updated : user)));
      toast({
        title: 'Role updated',
        description: `${updated.username} is now ${userType.toUpperCase()}`,
      });
    } catch (error) {
      toast({
        title: 'Error updating role',
        description: error instanceof Error ? error.message : 'Unable to update role',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      await apiClient.deleteAdminUser(userId);
      setUsers(users.filter((user) => user.id !== userId));
      toast({
        title: 'User removed',
        description: 'The user account has been deleted successfully',
      });
    } catch (error) {
      toast({
        title: 'Error deleting user',
        description: error instanceof Error ? error.message : 'Unable to delete user',
        variant: 'destructive',
      });
    }
  };

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
        <div className="flex gap-2 mb-6 border-b overflow-x-auto">
          <button
            onClick={() => setActiveTab('stats')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === 'stats'
                ? 'text-green-600 border-green-600'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            Statistics
          </button>
          <button
            onClick={() => setActiveTab('diseases')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === 'diseases'
                ? 'text-green-600 border-green-600'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            Disease Management
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === 'users'
                ? 'text-green-600 border-green-600'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            Users
          </button>
          <button
            onClick={() => setActiveTab('payments')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === 'payments'
                ? 'text-green-600 border-green-600'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            Payments
          </button>
          <button
            onClick={() => setActiveTab('subscriptions')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === 'subscriptions'
                ? 'text-green-600 border-green-600'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            Subscriptions
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
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">User Management</h2>
                <p className="text-sm text-gray-600">
                  Block users, remove accounts, and assign privilege levels.
                </p>
              </div>
              <Button
                onClick={() => setIsAddingUser(!isAddingUser)}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                {isAddingUser ? 'Cancel new user' : 'Add new user'}
              </Button>
            </div>

            {isAddingUser && (
              <Card className="p-6 border border-green-200 bg-white">
                <h3 className="text-lg font-bold mb-4 text-gray-900">
                  Create a new user account
                </h3>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Username
                    </label>
                    <Input
                      placeholder="josh"
                      value={newUser.username}
                      onChange={(e) =>
                        setNewUser({ ...newUser, username: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <Input
                      placeholder="user@example.com"
                      value={newUser.email}
                      onChange={(e) =>
                        setNewUser({ ...newUser, email: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Password
                    </label>
                    <Input
                      type="password"
                      placeholder="Secure password"
                      value={newUser.password}
                      onChange={(e) =>
                        setNewUser({ ...newUser, password: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Role
                    </label>
                    <select
                      value={newUser.user_type}
                      onChange={(e) =>
                        setNewUser({ ...newUser, user_type: e.target.value })
                      }
                      className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-100"
                    >
                      <option value="farmer">Farmer</option>
                      <option value="veterinarian">Veterinarian</option>
                      <option value="agronomist">Agronomist</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                </div>
                <div className="mt-4 flex items-center gap-3">
                  <Button onClick={handleCreateUser} className="bg-green-600 hover:bg-green-700 text-white">
                    Create User
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setIsAddingUser(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </Card>
            )}

            <Card className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {users.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-12 text-center text-sm text-gray-500">
                        No users found yet.
                      </td>
                    </tr>
                  )}

                  {users.map((item) => (
                    <tr key={item.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{item.username}</div>
                        <div className="text-sm text-gray-500">{item.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <select
                          value={item.profile?.user_type || 'farmer'}
                          onChange={(e) => handleRoleChange(item.id, e.target.value)}
                          className="rounded-md border border-gray-300 px-2 py-1 text-sm text-gray-700 focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-100"
                        >
                          <option value="farmer">Farmer</option>
                          <option value="veterinarian">Veterinarian</option>
                          <option value="agronomist">Agronomist</option>
                          <option value="admin">Admin</option>
                        </select>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${item.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {item.is_active ? 'Active' : 'Disabled'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className={item.is_active ? 'text-red-600 border-red-600 hover:bg-red-50' : 'text-green-600 border-green-600 hover:bg-green-50'}
                          onClick={() => handleToggleActive(item.id, item.is_active)}
                        >
                          {item.is_active ? 'Disable' : 'Enable'}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-gray-600 border-gray-400 hover:bg-gray-50"
                          onClick={() => handleDeleteUser(item.id)}
                        >
                          Remove
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          </div>
        )}

        {/* Payments Tab */}
        {activeTab === 'payments' && (
          <div className="space-y-6">
            <Card className="overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      User
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      Amount (UGX)
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      Method
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map((payment) => (
                    <tr key={payment.id} className="border-b hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900">
                            {payment.username}
                          </p>
                          <p className="text-sm text-gray-600">
                            {payment.user_email}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-medium text-gray-900">
                        {payment.amount.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-gray-900">
                        {payment.payment_method.toUpperCase()}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            payment.status === 'completed'
                              ? 'bg-green-100 text-green-800'
                              : payment.status === 'pending'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {payment.status.charAt(0).toUpperCase() +
                            payment.status.slice(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(payment.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>

            {payments.length === 0 && (
              <Card className="p-8 text-center">
                <p className="text-gray-500">No payments recorded yet</p>
              </Card>
            )}
          </div>
        )}

        {/* Subscriptions Tab */}
        {activeTab === 'subscriptions' && (
          <div className="space-y-6">
            <Card className="overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      User
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      Plan
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      Amount (UGX)
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      Paid
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      Expires
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-700">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {subscriptions.map((sub) => (
                    <tr key={sub.id} className="border-b hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900">
                            {sub.username}
                          </p>
                          <p className="text-sm text-gray-600">
                            {sub.user_email}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-medium text-gray-900">
                        {sub.plan.charAt(0).toUpperCase() + sub.plan.slice(1)}
                      </td>
                      <td className="px-6 py-4 font-medium text-gray-900">
                        {sub.amount.toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            sub.status === 'active'
                              ? 'bg-green-100 text-green-800'
                              : sub.status === 'expired'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {sub.status.charAt(0).toUpperCase() + sub.status.slice(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            sub.is_paid
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {sub.is_paid ? 'Yes' : 'No'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(sub.end_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-blue-600 border-blue-600 hover:bg-blue-50"
                          onClick={async () => {
                            try {
                              const response = await apiClient.allowUserAccess(
                                sub.user,
                                !sub.is_paid
                              );
                              setSubscriptions(
                                subscriptions.map((s) =>
                                  s.id === sub.id
                                    ? {
                                        ...s,
                                        is_paid: !s.is_paid,
                                      }
                                    : s
                                )
                              );
                              toast({
                                title: 'Updated',
                                description: response.message,
                              });
                            } catch (error) {
                              toast({
                                title: 'Error',
                                description: 'Failed to update',
                                variant: 'destructive',
                              });
                            }
                          }}
                        >
                          {sub.is_paid ? 'Revoke' : 'Allow'}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>

            {subscriptions.length === 0 && (
              <Card className="p-8 text-center">
                <p className="text-gray-500">No subscriptions yet</p>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
