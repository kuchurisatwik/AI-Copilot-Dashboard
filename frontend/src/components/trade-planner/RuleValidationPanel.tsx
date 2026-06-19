import React from 'react';

interface RuleResult {
  rule: string;
  status: 'pass' | 'warning' | 'block';
  message: string;
}

interface RuleValidationPanelProps {
  validationData: {
    overall_status: 'pass' | 'warning' | 'block';
    rule_results: RuleResult[];
  } | null;
}

export default function RuleValidationPanel({ validationData }: RuleValidationPanelProps) {
  if (!validationData) {
    return null;
  }

  const { overall_status, rule_results } = validationData;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <svg className="w-5 h-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>;
      case 'warning':
        return <svg className="w-5 h-5 text-color-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>;
      case 'block':
        return <svg className="w-5 h-5 text-color-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>;
      default:
        return null;
    }
  };

  const getPanelClass = () => {
    if (overall_status === 'block') return 'border-color-danger bg-color-danger-subtle/30';
    if (overall_status === 'warning') return 'border-color-warning bg-color-warning-subtle/30';
    return 'border-success bg-success-subtle/10';
  };

  return (
    <div className={`card border ${getPanelClass()} transition-all duration-300`}>
      <h3 className="font-semibold text-base mb-3 flex items-center gap-2">
        {getStatusIcon(overall_status)}
        Rule Engine Validation
      </h3>
      
      <div className="space-y-3">
        {rule_results.map((result, idx) => (
          <div key={idx} className="flex items-start gap-3 p-2 rounded-md bg-bg-primary/50 border border-border-primary">
            <div className="mt-0.5">
              {getStatusIcon(result.status)}
            </div>
            <div>
              <p className={`text-sm font-medium ${
                result.status === 'block' ? 'text-color-danger' :
                result.status === 'warning' ? 'text-color-warning' :
                'text-success'
              }`}>
                {result.rule.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
              </p>
              <p className="text-xs text-text-secondary mt-0.5">{result.message}</p>
            </div>
          </div>
        ))}
      </div>
      
      {overall_status === 'block' && (
        <div className="mt-4 p-3 bg-color-danger-subtle text-color-danger text-sm rounded border border-color-danger/20 flex items-start gap-2">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <p>This trade violates core risk parameters and cannot be executed according to your risk profile.</p>
        </div>
      )}
    </div>
  );
}
