"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/auth';
import { useAuthStore } from '@/stores/authStore';

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await authApi.login(formData);
      login(result.data.user, result.data.access_token, result.data.refresh_token);
      router.push('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to login. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-primary p-4">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 rounded-full bg-accent-primary-subtle text-accent-primary mb-4 shadow-glow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Trader Copilot AI</h1>
          <p className="text-text-secondary mt-2">Sign in to your account to continue</p>
        </div>

        <div className="card-elevated p-8 rounded-xl border border-border-secondary">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="p-3 text-sm text-color-danger bg-color-danger-subtle border border-color-danger/20 rounded-md">
                {error}
              </div>
            )}
            
            <div>
              <label className="input-label" htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                className="input"
                placeholder="trader@example.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="input-label !mb-0" htmlFor="password">Password</label>
                <Link href="#" className="text-xs text-accent-primary hover:underline">Forgot password?</Link>
              </div>
              <input
                id="password"
                type="password"
                className="input"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary w-full mt-2"
              disabled={isLoading}
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-text-secondary">
            Don't have an account?{' '}
            <Link href="/register" className="text-accent-primary font-medium hover:underline">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
