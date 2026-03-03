import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Smile, Meh, Frown } from 'lucide-react';

const Insights = () => {
    const [data, setData] = useState([]);
    const [summary, setSummary] = useState({ Low: 0, Moderate: 0, High: 0 });

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:8001/insights');
                const distribution = response.data.anxiety_distribution;

                // Transform data for chart
                const transformed = distribution.map(item => ({
                    name: item._id,
                    count: item.count,
                }));
                setData(transformed);

                // Update summary counts
                const newSummary = { Low: 0, Moderate: 0, High: 0 };
                distribution.forEach(item => {
                    if (newSummary.hasOwnProperty(item._id)) {
                        newSummary[item._id] = item.count;
                    }
                });
                setSummary(newSummary);
            } catch (error) {
                console.error("Error fetching insights:", error);
            }
        };
        fetchData();
    }, []);

    const COLORS = {
        'Low': '#D1E9F6',      // Dusty Sky
        'Moderate': '#B2C9D8', // Dusty Blue
        'High': '#94ADB8'      // Mid Slate
    };

    return (
        <div className="flex flex-col items-center justify-start min-h-screen py-6 px-6 space-y-8">
            {/* Header Box */}
            <div className="w-full max-w-4xl bg-white/60 backdrop-blur-md rounded-[1.5rem] p-6 shadow-sm border border-white/40 text-center space-y-1">
                <h1 className="text-2xl font-black text-[#1a365d]">
                    Anxiety <span className="text-[#76919E]">Trends</span>
                </h1>
                <p className="text-gray-500 font-medium max-w-xl mx-auto leading-relaxed text-[0.65rem]">
                    Visualizing your emotional data to help you understand patterns.
                </p>
            </div>

            {/* Chart Box */}
            <div className="w-full max-w-6xl bg-white rounded-[1.2rem] p-6 shadow-sm border border-white relative min-h-[350px]">
                <div className="absolute top-6 right-8 flex space-x-2 text-gray-300">
                    <div className="p-1.5 border border-gray-100 rounded-lg"><div className="w-4 h-4 border-2 border-current"></div></div>
                    <div className="p-1.5 border border-gray-100 rounded-lg"><div className="w-4 h-4 border-2 border-current rounded-full"></div></div>
                </div>

                <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                        <XAxis
                            dataKey="name"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 600 }}
                            dy={10}
                        />
                        <YAxis
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 600 }}
                            dx={-10}
                        />
                        <Tooltip
                            cursor={{ fill: '#f8fafc' }}
                            contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                        />
                        <Bar dataKey="count" radius={[10, 10, 10, 10]} barSize={80}>
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#8884d8'} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>

                <div className="mt-4 flex justify-center text-[0.65rem] font-bold tracking-widest text-gray-400 uppercase">
                    Anxiety Level
                </div>
                <div className="absolute left-6 top-1/2 -rotate-90 text-[0.65rem] font-bold tracking-widest text-gray-400 uppercase origin-left">
                    Count
                </div>
            </div>

            {/* Summary Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl">
                <SummaryCard
                    title="Low Anxiety"
                    count={summary.Low}
                    icon={Smile}
                    color="text-[#587584]"
                    borderColor="border-[#D1E9F6]"
                    bg="bg-slate-50/80"
                />
                <SummaryCard
                    title="Moderate Anxiety"
                    count={summary.Moderate}
                    icon={Meh}
                    color="text-[#587584]"
                    borderColor="border-[#B2C9D8]"
                    bg="bg-slate-100/60"
                />
                <SummaryCard
                    title="High Anxiety"
                    count={summary.High}
                    icon={Frown}
                    color="text-[#1a365d]"
                    borderColor="border-[#94ADB8]"
                    bg="bg-slate-200/40"
                />
            </div>
        </div>
    );
};

const SummaryCard = ({ title, count, icon: Icon, color, borderColor, bg }) => (
    <div className={`bg-white rounded-[1.5rem] p-6 shadow-sm border-l-4 ${borderColor} relative flex flex-col justify-between min-h-[140px]`}>
        <div>
            <div className="text-[0.6rem] font-black tracking-widest text-gray-400 uppercase mb-2">
                {title}
            </div>
            <div className="text-4xl font-black text-[#1a365d]">
                {count}
            </div>
        </div>
        <div className={`absolute bottom-6 right-6 ${color}`}>
            <Icon size={32} fill="currentColor" fillOpacity={0.1} />
        </div>
    </div>
);

export default Insights;
