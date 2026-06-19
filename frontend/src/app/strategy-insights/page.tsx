"use client";

import React, { useEffect, useState } from "react";
import MainLayout from "@/components/layout/MainLayout";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { analyticsApi } from "@/lib/analytics";
import { strategiesApi } from "@/lib/strategies";

export default function StrategyInsightsPage() {
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [strategies, setStrategies] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsRes, strategiesRes] = await Promise.all([
          analyticsApi.getAllTimeAnalytics(),
          strategiesApi.getStrategies()
        ]);
        setAnalyticsData(analyticsRes.data);
        setStrategies(strategiesRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const getStrategyName = (id: string) => {
    const s = strategies.find(strat => strat.id === id);
    return s ? s.name : "Unknown Strategy";
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="max-w-6xl mx-auto space-y-6 animate-fade-in pb-12">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Strategy Insights</h1>
            <p className="text-text-secondary mt-1">
              Compare your performance across different trading strategies.
            </p>
          </div>

          {isLoading ? (
            <div className="p-12 text-center text-text-secondary">Loading insights...</div>
          ) : !analyticsData || !analyticsData.strategy_breakdown || Object.keys(analyticsData.strategy_breakdown).length === 0 ? (
            <div className="p-12 text-center text-text-secondary card">
              No strategy data available. Execute more trades to generate insights.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(analyticsData.strategy_breakdown).map(([id, stats]: [string, any]) => {
                const winRate = stats.count > 0 ? ((stats.wins / stats.count) * 100).toFixed(1) : 0;
                return (
                  <div key={id} className="card hover:border-accent-primary/50 transition-colors">
                    <h3 className="text-lg font-semibold mb-4 text-accent-primary">
                      {getStrategyName(id)}
                    </h3>
                    
                    <div className="space-y-4">
                      <div className="flex justify-between items-center border-b border-border-secondary pb-2">
                        <span className="text-sm text-text-secondary">Total Trades</span>
                        <span className="font-mono font-medium">{stats.count}</span>
                      </div>
                      
                      <div className="flex justify-between items-center border-b border-border-secondary pb-2">
                        <span className="text-sm text-text-secondary">Win Rate</span>
                        <span className={`font-mono font-medium ${parseFloat(winRate as string) >= 50 ? 'text-success' : 'text-color-danger'}`}>
                          {winRate}%
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center border-b border-border-secondary pb-2">
                        <span className="text-sm text-text-secondary">Total PnL</span>
                        <span className={`font-mono font-medium ${stats.pnl > 0 ? 'text-success' : 'text-color-danger'}`}>
                          {stats.pnl > 0 ? '+' : ''}{stats.pnl}
                        </span>
                      </div>
                      
                      <div className="pt-2">
                        <div className="w-full bg-bg-primary rounded-full h-2 mt-2 overflow-hidden flex">
                          <div 
                            className="bg-success h-full" 
                            style={{ width: `${winRate}%` }}
                          ></div>
                          <div 
                            className="bg-color-danger h-full" 
                            style={{ width: `${100 - parseFloat(winRate as string)}%` }}
                          ></div>
                        </div>
                        <div className="flex justify-between mt-1 text-xs text-text-tertiary">
                          <span>{stats.wins} Wins</span>
                          <span>{stats.count - stats.wins} Losses</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
