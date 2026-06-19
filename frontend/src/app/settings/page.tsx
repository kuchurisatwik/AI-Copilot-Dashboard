"use client";

import React, { useEffect, useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { strategiesApi } from '@/lib/strategies';
import { riskApi } from '@/lib/risk';
import { useAuthStore } from '@/stores/authStore';

export default function SettingsPage() {
  const user = useAuthStore((state) => state.user);
  const [strategies, setStrategies] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  const [isLoadingRisk, setIsLoadingRisk] = useState(true);
  const [isSavingRisk, setIsSavingRisk] = useState(false);
  const [riskError, setRiskError] = useState('');
  const [riskSuccess, setRiskSuccess] = useState('');
  
  const [riskForm, setRiskForm] = useState({
    account_size: 100000,
    max_risk_per_trade_pct: 1.0,
    max_daily_drawdown_pct: 3.0,
    max_open_trades: 3,
  });

  useEffect(() => {
    const fetchStrategies = async () => {
      try {
        const response = await strategiesApi.getStrategies();
        setStrategies(response.data);
      } catch (err) {
        console.error('Failed to load strategies', err);
      } finally {
        setIsLoading(false);
      }
    };

    const fetchRiskProfile = async () => {
      try {
        const res = await riskApi.getProfile();
        setRiskForm({
          account_size: res.data.account_size,
          max_risk_per_trade_pct: res.data.max_risk_per_trade_pct,
          max_daily_drawdown_pct: res.data.max_daily_drawdown_pct,
          max_open_trades: res.data.max_open_trades,
        });
      } catch (err) {
        console.error('Failed to load risk profile', err);
      } finally {
        setIsLoadingRisk(false);
      }
    };

    fetchStrategies();
    fetchRiskProfile();
  }, []);

  const handleRiskChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setRiskForm(prev => ({
      ...prev,
      [name]: parseFloat(value) || 0
    }));
  };

  const handleRiskSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingRisk(true);
    setRiskError('');
    setRiskSuccess('');

    try {
      await riskApi.updateProfile(riskForm);
      setRiskSuccess('Risk profile updated successfully!');
      setTimeout(() => setRiskSuccess(''), 3000);
    } catch (err: any) {
      setRiskError(err.response?.data?.detail || 'Failed to update risk profile');
    } finally {
      setIsSavingRisk(false);
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="max-w-4xl space-y-8 animate-fade-in">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
            <p className="text-text-secondary mt-1">Manage your account preferences and trading strategies.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Sidebar navigation for settings could go here in a more complex app */}
            <div className="md:col-span-3 space-y-8">
              
              {/* Profile Settings */}
              <section className="card">
                <h2 className="text-lg font-semibold mb-4 border-b border-border-primary pb-2">Profile Information</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="input-label">Name</label>
                    <div className="p-2 bg-bg-primary border border-border-primary rounded-md text-sm">{user?.name}</div>
                  </div>
                  <div>
                    <label className="input-label">Email</label>
                    <div className="p-2 bg-bg-primary border border-border-primary rounded-md text-sm">{user?.email}</div>
                  </div>
                </div>
              </section>

              {/* Risk Engine Limits */}
              <section className="card">
                <h2 className="text-lg font-semibold mb-4 border-b border-border-primary pb-2">Risk Engine Limits</h2>
                {isLoadingRisk ? (
                  <div className="animate-pulse space-y-4">
                    <div className="h-4 bg-bg-surface rounded w-3/4"></div>
                  </div>
                ) : (
                  <form onSubmit={handleRiskSubmit} className="space-y-4">
                    {riskError && (
                      <div className="p-3 text-sm text-color-danger bg-color-danger-subtle border border-color-danger/20 rounded-md">
                        {riskError}
                      </div>
                    )}
                    {riskSuccess && (
                      <div className="p-3 text-sm text-success bg-success/10 border border-success/20 rounded-md">
                        {riskSuccess}
                      </div>
                    )}
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="input-label" htmlFor="account_size">Account Size (₹)</label>
                        <input 
                          type="number" id="account_size" name="account_size"
                          value={riskForm.account_size} onChange={handleRiskChange}
                          className="input-field" step="0.01" min="1" required
                        />
                      </div>
                      <div>
                        <label className="input-label" htmlFor="max_risk_per_trade_pct">Max Risk Per Trade (%)</label>
                        <input 
                          type="number" id="max_risk_per_trade_pct" name="max_risk_per_trade_pct"
                          value={riskForm.max_risk_per_trade_pct} onChange={handleRiskChange}
                          className="input-field" step="0.1" min="0.1" max="100" required
                        />
                      </div>
                      <div>
                        <label className="input-label" htmlFor="max_daily_drawdown_pct">Max Daily Drawdown (%)</label>
                        <input 
                          type="number" id="max_daily_drawdown_pct" name="max_daily_drawdown_pct"
                          value={riskForm.max_daily_drawdown_pct} onChange={handleRiskChange}
                          className="input-field" step="0.1" min="0.1" max="100" required
                        />
                      </div>
                      <div>
                        <label className="input-label" htmlFor="max_open_trades">Max Open Trades</label>
                        <input 
                          type="number" id="max_open_trades" name="max_open_trades"
                          value={riskForm.max_open_trades} onChange={handleRiskChange}
                          className="input-field" step="1" min="1" max="100" required
                        />
                      </div>
                    </div>
                    <div className="flex justify-end">
                      <button type="submit" disabled={isSavingRisk} className="btn btn-primary text-sm py-1.5 px-4">
                        {isSavingRisk ? 'Saving...' : 'Save Limits'}
                      </button>
                    </div>
                  </form>
                )}
              </section>

              {/* Strategies Management */}
              <section className="card">
                <div className="flex items-center justify-between mb-4 border-b border-border-primary pb-2">
                  <h2 className="text-lg font-semibold">Your Strategies</h2>
                  <button className="btn btn-primary text-xs py-1.5 px-3">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
                    New Strategy
                  </button>
                </div>
                
                {isLoading ? (
                  <div className="animate-pulse flex space-x-4">
                    <div className="flex-1 space-y-4 py-1">
                      <div className="h-4 bg-bg-surface rounded w-3/4"></div>
                      <div className="h-4 bg-bg-surface rounded"></div>
                      <div className="h-4 bg-bg-surface rounded w-5/6"></div>
                    </div>
                  </div>
                ) : strategies.length > 0 ? (
                  <div className="grid gap-4">
                    {strategies.map((strategy) => (
                      <div key={strategy.id} className="p-4 border border-border-primary rounded-lg bg-bg-primary flex items-start justify-between group hover:border-border-focus transition-colors">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-medium text-text-primary">{strategy.name}</h3>
                            <span className="badge badge--neutral">{strategy.type}</span>
                            {strategy.is_default && <span className="text-xs text-text-tertiary bg-bg-surface px-1.5 rounded">Default</span>}
                          </div>
                          <p className="text-sm text-text-secondary">{strategy.description}</p>
                        </div>
                        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button className="text-text-tertiary hover:text-accent-primary p-1"><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg></button>
                          {!strategy.is_default && (
                            <button className="text-text-tertiary hover:text-color-danger p-1"><svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg></button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <p>No strategies found. Seed defaults or create your own.</p>
                  </div>
                )}
              </section>

            </div>
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
