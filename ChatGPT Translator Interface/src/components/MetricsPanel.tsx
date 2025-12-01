import { Activity, Target, Zap, Brain, TrendingUp } from 'lucide-react';
import { Metrics, Mode, Theme } from '../App';

interface MetricsPanelProps {
  metrics: Metrics;
  theme: Theme;
  mode: Mode;
}

export function MetricsPanel({ metrics, theme, mode }: MetricsPanelProps) {
  const metricItems = [
    {
      label: 'WER',
      value: metrics.wer !== undefined ? `${(metrics.wer * 100).toFixed(2)}%` : 'N/A',
      icon: Activity,
      show: true,
    },
    {
      label: 'CER',
      value: metrics.cer !== undefined ? `${(metrics.cer * 100).toFixed(2)}%` : 'N/A',
      icon: Target,
      show: true,
    },
    {
      label: 'BLEU',
      value: metrics.bleuScore !== undefined ? metrics.bleuScore.toFixed(3) : 'N/A',
      icon: TrendingUp,
      show: mode === 'translate',
    },
    {
      label: 'Perplexity',
      value: metrics.perplexity !== undefined ? metrics.perplexity.toFixed(2) : 'N/A',
      icon: Brain,
      show: true,
    },
    {
      label: 'Accuracy',
      value: metrics.accuracy !== undefined ? `${(metrics.accuracy * 100).toFixed(1)}%` : 'N/A',
      icon: Zap,
      show: true,
    },
  ];

  const visibleMetrics = metricItems.filter(item => item.show);

  return (
    <div className="bg-gradient-to-b from-transparent to-white/50 dark:to-[#0A0A0A]/50">
      <div className="max-w-3xl mx-auto px-6 py-3">
        <div className="flex items-center justify-between">
          <span className={`text-xs ${theme === 'dark' ? 'text-gray-500' : 'text-gray-600'}`}>
            Inference Metrics
          </span>
          <div className="flex items-center gap-6">
            {visibleMetrics.map((metric, index) => {
              const Icon = metric.icon;
              return (
                <div key={index} className="flex items-center gap-2">
                  <Icon className={`w-3.5 h-3.5 ${
                    theme === 'dark' ? 'text-gray-600' : 'text-gray-500'
                  }`} />
                  <span className={`text-xs ${
                    theme === 'dark' ? 'text-gray-500' : 'text-gray-600'
                  }`}>
                    {metric.label}:
                  </span>
                  <span className={`text-xs ${
                    theme === 'dark' ? 'text-amber-400' : 'text-amber-600'
                  }`}>
                    {metric.value}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}