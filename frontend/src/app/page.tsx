"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import MainLayout from "@/components/layout/MainLayout";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { useAuthStore } from "@/stores/authStore";
import { analyticsApi } from "@/lib/analytics";
import { tradesApi } from "@/lib/trades";

export default function Dashboard() {
  const { user } = useAuthStore();
  const [metrics, setMetrics] = useState<any>(null);
  const [recentTrades, setRecentTrades] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const [metricsRes, tradesRes] = await Promise.all([
          analyticsApi.getDashboardMetrics(),
          tradesApi.getTrades({ limit: 5 })
        ]);
        setMetrics(metricsRes.data);
        setRecentTrades(tradesRes.data || []);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="max-w-7xl mx-auto space-y-8 animate-fade-in pb-12">
          
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-text-primary">
                Welcome back, {user?.name?.split(' ')[0] || 'Trader'}
              </h1>
              <p className="text-text-secondary mt-1">Here is how your trading is performing.</p>
            </div>
            <Link href="/trade-planner" className="btn btn-primary shadow-glow">
              Plan New Trade
            </Link>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              {[1,2,3,4].map(i => (
                <div key={i} className="card h-28 animate-pulse bg-bg-surface border-border-primary"></div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <div className="card border-border-primary hover:border-accent-primary/50 transition-colors">
                <div className="text-sm text-text-secondary uppercase mb-1">Total PnL</div>
                <div className={`text-2xl font-bold font-mono ${metrics?.total_pnl >= 0 ? 'text-success' : 'text-color-danger'}`}>
                  {metrics?.total_pnl > 0 ? '+' : ''}{metrics?.total_pnl?.toLocaleString(undefined, {style: 'currency', currency: 'INR'}) || '₹0'}
                </div>
              </div>
              <div className="card border-border-primary hover:border-accent-primary/50 transition-colors">
                <div className="text-sm text-text-secondary uppercase mb-1">Win Rate</div>
                <div className="text-2xl font-bold font-mono text-text-primary">
                  {metrics?.win_rate?.toFixed(1) || '0.0'}%
                </div>
                <div className="text-xs text-text-tertiary mt-1">
                  Recent (last 10): <span className={metrics?.recent_win_rate >= metrics?.win_rate ? 'text-success' : 'text-color-warning'}>{metrics?.recent_win_rate?.toFixed(1) || '0.0'}%</span>
                </div>
              </div>
              <div className="card border-border-primary hover:border-accent-primary/50 transition-colors">
                <div className="text-sm text-text-secondary uppercase mb-1">Profit Factor</div>
                <div className="text-2xl font-bold font-mono text-text-primary">
                  {metrics?.profit_factor?.toFixed(2) || '0.00'}
                </div>
              </div>
              <div className="card border-border-primary hover:border-accent-primary/50 transition-colors">
                <div className="text-sm text-text-secondary uppercase mb-1">Avg R-Multiple</div>
                <div className={`text-2xl font-bold font-mono ${metrics?.avg_r_multiple >= 1 ? 'text-success' : 'text-color-warning'}`}>
                  {metrics?.avg_r_multiple?.toFixed(2) || '0.00'}R
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <div className="card h-96 flex flex-col items-center justify-center border-border-primary">
                <svg className="w-16 h-16 text-text-tertiary mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" /></svg>
                <h3 className="text-text-secondary font-medium">Equity Curve Chart</h3>
                <p className="text-sm text-text-tertiary mt-1">Complete more trades to generate an equity curve</p>
              </div>
            </div>
            
            <div className="space-y-6">
              <div className="card">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-semibold">Recent Trades</h3>
                  <Link href="/journal" className="text-xs text-accent-primary hover:text-accent-primary/80">View All</Link>
                </div>
                
                <div className="space-y-3">
                  {recentTrades.length === 0 ? (
                    <p className="text-sm text-text-tertiary italic text-center py-4">No trades found.</p>
                  ) : (
                    recentTrades.map(trade => (
                      <Link key={trade.id} href={`/journal/${trade.id}`} className="block p-3 rounded-md bg-bg-surface border border-border-primary hover:border-accent-primary/30 transition-colors">
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-bold font-mono text-sm">{trade.symbol}</span>
                          <span className={`text-xs font-bold uppercase ${trade.pnl > 0 ? 'text-success' : trade.pnl < 0 ? 'text-color-danger' : 'text-text-tertiary'}`}>
                            {trade.result || trade.status}
                          </span>
                        </div>
                        <div className="flex justify-between items-center text-xs text-text-secondary">
                          <span>{trade.direction.toUpperCase()} • {trade.r_multiple ? `${trade.r_multiple}R` : '-'}</span>
                          <span>{new Date(trade.created_at).toLocaleDateString()}</span>
                        </div>
                      </Link>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
          
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
