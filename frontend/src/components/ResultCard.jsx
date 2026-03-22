import React from 'react';
import { AlertCircle, CheckCircle, HelpCircle, Activity } from 'lucide-react';

const ResultCard = ({ result }) => {
  if (!result) return null;

  const getStyle = (prediction) => {
    switch (prediction) {
      case 'High Anxiety':
        return { color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20', icon: <AlertCircle className="w-6 h-6 text-red-500" /> };
      case 'Moderate Anxiety':
        return { color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20', icon: <Activity className="w-6 h-6 text-orange-500" /> };
      case 'Low Anxiety':
        return { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', icon: <CheckCircle className="w-6 h-6 text-emerald-500" /> };
      default:
        return { color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20', icon: <HelpCircle className="w-6 h-6 text-blue-500" /> };
    }
  };

  const style = getStyle(result.prediction);

  return (
    <div className={`rounded-2xl p-6 shadow-xl border backdrop-blur-md transition-all ${style.bg} ${style.border}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          {style.icon}
          Prediction Result
        </h2>
        {result.confidence && (
          <span className="bg-slate-800 text-slate-300 px-3 py-1 rounded-full text-sm border border-slate-700 font-medium">
            Conf: {(result.confidence * 100).toFixed(1)}%
          </span>
        )}
      </div>

      <div className="space-y-4">
        <div>
          <p className="text-slate-400 text-sm mb-1 uppercase tracking-wider font-semibold">Classification</p>
          <p className={`text-3xl font-bold ${style.color} drop-shadow-sm`}>{result.prediction}</p>
        </div>

        {result.reason && (
          <div>
            <p className="text-slate-400 text-sm mb-1 uppercase tracking-wider font-semibold">Reasoning</p>
            <p className="text-slate-200">{result.reason}</p>
          </div>
        )}

        {result.suggestion && (
          <div className="bg-blue-900/20 border border-blue-800/50 rounded-xl p-4 mt-4">
             <p className="text-blue-300 font-medium mb-2">{result.suggestion}</p>
             <ul className="list-disc list-inside text-slate-300 text-sm space-y-1">
               {result.follow_up?.map((q, i) => (
                 <li key={i}>{q}</li>
               ))}
             </ul>
          </div>
        )}

        {result.detected_words && result.detected_words.length > 0 && (
          <div className="pt-4 border-t border-white/5">
            <p className="text-slate-400 text-sm mb-3 uppercase tracking-wider font-semibold">Detected Keywords</p>
            <div className="flex flex-wrap gap-2">
              {result.detected_words.map((dw, i) => {
                const tagStyle = getStyle(dw.label === 'High' ? 'High Anxiety' : dw.label === 'Moderate' ? 'Moderate Anxiety' : 'Low Anxiety');
                return (
                  <span key={i} className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1.5 ${tagStyle.bg} ${tagStyle.color} border ${tagStyle.border}`}>
                    {dw.word} <span className="text-xs opacity-70 border-l border-current pl-1.5 ml-0.5">{dw.label}</span>
                  </span>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultCard;
