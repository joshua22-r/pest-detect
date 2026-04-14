'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import { useAuth } from '@/contexts/auth-context';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Monitor, Sun, Moon, Palette, Eye, Layout, Save, RotateCcw, Loader } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

type DisplayMode = 'light' | 'dark' | 'system';
type LayoutMode = 'compact' | 'comfortable' | 'spacious';
type FontSize = 'small' | 'medium' | 'large';

interface DisplaySettings {
  theme: DisplayMode;
  layout: LayoutMode;
  fontSize: FontSize;
  animations: boolean;
  highContrast: boolean;
  reducedMotion: boolean;
}

const defaultSettings: DisplaySettings = {
  theme: 'system',
  layout: 'comfortable',
  fontSize: 'medium',
  animations: true,
  highContrast: false,
  reducedMotion: false,
};

export default function SettingsClient() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const { toast } = useToast();
  const { user, isLoading } = useAuth();
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [settings, setSettings] = useState<DisplaySettings>(defaultSettings);
  const [hasChanges, setHasChanges] = useState(false);

  // Check authentication
  useEffect(() => {
    if (!isLoading && !user) {
      setIsRedirecting(true);
      router.push('/auth/login?from=/settings');
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    const savedSettings = localStorage.getItem('display-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(parsed);
        if (parsed.theme !== theme) {
          setTheme(parsed.theme);
        }
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, [theme, setTheme]);

  const updateSetting = <K extends keyof DisplaySettings>(key: K, value: DisplaySettings[K]) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
    if (key === 'theme') {
      setTheme(value as DisplayMode);
    }
  };

  const saveSettings = () => {
    localStorage.setItem('display-settings', JSON.stringify(settings));
    setHasChanges(false);
    toast({
      title: 'Settings saved',
      description: 'Your display preferences have been updated.',
    });
  };

  const resetSettings = () => {
    setSettings(defaultSettings);
    setTheme('system');
    setHasChanges(true);
    toast({
      title: 'Settings reset',
      description: 'Display settings have been reset to defaults.',
    });
  };

  const getThemeIcon = (mode: DisplayMode) => {
    switch (mode) {
      case 'light': return <Sun className="w-4 h-4" />;
      case 'dark': return <Moon className="w-4 h-4" />;
      case 'system': return <Monitor className="w-4 h-4" />;
    }
  };

  const getLayoutDescription = (layout: LayoutMode) => {
    switch (layout) {
      case 'compact': return 'Tighter spacing, more content visible';
      case 'comfortable': return 'Balanced spacing for readability';
      case 'spacious': return 'Extra padding for relaxed viewing';
    }
  };

  const getFontSizeDescription = (size: FontSize) => {
    switch (size) {
      case 'small': return 'Compact text for more information';
      case 'medium': return 'Standard readable size';
      case 'large': return 'Larger text for better accessibility';
    }
  };

  if (isLoading || isRedirecting) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Palette className="w-8 h-8 text-blue-600" />
            Display Settings
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Customize your viewing experience and interface preferences.
          </p>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="w-5 h-5" />
                Theme & Appearance
              </CardTitle>
              <CardDescription>Choose how the application looks and feels</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <Label className="text-base font-medium">Color Theme</Label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {(['light', 'dark', 'system'] as DisplayMode[]).map((mode) => (
                    <Button
                      key={mode}
                      variant={settings.theme === mode ? 'default' : 'outline'}
                      onClick={() => updateSetting('theme', mode)}
                      className="h-auto p-4 flex flex-col items-center gap-2"
                    >
                      {getThemeIcon(mode)}
                      <span className="capitalize font-medium">{mode}</span>
                      <Badge variant="secondary" className="text-xs">
                        {settings.theme === mode ? 'Active' : 'Inactive'}
                      </Badge>
                    </Button>
                  ))}
                </div>
              </div>

              <Separator />

              <div className="space-y-3">
                <Label className="text-base font-medium">Layout Density</Label>
                <Select
                  value={settings.layout}
                  onValueChange={(value: LayoutMode) => updateSetting('layout', value)}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="compact">
                      <div className="flex flex-col">
                        <span className="font-medium">Compact</span>
                        <span className="text-sm text-muted-foreground">
                          {getLayoutDescription('compact')}
                        </span>
                      </div>
                    </SelectItem>
                    <SelectItem value="comfortable">
                      <div className="flex flex-col">
                        <span className="font-medium">Comfortable</span>
                        <span className="text-sm text-muted-foreground">
                          {getLayoutDescription('comfortable')}
                        </span>
                      </div>
                    </SelectItem>
                    <SelectItem value="spacious">
                      <div className="flex flex-col">
                        <span className="font-medium">Spacious</span>
                        <span className="text-sm text-muted-foreground">
                          {getLayoutDescription('spacious')}
                        </span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Separator />

              <div className="space-y-3">
                <Label className="text-base font-medium">Font Size</Label>
                <Select
                  value={settings.fontSize}
                  onValueChange={(value: FontSize) => updateSetting('fontSize', value)}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="small">
                      <div className="flex flex-col">
                        <span className="font-medium">Small</span>
                        <span className="text-sm text-muted-foreground">
                          {getFontSizeDescription('small')}
                        </span>
                      </div>
                    </SelectItem>
                    <SelectItem value="medium">
                      <div className="flex flex-col">
                        <span className="font-medium">Medium</span>
                        <span className="text-sm text-muted-foreground">
                          {getFontSizeDescription('medium')}
                        </span>
                      </div>
                    </SelectItem>
                    <SelectItem value="large">
                      <div className="flex flex-col">
                        <span className="font-medium">Large</span>
                        <span className="text-sm text-muted-foreground">
                          {getFontSizeDescription('large')}
                        </span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Layout className="w-5 h-5" />
                Accessibility & Motion
              </CardTitle>
              <CardDescription>Adjust settings for better accessibility and comfort</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-base font-medium">Enable Animations</Label>
                  <p className="text-sm text-muted-foreground">Show smooth transitions and animations</p>
                </div>
                <Switch
                  checked={settings.animations}
                  onCheckedChange={(checked) => updateSetting('animations', checked)}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-base font-medium">High Contrast Mode</Label>
                  <p className="text-sm text-muted-foreground">Increase contrast for better visibility</p>
                </div>
                <Switch
                  checked={settings.highContrast}
                  onCheckedChange={(checked) => updateSetting('highContrast', checked)}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-base font-medium">Reduce Motion</Label>
                  <p className="text-sm text-muted-foreground">Minimize animations and transitions</p>
                </div>
                <Switch
                  checked={settings.reducedMotion}
                  onCheckedChange={(checked) => updateSetting('reducedMotion', checked)}
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex flex-col sm:flex-row gap-4 pt-6">
            <Button onClick={saveSettings} disabled={!hasChanges} className="flex-1 sm:flex-none">
              <Save className="w-4 h-4 mr-2" />
              Save Settings
            </Button>
            <Button variant="outline" onClick={resetSettings} className="flex-1 sm:flex-none">
              <RotateCcw className="w-4 h-4 mr-2" />
              Reset to Defaults
            </Button>
          </div>

          <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800">
            <CardHeader>
              <CardTitle className="text-blue-900 dark:text-blue-100">Current Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-medium text-blue-900 dark:text-blue-100">Theme:</span>
                  <span className="ml-2 capitalize">{settings.theme}</span>
                </div>
                <div>
                  <span className="font-medium text-blue-900 dark:text-blue-100">Layout:</span>
                  <span className="ml-2 capitalize">{settings.layout}</span>
                </div>
                <div>
                  <span className="font-medium text-blue-900 dark:text-blue-100">Font Size:</span>
                  <span className="ml-2 capitalize">{settings.fontSize}</span>
                </div>
                <div>
                  <span className="font-medium text-blue-900 dark:text-blue-100">Animations:</span>
                  <span className="ml-2">{settings.animations ? 'Enabled' : 'Disabled'}</span>
                </div>
                <div>
                  <span className="font-medium text-blue-900 dark:text-blue-100">High Contrast:</span>
                  <span className="ml-2">{settings.highContrast ? 'Enabled' : 'Disabled'}</span>
                </div>
                <div>
                  <span className="font-medium text-blue-900 dark:text-blue-100">Reduced Motion:</span>
                  <span className="ml-2">{settings.reducedMotion ? 'Enabled' : 'Disabled'}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
