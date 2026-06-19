"use client";

import React, { useEffect, useState, useCallback } from 'react';
import { tradesApi } from '@/lib/trades';

interface RiskCalculatorProps {
  symbol: string;
  entryPrice: number;
  stopLoss: number;
  takeProfit: number;
  direction: 'long' | 'short';
  onValidationChange?: (isValid: boolean) => void;
}

export default function RiskCalculator({ 
  symbol, entryPrice, stopLoss, takeProfit, direction, onValidationChange 
}: RiskCalculatorProps) {
  const [riskData, setRiskData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const calculateRisk = useCallback(async () => {
    if (!symbol || entryPrice <= 0 || stopLoss <= 0 || takeProfit <= 0) {
      setRiskData(null);
      if (onValidationChange) onValidationChange(false);
      return;
    }

    // Basic logic check
    if (direction === 'long' && (stopLoss >= entryPrice || takeProfit <= entryPrice)) {
      setError('For Long: Stop Loss < Entry < Take Profit');
      setRiskData(null);
      if (onValidationChange) onValidationChange(false);
      return;
    }
    
    if (direction === 'short' && (stopLoss <= entryPrice || takeProfit >= entryPrice)) {
      setError('For Short: Take Profit < Entry < Stop Loss');
      setRiskData(null);
      if (onValidationChange) onValidationChange(false);
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      const response = await tradesApi.calculateRisk({
        symbol,
        entry_price: entryPrice,
        stop_loss: stopLoss,
        take_profit: takeProfit,
        direction
      });
      setRiskData(response.data);
      if (onValidationChange) onValidationChange(true);
    } catch (err) {
      console.error('Error calculating risk', err);
      setError('Failed to calculate risk metrics');
      if (onValidationChange) onValidationChange(false);
    } finally {
      setIsLoading(false);
    }
  }, [symbol, entryPrice, stopLoss, takeProfit, direction, onValidationChange]);

  // Debounce calculations when inputs change
  useEffect(() => {
    const timer = setTimeout(() => {
      calculateRisk();
    }, 500);
    return () => clearTimeout(timer);
  }, [calculateRisk]);

  if (error) {
    return (
      <div className="p-3 text-sm text-color-danger bg-color-danger-subtle border border-color-danger/20 rounded-md">
        {error}
      </div>
    );
  }

  if (isLoading && !riskData) {
    return (
      <div className="card border border-border-primary animate-pulse h-40">
        <div className="h-4 bg-bg-surface rounded w-1/3 mb-4"></div>
        <div className="grid grid-cols-2 gap-4">
          <div className="h-8 bg-bg-surface rounded"></div>
          <div className="h-8 bg-bg-surface rounded"></div>
        </div>
      </div>
    );
  }

  if (!riskData) {
    return (
      <div className="card border border-border-primary text-center text-text-tertiary p-8">
        Enter trade parameters to calculate risk
      </div>
    );
  }

  return (
    <div className="card-elevated border border-border-focus/50 shadow-glow relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent-primary via-success to-accent-primary"></div>
      
      <h3 className="font-semibold text-lg mb-4 flex items-center justify-between">
        <span>Risk Metrics</span>
        <span className="badge badge--success">Validated</span>
      </h3>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="p-3 bg-bg-primary rounded-lg border border-border-primary text-center">
          <div className="text-xs text-text-secondary uppercase tracking-wider mb-1">Position Size</div>
          <div className="text-xl font-bold font-mono text-text-primary">
            {riskData.position_size.toLocaleString(undefined, { maximumFractionDigits: 4 })}
          </div>
        </div>
        
        <div className="p-3 bg-bg-primary rounded-lg border border-border-primary text-center">
          <div className="text-xs text-text-secondary uppercase tracking-wider mb-1">Reward/Risk</div>
          <div className={`text-xl font-bold font-mono ${riskData.reward_risk_ratio >= 2 ? 'text-success' : 'text-color-warning'}`}>
            {riskData.reward_risk_ratio.toFixed(2)}R
          </div>
        </div>
      </div>
      
      <div className="space-y-3 text-sm mb-4">
        <div className="flex justify-between items-center border-b border-border-secondary pb-2">
          <span className="text-text-secondary">Capital Exposure</span>
          <span className="font-medium">{riskData.capital_exposure_pct.toFixed(2)}%</span>
        </div>
        <div className="flex justify-between items-center border-b border-border-secondary pb-2">
          <span className="text-text-secondary">Max Loss Amount</span>
          <span className="font-medium text-color-danger">-₹{riskData.max_loss.toLocaleString()}</span>
        </div>
        <div className="flex justify-between items-center border-b border-border-secondary pb-2">
          <span className="text-text-secondary">Potential Profit</span>
          <span className="font-medium text-success">+₹{riskData.potential_profit.toLocaleString()}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-text-secondary">Risk % of Account</span>
          <span className="font-medium">{riskData.risk_pct.toFixed(2)}%</span>
        </div>
      </div>
      
      {riskData.warnings && riskData.warnings.length > 0 && (
        <div className="mt-4 p-3 bg-color-warning-subtle border border-color-warning/30 rounded-md">
          <div className="flex items-start">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-color-warning mt-0.5 mr-2 flex-shrink-0"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <div>
              <h4 className="text-sm font-semibold text-color-warning mb-1">Risk Limits Exceeded</h4>
              <ul className="text-xs text-text-secondary space-y-1 list-disc list-inside">
                {riskData.warnings.map((w: string, i: number) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
