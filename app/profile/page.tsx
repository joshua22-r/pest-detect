'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { User, Mail, Lock, Calendar, Leaf } from 'lucide-react';

export default function ProfilePage() {
  const { user, profile } = useAuth();
  const { toast } = useToast();

  const displayName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.username || '';
  const displayRole = profile?.user_type?.toUpperCase() || 'USER';
  const roleDescription = profile?.user_type === 'admin'
    ? 'Administrator Access'
    : profile?.user_type === 'veterinarian'
      ? 'Veterinarian Access'
      : profile?.user_type === 'agronomist'
        ? 'Agronomist Access'
        : 'Standard User';

  const [formData, setFormData] = useState({
    name: displayName,
    email: user?.email || '',
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [isEditingPassword, setIsEditingPassword] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleProfileChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handlePasswordChange = (field: string, value: string) => {
    setPasswordData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      toast({
        title: 'Profile updated',
        description: 'Your profile has been saved successfully',
      });

      setIsEditingProfile(false);
    } catch (error) {
      toast({
        title: 'Update failed',
        description: 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast({
        title: 'Passwords do not match',
        description: 'Please ensure both passwords are the same',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      toast({
        title: 'Password changed',
        description: 'Your password has been updated successfully',
      });

      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      setIsEditingPassword(false);
    } catch (error) {
      toast({
        title: 'Change failed',
        description: 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-green-600 to-blue-600 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
              <p className="text-lg text-gray-600">
                Manage your account information and preferences
              </p>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Profile Stats */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="p-6 border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100">
              <div className="flex items-center justify-between mb-4">
                <Leaf className="w-8 h-8 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-green-600 mb-1">{profile?.total_scans || 0}</div>
              <p className="text-sm text-gray-600 font-medium">Total Scans</p>
            </Card>

            <Card className="p-6 border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100">
              <div className="flex items-center justify-between mb-4">
                <Calendar className="w-8 h-8 text-blue-600" />
              </div>
              <div className="text-lg font-bold text-blue-600 mb-1">
                Member
              </div>
              <p className="text-sm text-gray-600 font-medium">Member Since</p>
            </Card>

            <Card className="p-6 border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-purple-600 bg-purple-100 px-3 py-1 rounded-full">
                  {displayRole}
                </span>
              </div>
              <div className="text-lg font-bold text-gray-900 mb-1">User Role</div>
              <p className="text-sm text-gray-600">
                {roleDescription}
              </p>
            </Card>
          </div>

          {/* Profile Information */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="p-8 border-0 shadow-lg bg-white">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                  <User className="w-6 h-6 mr-2 text-green-600" />
                  Profile Information
                </h2>
                {!isEditingProfile && (
                  <Button
                    variant="outline"
                    className="border-green-600 text-green-600 hover:bg-green-50"
                    onClick={() => setIsEditingProfile(true)}
                  >
                    Edit Profile
                  </Button>
                )}
              </div>

          {isEditingProfile ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <Input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleProfileChange('name', e.target.value)}
                  disabled={isSaving}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleProfileChange('email', e.target.value)}
                  disabled={isSaving}
                />
              </div>

              <div className="flex gap-2 pt-4">
                <Button
                  onClick={handleSaveProfile}
                  disabled={isSaving}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button
                  onClick={() => {
                    setIsEditingProfile(false);
                    setFormData({
                      name: displayName,
                      email: user?.email || '',
                    });
                  }}
                  variant="outline"
                  disabled={isSaving}
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-3 pb-4 border-b">
                <User className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-600">Full Name</p>
                  <p className="text-lg font-medium text-gray-900">{displayName}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-600">Email Address</p>
                  <p className="text-lg font-medium text-gray-900">{user?.email}</p>
                </div>
              </div>
            </div>
          )}
            </Card>

            {/* Change Password */}
            <Card className="p-8 border-0 shadow-lg bg-white">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <Lock className="w-6 h-6 text-orange-600" />
                  Change Password
                </h2>
                {!isEditingPassword && (
                  <Button
                    variant="outline"
                    className="border-orange-600 text-orange-600 hover:bg-orange-50"
                    onClick={() => setIsEditingPassword(true)}
                  >
                    Update Password
                  </Button>
                )}
              </div>

          {isEditingPassword ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Password
                </label>
                <Input
                  type="password"
                  placeholder="••••••••"
                  value={passwordData.currentPassword}
                  onChange={(e) =>
                    handlePasswordChange('currentPassword', e.target.value)
                  }
                  disabled={isSaving}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  New Password
                </label>
                <Input
                  type="password"
                  placeholder="••••••••"
                  value={passwordData.newPassword}
                  onChange={(e) =>
                    handlePasswordChange('newPassword', e.target.value)
                  }
                  disabled={isSaving}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm New Password
                </label>
                <Input
                  type="password"
                  placeholder="••••••••"
                  value={passwordData.confirmPassword}
                  onChange={(e) =>
                    handlePasswordChange('confirmPassword', e.target.value)
                  }
                  disabled={isSaving}
                />
              </div>

              <div className="flex gap-2 pt-4">
                <Button
                  onClick={handleChangePassword}
                  disabled={isSaving}
                  className="bg-orange-600 hover:bg-orange-700 text-white"
                >
                  {isSaving ? 'Updating...' : 'Update Password'}
                </Button>
                <Button
                  onClick={() => {
                    setIsEditingPassword(false);
                    setPasswordData({
                      currentPassword: '',
                      newPassword: '',
                      confirmPassword: '',
                    });
                  }}
                  variant="outline"
                  disabled={isSaving}
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <p className="text-gray-600">
              Keep your account secure by updating your password regularly.
            </p>
          )}
        </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
