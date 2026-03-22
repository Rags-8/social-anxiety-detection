import React from 'react';
import { Clock } from 'lucide-react';

const History = ({ items }) => {
  if (!items || items.length === 0) return null;

  return (
    <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-white/10 transition-all hover:border-white/20">
      <h3 className="text-lg font-semibold text-slate-200 mb-6 flex items-center gap-2 tracking-wide">
        <Clock className="w-5 h-5 text-blue-400" />
        Prediction History <span className="text-xs font-normal text-slate-500 ml-2 bg-slate-800 px-2 py-0.5 rounded-full">{items.length} Latest</span>
      </h3>
      
      <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
        {items.map((item, idx) => {
          
          let badgeColor = 'bg-blue-500/10 text-blue-400 border-blue-500/20';
          if (item.prediction.includes('High')) badgeColor = 'bg-red-500/10 text-red-400 border-red-500/20';
          else if (item.prediction.includes('Moderate')) badgeColor = 'bg-orange-500/10 text-orange-400 border-orange-500/20';
          else if (item.prediction.includes('Low')) badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';

          return (
            <div key={idx} className="group relative p-4 rounded-xl border border-slate-700/50 bg-slate-800/20 hover:bg-slate-800/50 transition-all flex flex-col gap-2">
              <div className="flex justify-between items-start gap-4">
                <p className="text-slate-200 text-sm italic font-medium">"{item.text}"</p>
                <span className={`shrink-0 px-2.5 py-1 rounded-md text-xs font-medium border ${badgeColor}`}>
                  {item.prediction}
                </span>
              </div>
              <div className="flex items-center justify-between mt-1">
                 <span className="text-xs text-slate-500">
                    {new Date(item.timestamp).toLocaleString(undefined, {
                      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                    })}
                 </span>
                 {item.confidence && (
                    <span className="text-xs font-mono text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                      {(item.confidence * 100).toFixed(1)}% Conf
                    </span>
                 )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  );
};

export default History;
