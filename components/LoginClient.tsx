'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useAuth } from '@/contexts/auth-context';
import { useToast } from '@/hooks/use-toast';
import { Spinner } from '@/components/ui/spinner';

export function LoginClient() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [socialLoading, setSocialLoading] = useState<'google' | 'facebook' | null>(null);
  const router = useRouter();
  const { login, socialLogin } = useAuth();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(username, password);
      toast({
        title: 'Login successful',
        description: 'Welcome back!',
      });
      // Redirection is now handled in the auth context
    } catch (error) {
      console.error('[v0] Login error:', error);
      const message = error instanceof Error ? error.message : (typeof error === 'object' && error !== null ? JSON.stringify(error) : 'Please check your credentials');
      toast({
        title: 'Login failed',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'facebook') => {
    setSocialLoading(provider);
    try {
      if (provider === 'google') {
        const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

        // Check if Google Client ID is properly configured
        if (!googleClientId || googleClientId.includes('your-google') || googleClientId.length < 20) {
          toast({
            title: 'Google Sign-In not configured',
            description: 'Please configure NEXT_PUBLIC_GOOGLE_CLIENT_ID in your environment variables',
            variant: 'destructive',
          });
          setSocialLoading(null);
          return;
        }

        // Initialize Google Identity Services
        if (!window.google) {
          // Load Google Identity Services script if not loaded
          await new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://accounts.google.com/gsi/client';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
          });
        }

        // Initialize Google Sign-In
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: async (response: any) => {
            try {
              // Send the ID token to backend
              await socialLogin('google', response.credential, 'credential');
              toast({
                title: 'Login successful',
                description: 'Welcome back from Google!',
              });
            } catch (error) {
              console.error('Google login error:', error);
              toast({
                title: 'Google login failed',
                description: 'Please try again',
                variant: 'destructive',
              });
            } finally {
              setSocialLoading(null);
            }
          },
        });

        // Show Google Sign-In prompt
        window.google.accounts.id.prompt();
      }
    } catch (error) {
      console.error('Social login error:', error);
      toast({
        title: 'Social login failed',
        description: 'Please try again',
        variant: 'destructive',
      });
      setSocialLoading(null);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-blue-50 to-emerald-50 px-4">
      <Card className="w-full max-w-md p-8 shadow-lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
          <p className="text-gray-600">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Username or Email
            </label>
            <Input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="Enter your username or email"
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
              disabled={isLoading}
            />
          </div>

          <div className="flex items-center justify-between">
            <Link
              href="/auth/forgot-password"
              className="text-sm text-green-600 hover:text-green-700"
            >
              Forgot password?
            </Link>
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white"
          >
            {isLoading ? <Spinner /> : 'Sign In'}
          </Button>
        </form>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or continue with</span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <Button
              variant="outline"
              onClick={() => handleSocialLogin('google')}
              disabled={socialLoading !== null}
              className="w-full"
            >
              {socialLoading === 'google' ? <Spinner /> : 'Google'}
            </Button>
            <Button
              variant="outline"
              onClick={() => handleSocialLogin('facebook')}
              disabled={socialLoading !== null}
              className="w-full"
            >
              {socialLoading === 'facebook' ? <Spinner /> : 'Facebook'}
            </Button>
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <Link href="/auth/register" className="text-green-600 hover:text-green-700 font-medium">
              Sign up
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
}