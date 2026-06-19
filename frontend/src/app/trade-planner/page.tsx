"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import StrategySelector from '@/components/trade-planner/StrategySelector';
import RiskCalculator from '@/components/trade-planner/RiskCalculator';
import RuleValidationPanel from '@/components/trade-planner/RuleValidationPanel';
import { tradesApi } from '@/lib/trades';

export default function TradePlannerPage() {
  const router = useRouter();
  const [selectedStrategyId, setSelectedStrategyId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    symbol: 'NIFTY',
    direction: 'long' as 'long' | 'short',
    orderType: 'limit',
    entryPrice: 0,
    stopLoss: 0,
    takeProfit: 0,
    thesis: ''
  });
  
  const [isRiskValid, setIsRiskValid] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tradeResult, setTradeResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    // Convert to number for price fields
    if (['entryPrice', 'stopLoss', 'takeProfit'].includes(name)) {
      setFormData(prev => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    // Reset result if inputs change
    if (tradeResult) setTradeResult(null);
  };

  const handlePlanTrade = async () => {
    if (!selectedStrategyId) {
      setError('Please select a trading strategy');
      return;
    }
    
    if (!isRiskValid) {
      setError('Please fix risk parameters before planning');
      return;
    }

    setError('');
    setIsSubmitting(true);

    try {
      const response = await tradesApi.planTrade({
        strategy_id: selectedStrategyId,
        symbol: formData.symbol,
        direction: formData.direction,
        order_type: formData.orderType,
        entry_price: formData.entryPrice,
        stop_loss: formData.stopLoss,
        take_profit: formData.takeProfit,
        thesis: formData.thesis
      });
      
      setTradeResult(response.data);
      
      // If validation passed, optionally redirect or show success
      if (response.data.rule_validation.overall_status !== 'block') {
        // router.push('/journal');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to plan trade');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in pb-12">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Trade Planner</h1>
            <p className="text-text-secondary mt-1">
              Plan your next trade. The AI Risk Engine will validate parameters before execution.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Left Column: Inputs */}
            <div className="lg:col-span-7 space-y-6">
              
              {/* Strategy & Basic Info */}
              <div className="card">
                <h2 className="text-lg font-semibold mb-4 border-b border-border-primary pb-2">1. Strategy & Setup</h2>
                <div className="space-y-4">
                  <StrategySelector 
                    selectedId={selectedStrategyId || undefined} 
                    onSelect={(s) => setSelectedStrategyId(s?.id || null)} 
                  />
                  
                  <div className="grid grid-cols-2 gap-4 pt-2">
                    <div>
                      <label className="input-label" htmlFor="symbol">Symbol</label>
                      <input
                        id="symbol"
                        name="symbol"
                        type="text"
                        className="input font-mono uppercase"
                        value={formData.symbol}
                        onChange={handleInputChange}
                        placeholder="NIFTY, RELIANCE..."
                      />
                    </div>
                    <div>
                      <label className="input-label" htmlFor="direction">Direction</label>
                      <select
                        id="direction"
                        name="direction"
                        className="input"
                        value={formData.direction}
                        onChange={handleInputChange}
                      >
                        <option value="long">Long (Buy)</option>
                        <option value="short">Short (Sell)</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Price Levels */}
              <div className="card">
                <h2 className="text-lg font-semibold mb-4 border-b border-border-primary pb-2">2. Price Levels</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="input-label" htmlFor="entryPrice">Entry Price</label>
                    <input
                      id="entryPrice"
                      name="entryPrice"
                      type="number"
                      step="0.05"
                      className="input font-mono"
                      value={formData.entryPrice || ''}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div>
                    <label className="input-label" htmlFor="stopLoss">Stop Loss</label>
                    <input
                      id="stopLoss"
                      name="stopLoss"
                      type="number"
                      step="0.05"
                      className="input font-mono text-color-danger"
                      value={formData.stopLoss || ''}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div>
                    <label className="input-label" htmlFor="takeProfit">Take Profit</label>
                    <input
                      id="takeProfit"
                      name="takeProfit"
                      type="number"
                      step="0.05"
                      className="input font-mono text-success"
                      value={formData.takeProfit || ''}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </div>
              
              {/* Thesis */}
              <div className="card">
                <h2 className="text-lg font-semibold mb-4 border-b border-border-primary pb-2">3. Trade Thesis</h2>
                <div>
                  <label className="input-label" htmlFor="thesis">Why are you taking this trade?</label>
                  <textarea
                    id="thesis"
                    name="thesis"
                    rows={4}
                    className="input resize-none"
                    placeholder="E.g., Price rejected from major daily support with bullish divergence on RSI..."
                    value={formData.thesis}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

            </div>

            {/* Right Column: Engine Feedback */}
            <div className="lg:col-span-5 space-y-6">
              
              {/* Interactive Risk Calculator */}
              <RiskCalculator
                symbol={formData.symbol}
                entryPrice={formData.entryPrice}
                stopLoss={formData.stopLoss}
                takeProfit={formData.takeProfit}
                direction={formData.direction}
                onValidationChange={setIsRiskValid}
              />

              {/* Server Validation Results (Appears after Planning) */}
              {tradeResult && tradeResult.rule_validation && (
                <div className="animate-fade-in-up">
                  <RuleValidationPanel validationData={tradeResult.rule_validation} />
                </div>
              )}

              {/* Action Buttons */}
              <div className="pt-4">
                {error && (
                  <div className="mb-4 p-3 text-sm text-color-danger bg-color-danger-subtle border border-color-danger/20 rounded-md">
                    {error}
                  </div>
                )}
                
                <button
                  className="btn btn-primary w-full text-lg py-3 shadow-glow"
                  onClick={handlePlanTrade}
                  disabled={!isRiskValid || isSubmitting || !selectedStrategyId}
                >
                  {isSubmitting ? 'Evaluating...' : 'Plan Trade & Validate'}
                </button>
                
                {tradeResult && tradeResult.rule_validation.overall_status !== 'block' && (
                  <button
                    className="btn bg-success hover:bg-success/90 text-white w-full text-lg py-3 mt-4 shadow-[0_0_15px_rgba(34,197,94,0.3)] transition-all flex items-center justify-center"
                    onClick={async () => {
                      try {
                        setIsSubmitting(true);
                        await tradesApi.openTrade(tradeResult.trade.id);
                        router.push('/journal');
                      } catch (err: any) {
                        setError(err.response?.data?.detail || 'Failed to execute trade');
                        setIsSubmitting(false);
                      }
                    }}
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent mr-2"></div>
                    ) : null}
                    {isSubmitting ? 'Executing...' : 'Execute Trade'}
                  </button>
                )}
              </div>

            </div>
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
