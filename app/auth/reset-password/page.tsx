import { Suspense } from 'react';
import ResetPasswordClient from '@/components/ResetPasswordClient';

export const dynamic = 'force-dynamic';

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-gray-50"><p className="text-gray-600">Loading...</p></div>}>
      <ResetPasswordClient />
    </Suspense>
  );
}