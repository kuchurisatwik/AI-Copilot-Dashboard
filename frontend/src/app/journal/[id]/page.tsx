"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import MainLayout from '@/components/layout/MainLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { tradesApi } from '@/lib/trades';

export default function TradeReviewPage() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [notes, setNotes] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  const [newNote, setNewNote] = useState('');
  const [closePrice, setClosePrice] = useState('');
  
  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [tradeRes, notesRes] = await Promise.all([
        tradesApi.getTrade(id as string),
        tradesApi.getTradeNotes(id as string)
      ]);
      setData(tradeRes.data);
      setNotes(notesRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      fetchData();
    }
  }, [id]);

  const handleOpenTrade = async () => {
    try {
      await tradesApi.openTrade(id as string);
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Failed to open trade');
    }
  };

  const handleCloseTrade = async () => {
    if (!closePrice) return alert('Enter closing price');
    try {
      await tradesApi.closeTrade(id as string, { exit_price: parseFloat(closePrice) });
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Failed to close trade');
    }
  };

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    try {
      await tradesApi.addTradeNote(id as string, { content: newNote, note_type: 'during_trade' });
      setNewNote('');
      const notesRes = await tradesApi.getTradeNotes(id as string);
      setNotes(notesRes.data);
    } catch (err) {
      console.error(err);
      alert('Failed to add note');
    }
  };

  if (isLoading) {
    return <MainLayout><div className="p-8 text-center text-text-secondary">Loading trade...</div></MainLayout>;
  }

  if (!data) {
    return <MainLayout><div className="p-8 text-center text-color-danger">Trade not found.</div></MainLayout>;
  }

  const { trade, risk_calculation, rule_validation } = data;

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in pb-12">
          
          {/* Header */}
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Link href="/journal" className="p-2 rounded-md hover:bg-bg-surface transition-colors text-text-secondary">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
              </Link>
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-3">
                  {trade.symbol} 
                  <span className={`text-sm px-2 py-0.5 rounded ${trade.direction === 'long' ? 'bg-success-subtle text-success' : 'bg-color-danger-subtle text-color-danger'} uppercase tracking-wider`}>
                    {trade.direction}
                  </span>
                </h1>
                <p className="text-text-secondary text-sm">
                  Created {new Date(trade.created_at).toLocaleString()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <span className="badge px-3 py-1 text-sm bg-bg-surface border-border-focus uppercase">
                {trade.status}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Left Col */}
            <div className="md:col-span-2 space-y-6">
              
              <div className="card">
                <h2 className="text-lg font-semibold border-b border-border-primary pb-3 mb-4">Trade Details</h2>
                <div className="grid grid-cols-3 gap-6 mb-6">
                  <div>
                    <div className="text-xs text-text-secondary uppercase mb-1">Entry</div>
                    <div className="font-mono text-lg">{trade.entry_price}</div>
                  </div>
                  <div>
                    <div className="text-xs text-text-secondary uppercase mb-1">Stop Loss</div>
                    <div className="font-mono text-lg text-color-danger">{trade.stop_loss}</div>
                  </div>
                  <div>
                    <div className="text-xs text-text-secondary uppercase mb-1">Take Profit</div>
                    <div className="font-mono text-lg text-success">{trade.take_profit}</div>
                  </div>
                </div>
                
                {trade.thesis && (
                  <div className="p-4 bg-bg-primary rounded border border-border-primary">
                    <div className="text-xs text-text-secondary uppercase mb-2">Thesis</div>
                    <p className="text-sm whitespace-pre-wrap">{trade.thesis}</p>
                  </div>
                )}
              </div>
              
              {/* Journal Notes */}
              <div className="card">
                <h2 className="text-lg font-semibold border-b border-border-primary pb-3 mb-4">Journal Notes</h2>
                
                <div className="space-y-4 mb-4 max-h-[300px] overflow-y-auto pr-2">
                  {notes.length === 0 ? (
                    <p className="text-sm text-text-tertiary italic">No notes yet.</p>
                  ) : (
                    notes.map(note => (
                      <div key={note.id} className="p-3 bg-bg-surface rounded-md border border-border-primary">
                        <p className="text-sm">{note.content}</p>
                        <div className="text-xs text-text-tertiary mt-2 text-right">
                          {new Date(note.created_at).toLocaleString()}
                        </div>
                      </div>
                    ))
                  )}
                </div>
                
                <div className="flex gap-2">
                  <input 
                    className="input flex-1" 
                    placeholder="Add a new note..." 
                    value={newNote}
                    onChange={e => setNewNote(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleAddNote()}
                  />
                  <button className="btn btn-secondary" onClick={handleAddNote}>Add</button>
                </div>
              </div>

            </div>
            
            {/* Right Col */}
            <div className="space-y-6">
              
              {/* Execution Actions */}
              <div className="card border-accent-primary/50 shadow-glow relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-accent-primary"></div>
                <h2 className="text-lg font-semibold mb-4">Execution</h2>
                
                {trade.status === 'validated' && (
                  <div className="space-y-4">
                    <p className="text-sm text-text-secondary">This trade is planned and validated. Execute it in your broker, then mark it open here.</p>
                    <button className="btn btn-primary w-full shadow-glow" onClick={handleOpenTrade}>
                      Mark as Open
                    </button>
                  </div>
                )}
                
                {trade.status === 'open' && (
                  <div className="space-y-4">
                    <p className="text-sm text-text-secondary">Trade is currently active.</p>
                    <div>
                      <label className="input-label text-xs">Exit Price</label>
                      <input 
                        type="number" 
                        step="0.05"
                        className="input font-mono mb-3" 
                        value={closePrice}
                        onChange={e => setClosePrice(e.target.value)}
                        placeholder="Price closed at..."
                      />
                    </div>
                    <button className="btn bg-color-warning text-white hover:bg-color-warning/90 w-full" onClick={handleCloseTrade}>
                      Close Trade
                    </button>
                  </div>
                )}
                
                {trade.status === 'closed' && (
                  <div className="space-y-3">
                    <div className="flex justify-between items-center py-2 border-b border-border-secondary">
                      <span className="text-text-secondary text-sm">Exit Price</span>
                      <span className="font-mono font-medium">{trade.exit_price}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-border-secondary">
                      <span className="text-text-secondary text-sm">PnL</span>
                      <span className={`font-mono font-bold ${trade.pnl > 0 ? 'text-success' : 'text-color-danger'}`}>
                        {trade.pnl > 0 ? '+' : ''}{trade.pnl}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-text-secondary text-sm">R-Multiple</span>
                      <span className={`font-mono font-bold ${trade.r_multiple >= 1 ? 'text-success' : 'text-color-danger'}`}>
                        {trade.r_multiple}R
                      </span>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Risk Summary */}
              {risk_calculation && (
                <div className="card">
                  <h2 className="text-sm font-semibold text-text-secondary uppercase mb-3">Risk Snapshot</h2>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between py-1 border-b border-border-secondary">
                      <span className="text-text-tertiary">Position Size</span>
                      <span className="font-mono">{risk_calculation.position_size}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-border-secondary">
                      <span className="text-text-tertiary">Risk Amount</span>
                      <span className="font-mono text-color-danger">-{risk_calculation.risk_amount}</span>
                    </div>
                    <div className="flex justify-between py-1">
                      <span className="text-text-tertiary">R/R</span>
                      <span className="font-mono text-success">{risk_calculation.reward_risk_ratio}R</span>
                    </div>
                  </div>
                </div>
              )}

            </div>
            
          </div>
          
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
