'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useAuth } from '@/contexts/auth-context';
import { useToast } from '@/hooks/use-toast';
import { Spinner } from '@/components/ui/spinner';

// Type declarations for global objects
declare global {
  interface Window {
    google?: any;
    FB?: any;
    fbAsyncInit?: () => void;
  }
}

export function LoginClient() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [socialLoading, setSocialLoading] = useState<'google' | 'facebook' | null>(null);
  const [isAuthChecking, setIsAuthChecking] = useState(true);
  const router = useRouter();
  const { login, socialLogin, user, isLoading: authIsLoading } = useAuth();
  const { toast } = useToast();

  // Redirect if already logged in
  useEffect(() => {
    if (!authIsLoading) {
      if (user) {
        // User is already logged in, redirect to dashboard
        router.push('/predict');
      }
      setIsAuthChecking(false);
    }
  }, [user, authIsLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate input
    if (!username.trim()) {
      toast({
        title: 'Validation error',
        description: 'Please enter your username or email',
        variant: 'destructive',
      });
      return;
    }

    if (!password.trim()) {
      toast({
        title: 'Validation error',
        description: 'Please enter your password',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);

    try {
      await login(username, password);
      // Toast and redirection are now handled in the auth context
    } catch (error) {
      console.error('[LoginClient] Login error:', error);
      const message = error instanceof Error ? error.message : (typeof error === 'object' && error !== null ? (error as any)?.description || JSON.stringify(error) : 'Please check your credentials');
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

        if (!googleClientId || googleClientId.includes('your-google') || googleClientId.length < 20) {
          toast({
            title: 'Google Sign-In not configured',
            description: 'Please configure NEXT_PUBLIC_GOOGLE_CLIENT_ID in environment variables',
            variant: 'destructive',
          });
          setSocialLoading(null);
          return;
        }

        // Load Google Identity Services if not already loaded
        if (!window.google) {
          await new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://accounts.google.com/gsi/client';
            script.async = true;
            script.defer = true;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
          });
        }

        // Use OAuth popup flow
        const redirectUri = `${window.location.origin}/auth/google-callback`;
        const scope = encodeURIComponent('openid email profile');
        const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?
          client_id=${googleClientId}&
          redirect_uri=${encodeURIComponent(redirectUri)}&
          response_type=token%20id_token&
          scope=${scope}&
          nonce=${Math.random().toString(36).substring(2, 15)}`;

        // Open popup window
        const width = 500;
        const height = 600;
        const left = window.screenX + (window.outerWidth - width) / 2;
        const top = window.screenY + (window.outerHeight - height) / 2;

        const popup = window.open(
          googleAuthUrl,
          'GoogleSignIn',
          `width=${width},height=${height},left=${left},top=${top}`
        );

        if (!popup) {
          toast({
            title: 'Popup blocked',
            description: 'Please allow popups for Google Sign-In to work',
            variant: 'destructive',
          });
          setSocialLoading(null);
          return;
        }

        // Listen for message from callback (in production, use a proper OAuth library)
        window.addEventListener('message', async (event) => {
          if (event.origin !== window.location.origin) return;

          if (event.data.type === 'GOOGLE_LOGIN_SUCCESS') {
            try {
              await socialLogin('google', event.data.credential, 'credential');
              popup?.close();
            } catch (error) {
              console.error('Google login error:', error);
              toast({
                title: 'Login failed',
                description: error instanceof Error ? error.message : 'Please try again',
                variant: 'destructive',
              });
            } finally {
              setSocialLoading(null);
            }
          }
        });
      } else if (provider === 'facebook') {
        const facebookAppId = process.env.NEXT_PUBLIC_FACEBOOK_APP_ID;

        if (!facebookAppId || facebookAppId.includes('your-facebook') || facebookAppId.length < 10) {
          toast({
            title: 'Facebook Sign-In not configured',
            description: 'Please configure NEXT_PUBLIC_FACEBOOK_APP_ID in environment variables',
            variant: 'destructive',
          });
          setSocialLoading(null);
          return;
        }

        // Load Facebook SDK if not already loaded
        if (!window.FB) {
          await new Promise((resolve) => {
            window.fbAsyncInit = function () {
              FB.init({
                appId: facebookAppId,
                xfbml: true,
                version: 'v18.0',
              });
              resolve(null);
            };

            // Load FB SDK
            const script = document.createElement('script');
            script.src = 'https://connect.facebook.net/en_US/sdk.js';
            script.async = true;
            script.defer = true;
            document.head.appendChild(script);
          });
        }

        // Open Facebook login popup
        const width = 500;
        const height = 600;
        const left = window.screenX + (window.outerWidth - width) / 2;
        const top = window.screenY + (window.outerHeight - height) / 2;

        FB.login(
          async (response: any) => {
            if (response.authResponse) {
              try {
                await socialLogin('facebook', response.authResponse.accessToken, 'access_token');
                toast({
                  title: 'Login successful',
                  description: 'Welcome from Facebook!',
                });
              } catch (error) {
                console.error('Facebook login error:', error);
                toast({
                  title: 'Login failed',
                  description: error instanceof Error ? error.message : 'Please try again',
                  variant: 'destructive',
                });
              } finally {
                setSocialLoading(null);
              }
            } else {
              toast({
                title: 'Login canceled',
                description: 'You cancelled the login process',
                variant: 'default',
              });
              setSocialLoading(null);
            }
          },
          { scope: 'public_profile,email', width, height, left, top }
        );
      }
    } catch (error) {
      console.error('Social login error:', error);
      toast({
        title: 'Social login error',
        description: error instanceof Error ? error.message : 'Please try again',
        variant: 'destructive',
      });
      setSocialLoading(null);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-blue-50 to-emerald-50 px-4">
      {isAuthChecking || user ? (
        <div className="text-center">
          <Spinner />
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      ) : (
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
      )}
    </div>
  );
}