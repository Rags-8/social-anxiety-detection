import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

const Chart = ({ history }) => {
  if (!history || history.length === 0) return null;

  const counts = { High: 0, Moderate: 0, Low: 0, Uncertain: 0 };

  history.forEach((h) => {
    if (h.prediction.includes('High')) counts.High++;
    else if (h.prediction.includes('Moderate')) counts.Moderate++;
    else if (h.prediction.includes('Low')) counts.Low++;
    else counts.Uncertain++;
  });

  const data = {
    labels: ['High Anxiety', 'Moderate Anxiety', 'Low Anxiety', 'Uncertain'],
    datasets: [
      {
        data: [counts.High, counts.Moderate, counts.Low, counts.Uncertain],
        backgroundColor: [
          'rgba(244, 63, 94, 0.8)',   // Rose 500
          'rgba(249, 115, 22, 0.8)',  // Orange 500
          'rgba(16, 185, 129, 0.8)',  // Emerald 500
          'rgba(99, 102, 241, 0.8)',  // Indigo 500
        ],
        borderColor: [
          'rgba(244, 63, 94, 1)',
          'rgba(249, 115, 22, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(99, 102, 241, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#cbd5e1', // text-slate-300
          padding: 20,
          font: { family: 'inherit' }
        }
      }
    },
    cutout: '70%',
    maintainAspectRatio: false
  };

  return (
    <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-white/10 h-[300px] flex flex-col transition-all hover:border-white/20">
      <h3 className="text-lg font-semibold text-slate-200 mb-4 tracking-wide flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
        Recent Trend Analysis
      </h3>
      <div className="relative flex-1 w-full flex items-center justify-center">
        <Doughnut data={data} options={options} />
      </div>
    </div>
  );
};

export default Chart;
