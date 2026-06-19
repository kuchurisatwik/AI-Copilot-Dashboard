"use client";

import React, { useEffect, useState } from "react";
import MainLayout from "@/components/layout/MainLayout";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { analyticsApi } from "@/lib/analytics";

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await analyticsApi.getAllTimeAnalytics();
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="max-w-6xl mx-auto space-y-6 animate-fade-in pb-12">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Performance Analytics</h1>
            <p className="text-text-secondary mt-1">Deep dive into your trading statistics.</p>
          </div>

          {isLoading ? (
            <div className="p-12 text-center text-text-secondary">Loading analytics...</div>
          ) : !data ? (
            <div className="p-12 text-center text-text-secondary card">Not enough data to display analytics.</div>
          ) : (
            <div className="space-y-6">
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="text-xs text-text-secondary uppercase mb-1">Total Trades</div>
                  <div className="text-xl font-bold font-mono">{data.total_trades}</div>
                </div>
                <div className="card">
                  <div className="text-xs text-text-secondary uppercase mb-1">Wins / Losses</div>
                  <div className="text-xl font-bold font-mono"><span className="text-success">{data.winning_trades}</span> / <span className="text-color-danger">{data.losing_trades}</span></div>
                </div>
                <div className="card">
                  <div className="text-xs text-text-secondary uppercase mb-1">Win Rate</div>
                  <div className="text-xl font-bold font-mono">{data.win_rate?.toFixed(2)}%</div>
                </div>
                <div className="card">
                  <div className="text-xs text-text-secondary uppercase mb-1">Expectancy</div>
                  <div className="text-xl font-bold font-mono text-success">
                    {/* Simplified expectancy = (WinRate * AvgWin) - (LossRate * AvgLoss), but we can just use R-multiple */}
                    {data.avg_r_multiple?.toFixed(2)}R per trade
                  </div>
                </div>
              </div>
              
              <div className="card">
                <h3 className="font-semibold mb-4">Strategy Performance</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs text-text-secondary uppercase bg-bg-surface border-b border-border-primary">
                      <tr>
                        <th className="px-4 py-3 font-medium">Strategy ID</th>
                        <th className="px-4 py-3 font-medium text-right">Trades</th>
                        <th className="px-4 py-3 font-medium text-right">Wins</th>
                        <th className="px-4 py-3 font-medium text-right">Win Rate</th>
                        <th className="px-4 py-3 font-medium text-right">PnL</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border-primary">
                      {Object.entries(data.strategy_breakdown || {}).map(([id, stats]: [string, any]) => (
                        <tr key={id}>
                          <td className="px-4 py-3 font-mono text-xs">{id}</td>
                          <td className="px-4 py-3 text-right font-mono">{stats.count}</td>
                          <td className="px-4 py-3 text-right font-mono">{stats.wins}</td>
                          <td className="px-4 py-3 text-right font-mono">{((stats.wins / stats.count) * 100).toFixed(1)}%</td>
                          <td className="px-4 py-3 text-right font-mono text-success">{stats.pnl}</td>
                        </tr>
                      ))}
                      {Object.keys(data.strategy_breakdown || {}).length === 0 && (
                        <tr><td colSpan={5} className="px-4 py-8 text-center text-text-tertiary">No strategy data yet</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

            </div>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
