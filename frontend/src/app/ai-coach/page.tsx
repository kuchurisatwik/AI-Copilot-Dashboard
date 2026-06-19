"use client";

import React, { useEffect, useState } from "react";
import MainLayout from "@/components/layout/MainLayout";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { aiApi } from "@/lib/ai";

export default function AICoachPage() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await aiApi.getCoachAdvice();
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
        <div className="max-w-4xl mx-auto space-y-6 animate-fade-in pb-12">
          
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-accent-primary to-purple-600 flex items-center justify-center shadow-[0_0_15px_rgba(59,130,246,0.5)]">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">AI Trading Coach</h1>
              <p className="text-text-secondary mt-1">
                Automated insights based on your recent trading performance.
              </p>
            </div>
          </div>

          {isLoading ? (
            <div className="card p-12 text-center text-text-secondary flex flex-col items-center gap-4">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-accent-primary border-t-transparent"></div>
              <p>Analyzing your trading patterns...</p>
            </div>
          ) : !data ? (
            <div className="card p-12 text-center text-text-secondary">
              Failed to load AI Coach insights. Please try again.
            </div>
          ) : (
            <div className="space-y-6">
              
              <div className="card border-accent-primary/30 shadow-[0_0_20px_rgba(59,130,246,0.05)]">
                <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
                  Latest Analysis
                </h2>
                
                <div className="space-y-4">
                  {data.advice && data.advice.length > 0 ? (
                    data.advice.map((point: string, idx: number) => (
                      <div key={idx} className="flex items-start gap-4 p-4 rounded-lg bg-bg-surface border border-border-primary">
                        <div className="mt-1 flex-shrink-0 text-accent-primary">
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                        </div>
                        <p className="text-text-primary leading-relaxed">{point}</p>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 rounded-lg bg-bg-surface border border-border-primary text-text-secondary text-center">
                      Not enough data to generate targeted advice. Keep trading!
                    </div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="card p-4 flex flex-col items-center text-center justify-center">
                  <div className="text-xs text-text-secondary uppercase mb-2">Analyzed Trades</div>
                  <div className="text-2xl font-bold font-mono text-text-primary">{data.metrics.total_trades}</div>
                </div>
                <div className="card p-4 flex flex-col items-center text-center justify-center">
                  <div className="text-xs text-text-secondary uppercase mb-2">Win Rate Base</div>
                  <div className="text-2xl font-bold font-mono text-text-primary">{data.metrics.win_rate.toFixed(1)}%</div>
                </div>
                <div className="card p-4 flex flex-col items-center text-center justify-center">
                  <div className="text-xs text-text-secondary uppercase mb-2">Profit Factor Base</div>
                  <div className="text-2xl font-bold font-mono text-text-primary">{data.metrics.profit_factor.toFixed(2)}</div>
                </div>
              </div>

            </div>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
