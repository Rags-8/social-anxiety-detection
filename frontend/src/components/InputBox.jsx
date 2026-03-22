import React, { useState } from 'react';
import { Loader2, Send } from 'lucide-react';

const InputBox = ({ onAnalyze, isLoading }) => {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !isLoading) {
      onAnalyze(text);
      setText('');
    }
  };

  return (
    <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-white/10 mb-8 transition-all hover:border-white/20">
      <h2 className="text-xl font-semibold text-white mb-4">Analyze Sentiment</h2>
      <form onSubmit={handleSubmit} className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="How are you feeling today? (e.g., 'I feel panic when I enter crowds')"
          className="w-full min-h-[120px] bg-slate-900/50 text-white placeholder-slate-400 rounded-xl p-4 pr-16 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-slate-700 resize-none transition-all"
        />
        <button
          type="submit"
          disabled={!text.trim() || isLoading}
          className="absolute bottom-4 right-4 bg-blue-600 hover:bg-blue-500 text-white p-3 rounded-lg flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
          )}
        </button>
      </form>
    </div>
  );
};

export default InputBox;
