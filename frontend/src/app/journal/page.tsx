"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import MainLayout from '@/components/layout/MainLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { tradesApi } from '@/lib/trades';

export default function JournalPage() {
  const [trades, setTrades] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: '',
    result: '',
    symbol: ''
  });

  const fetchTrades = async () => {
    setIsLoading(true);
    try {
      const activeFilters = Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== '')
      );
      const response = await tradesApi.getTrades(activeFilters);
      setTrades(response.data || []);
    } catch (err) {
      console.error('Failed to load trades', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTrades();
  }, [filters]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'open': return <span className="badge border-accent-primary text-accent-primary">Open</span>;
      case 'closed': return <span className="badge badge--success">Closed</span>;
      case 'draft': return <span className="badge border-border-primary text-text-secondary">Draft</span>;
      case 'validated': return <span className="badge border-color-warning text-color-warning">Validated</span>;
      case 'blocked': return <span className="badge badge--danger">Blocked</span>;
      default: return <span className="badge">{status}</span>;
    }
  };

  const getResultBadge = (result: string) => {
    if (!result) return null;
    switch(result) {
      case 'win': return <span className="text-success font-semibold">Win</span>;
      case 'loss': return <span className="text-color-danger font-semibold">Loss</span>;
      case 'breakeven': return <span className="text-text-secondary font-semibold">BE</span>;
      default: return null;
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="max-w-7xl mx-auto space-y-6 animate-fade-in pb-12">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Trading Journal</h1>
              <p className="text-text-secondary mt-1">Review your past trades and log your notes.</p>
            </div>
            <Link href="/trade-planner" className="btn btn-primary">
              Plan New Trade
            </Link>
          </div>

          {/* Filters */}
          <div className="card flex gap-4 items-end flex-wrap">
            <div>
              <label className="input-label text-xs">Symbol</label>
              <input 
                name="symbol" 
                value={filters.symbol} 
                onChange={handleFilterChange} 
                className="input py-1.5 px-3 h-auto" 
                placeholder="Search symbol..." 
              />
            </div>
            <div>
              <label className="input-label text-xs">Status</label>
              <select name="status" value={filters.status} onChange={handleFilterChange} className="input py-1.5 px-3 h-auto">
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="closed">Closed</option>
                <option value="validated">Validated</option>
                <option value="draft">Draft</option>
              </select>
            </div>
            <div>
              <label className="input-label text-xs">Result</label>
              <select name="result" value={filters.result} onChange={handleFilterChange} className="input py-1.5 px-3 h-auto">
                <option value="">All Results</option>
                <option value="win">Win</option>
                <option value="loss">Loss</option>
                <option value="breakeven">Breakeven</option>
              </select>
            </div>
            <button className="btn btn-secondary py-1.5 px-3 h-auto" onClick={() => setFilters({status: '', result: '', symbol: ''})}>
              Clear
            </button>
          </div>

          {/* Trades Table */}
          <div className="card p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-text-secondary uppercase bg-bg-surface border-b border-border-primary">
                  <tr>
                    <th className="px-6 py-4 font-medium">Date</th>
                    <th className="px-6 py-4 font-medium">Symbol</th>
                    <th className="px-6 py-4 font-medium">Type</th>
                    <th className="px-6 py-4 font-medium">Entry</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium text-right">PnL</th>
                    <th className="px-6 py-4 font-medium">R-Mult</th>
                    <th className="px-6 py-4 font-medium text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-primary">
                  {isLoading ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-12 text-center text-text-secondary">Loading trades...</td>
                    </tr>
                  ) : trades.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-12 text-center text-text-secondary">No trades found.</td>
                    </tr>
                  ) : (
                    trades.map((trade) => (
                      <tr key={trade.id} className="hover:bg-bg-surface/50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          {new Date(trade.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 font-medium">{trade.symbol}</td>
                        <td className="px-6 py-4">
                          <span className={`uppercase text-xs font-bold ${trade.direction === 'long' ? 'text-success' : 'text-color-danger'}`}>
                            {trade.direction}
                          </span>
                        </td>
                        <td className="px-6 py-4 font-mono">{trade.entry_price}</td>
                        <td className="px-6 py-4">{getStatusBadge(trade.status)}</td>
                        <td className="px-6 py-4 text-right font-mono">
                          {trade.pnl !== null ? (
                            <span className={trade.pnl > 0 ? 'text-success' : trade.pnl < 0 ? 'text-color-danger' : ''}>
                              {trade.pnl > 0 ? '+' : ''}{trade.pnl}
                            </span>
                          ) : '-'}
                        </td>
                        <td className="px-6 py-4 font-mono">
                          {trade.r_multiple !== null ? `${trade.r_multiple}R` : '-'}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <Link href={`/journal/${trade.id}`} className="text-accent-primary hover:text-accent-primary/80 font-medium">
                            Review
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
          
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
