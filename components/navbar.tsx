'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Menu, X, Leaf, LogOut, User, Zap, ImagePlus, History } from 'lucide-react';

export function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div className="flex gap-1 p-2 bg-gradient-to-r from-green-100 to-blue-100 rounded-lg">
              <Leaf className="w-6 h-6 text-green-600" />
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <span className="text-xl font-bold text-gray-900 hidden sm:block">BioGuard AI</span>
            <span className="text-lg font-bold text-gray-900 sm:hidden">BG AI</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-2">
            {isAuthenticated && (
              <>
                <Link href="/predict">
                  <Button variant="ghost" className="text-gray-700 hover:text-green-600 hover:bg-green-50 font-medium transition-colors">
                    <ImagePlus className="w-4 h-4 mr-2" />
                    Detect & Analyze
                  </Button>
                </Link>
                <Link href="/history">
                  <Button variant="ghost" className="text-gray-700 hover:text-green-600 hover:bg-green-50 font-medium transition-colors">
                    <History className="w-4 h-4 mr-2" />
                    History
                  </Button>
                </Link>
                {user?.role === 'admin' && (
                  <Link href="/admin/dashboard">
                    <Button variant="ghost" className="text-gray-700 hover:text-green-600 hover:bg-green-50 font-medium transition-colors">
                      Admin
                    </Button>
                  </Link>
                )}
              </>
            )}
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="flex items-center gap-2 text-gray-700 hover:text-green-600 hover:bg-green-50 transition-colors"
                  >
                    <div className="w-8 h-8 bg-gradient-to-r from-green-600 to-blue-600 rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 text-white" />
                    </div>
                    <span className="hidden sm:inline font-medium">{user?.first_name || user?.username}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuItem asChild>
                    <Link href="/profile" className="flex items-center">
                      <User className="w-4 h-4 mr-2" />
                      Profile
                    </Link>
                  </DropdownMenuItem>
                  {user?.role === 'admin' && (
                    <DropdownMenuItem asChild>
                      <Link href="/admin/dashboard" className="flex items-center">
                        Admin Dashboard
                      </Link>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600">
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex gap-2">
                <Link href="/auth/login">
                  <Button variant="outline" className="text-green-600 border-green-600 hover:bg-green-50 font-medium">
                    Sign In
                  </Button>
                </Link>
                <Link href="/auth/register">
                  <Button className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-medium shadow-lg hover:shadow-xl transition-all duration-300">
                    Sign Up
                  </Button>
                </Link>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? (
                <X className="w-6 h-6 text-gray-700" />
              ) : (
                <Menu className="w-6 h-6 text-gray-700" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && isAuthenticated && (
          <div className="md:hidden pb-4 border-t border-gray-200 bg-gray-50">
            <div className="px-4 py-2">
              <Link href="/predict" className="flex items-center py-3 px-2 text-gray-700 hover:text-green-600 hover:bg-white rounded-lg transition-colors">
                <ImagePlus className="w-5 h-5 mr-3" />
                Detect & Analyze
              </Link>
              <Link href="/history" className="flex items-center py-3 px-2 text-gray-700 hover:text-green-600 hover:bg-white rounded-lg transition-colors">
                <History className="w-5 h-5 mr-3" />
                History
              </Link>
              <Link href="/profile" className="flex items-center py-3 px-2 text-gray-700 hover:text-green-600 hover:bg-white rounded-lg transition-colors">
                <User className="w-5 h-5 mr-3" />
                Profile
              </Link>
              {user?.role === 'admin' && (
                <Link href="/admin/dashboard" className="flex items-center py-3 px-2 text-gray-700 hover:text-green-600 hover:bg-white rounded-lg transition-colors">
                  Admin Dashboard
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
