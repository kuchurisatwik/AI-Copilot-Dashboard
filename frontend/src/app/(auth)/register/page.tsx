"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/auth';
import { useAuthStore } from '@/stores/authStore';

export default function RegisterPage() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  
  const [formData, setFormData] = useState({ 
    name: '', 
    email: '', 
    password: '',
    account_size: 100000,
    default_risk_pct: 1.0
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setIsLoading(true);

    try {
      const result = await authApi.register(formData);
      login(result.data.user, result.data.access_token, result.data.refresh_token);
      router.push('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create account. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-primary p-4 py-12">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 rounded-full bg-accent-primary-subtle text-accent-primary mb-4 shadow-glow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Create an Account</h1>
          <p className="text-text-secondary mt-2">Join Trader Copilot AI to manage your risk</p>
        </div>

        <div className="card-elevated p-8 rounded-xl border border-border-secondary">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="p-3 text-sm text-color-danger bg-color-danger-subtle border border-color-danger/20 rounded-md">
                {error}
              </div>
            )}
            
            <div>
              <label className="input-label" htmlFor="name">Full Name</label>
              <input
                id="name"
                type="text"
                className="input"
                placeholder="John Doe"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            
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
              <label className="input-label" htmlFor="password">Password (Min 8 chars)</label>
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
            
            <div className="grid grid-cols-2 gap-4 pt-2">
              <div>
                <label className="input-label" htmlFor="account_size">Account Size (₹)</label>
                <input
                  id="account_size"
                  type="number"
                  className="input"
                  min="1000"
                  value={formData.account_size}
                  onChange={(e) => setFormData({ ...formData, account_size: parseFloat(e.target.value) })}
                  required
                />
              </div>
              <div>
                <label className="input-label" htmlFor="risk_pct">Default Risk %</label>
                <input
                  id="risk_pct"
                  type="number"
                  className="input"
                  min="0.1"
                  max="10"
                  step="0.1"
                  value={formData.default_risk_pct}
                  onChange={(e) => setFormData({ ...formData, default_risk_pct: parseFloat(e.target.value) })}
                  required
                />
              </div>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary w-full mt-4"
              disabled={isLoading}
            >
              {isLoading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-text-secondary">
            Already have an account?{' '}
            <Link href="/login" className="text-accent-primary font-medium hover:underline">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
