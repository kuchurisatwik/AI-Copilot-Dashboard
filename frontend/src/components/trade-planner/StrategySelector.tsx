"use client";

import React, { useEffect, useState } from 'react';
import { strategiesApi } from '@/lib/strategies';

interface Strategy {
  id: string;
  name: string;
  type: string;
  description: string;
  risk_appetite: number;
}

interface StrategySelectorProps {
  onSelect: (strategy: Strategy | null) => void;
  selectedId?: string;
}

export default function StrategySelector({ onSelect, selectedId }: StrategySelectorProps) {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStrategies = async () => {
      try {
        const response = await strategiesApi.getStrategies();
        setStrategies(response.data);
        
        // Auto-select if selectedId is provided and exists in the list
        if (selectedId && response.data) {
          const selected = response.data.find((s: Strategy) => s.id === selectedId);
          if (selected) {
            onSelect(selected);
          }
        } else if (response.data.length > 0 && !selectedId) {
          // Auto-select the first one if nothing is selected
          onSelect(response.data[0]);
        }
      } catch (err: any) {
        setError('Failed to load strategies');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStrategies();
  }, [selectedId]);

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-2">
        <div className="h-4 bg-bg-surface rounded w-1/4"></div>
        <div className="h-10 bg-bg-surface rounded w-full"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3 text-sm text-color-danger bg-color-danger-subtle border border-color-danger/20 rounded-md">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-1.5">
      <label className="input-label" htmlFor="strategy-select">Trading Strategy</label>
      <select
        id="strategy-select"
        className="input"
        value={selectedId || ''}
        onChange={(e) => {
          const selected = strategies.find(s => s.id === e.target.value) || null;
          onSelect(selected);
        }}
      >
        <option value="" disabled>Select a strategy</option>
        {strategies.map((strategy) => (
          <option key={strategy.id} value={strategy.id}>
            {strategy.name} ({strategy.type})
          </option>
        ))}
      </select>
      
      {/* Show description of selected strategy */}
      {selectedId && strategies.find(s => s.id === selectedId)?.description && (
        <p className="text-xs text-text-tertiary mt-2">
          {strategies.find(s => s.id === selectedId)?.description}
        </p>
      )}
    </div>
  );
}
