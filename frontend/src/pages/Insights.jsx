import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ComposedChart, Bar, Line, Legend, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Smile, Meh, Frown } from 'lucide-react';

const Insights = () => {
    const [data, setData] = useState([]);
    const [timelineData, setTimelineData] = useState([]);
    const [summary, setSummary] = useState({ Low: 0, Moderate: 0, High: 0 });

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_URL}/insights`);
                const distribution = response.data.anxiety_distribution;

                // Transform data for chart
                const transformed = distribution.map(item => ({
                    name: item._id,
                    count: item.count,
                }));
                setData(transformed);
                
                if (response.data.timeline) {
                    setTimelineData(response.data.timeline);
                }

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

    // Calculate total for percentages
    const totalPredictions = data.reduce((acc, curr) => acc + curr.count, 0);

    const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, value, name }) => {
        const RADIAN = Math.PI / 180;
        const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
        const x = cx + radius * Math.cos(-midAngle * RADIAN);
        const y = cy + radius * Math.sin(-midAngle * RADIAN);
        const percent = totalPredictions > 0 ? ((value / totalPredictions) * 100).toFixed(0) : 0;

        if (percent === "0") return null;

        return (
            <text x={x} y={y} fill="#1a365d" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central" className="text-[10px] font-black">
                {`${percent}%`}
            </text>
        );
    };

    // Calculate global percentages for tooltip
    const categoryTotals = data.reduce((acc, curr) => {
        acc[curr.name] = curr.count;
        return acc;
    }, { Low: 0, Moderate: 0, High: 0 });

    const getPercentage = (count) => {
        return totalPredictions > 0 ? ((count / totalPredictions) * 100).toFixed(0) : "0";
    };

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            // Group and normalize names
            const categories = ['High', 'Moderate', 'Low'];
            const displayData = categories.map(cat => {
                const item = payload.find(p => p.dataKey === cat);
                return {
                    name: `${cat} Anxiety`,
                    value: item ? item.value : 0,
                    color: COLORS[cat],
                    percent: getPercentage(categoryTotals[cat])
                };
            });

            return (
                <div className="bg-white/95 backdrop-blur-md p-5 rounded-2xl shadow-xl border border-white/40">
                    <p className="text-[0.7rem] font-black text-[#1a365d] mb-3 uppercase tracking-widest border-b border-gray-100 pb-2">{label}</p>
                    <div className="space-y-2">
                        {displayData.map((entry, index) => (
                            <div key={index} className="flex items-center justify-between space-x-12">
                                <div className="flex items-center space-x-2">
                                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }}></div>
                                    <span className="text-[0.75rem] font-bold text-gray-500">{entry.name}</span>
                                </div>
                                <div className="text-right">
                                    <span className="text-[0.75rem] font-black text-[#1a365d] block">
                                        {entry.value} cases ({entry.percent}%)
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="flex flex-col items-center justify-start min-h-screen py-6 px-6 space-y-8">
            {/* Header Box */}
            <div className="w-full max-w-4xl bg-white/60 backdrop-blur-md rounded-[1.5rem] p-6 shadow-sm border border-white/40 text-center space-y-1">
                <h1 className="text-2xl font-black text-[#1a365d]">
                    Anxiety <span className="text-[#76919E]">Trends</span>
                </h1>
                <p className="text-gray-500 font-medium max-w-xl mx-auto leading-relaxed text-[0.65rem]">
                    Unified visualization of your emotional data distribution, percentages, and patterns over time.
                </p>
            </div>

            {/* Combined Visualization Area */}
            <div className="w-full max-w-6xl bg-white rounded-[1.2rem] p-8 shadow-sm border border-white relative min-h-[500px]">
                <div className="text-[0.7rem] font-black tracking-widest text-[#1a365d] uppercase mb-8 text-center flex items-center justify-center space-x-2">
                    <span>Comprehensive Emotional Analysis</span>
                </div>
                
                <ResponsiveContainer width="100%" height={450}>
                    <ComposedChart data={timelineData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                        <XAxis 
                            dataKey="date" 
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
                            label={{ value: 'Number of Predictions', angle: -90, position: 'insideLeft', style: { fill: '#94a3b8', fontSize: 10, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em' } }}
                        />
                        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f8fafc' }} />
                        <Legend 
                            verticalAlign="top" 
                            height={48} 
                            iconType="circle" 
                            wrapperStyle={{ fontSize: '12px', fontWeight: 800, color: '#1a365d', textTransform: 'uppercase', letterSpacing: '0.05em' }}
                        />
                        
                        {/* Grouped Bars for Distribution */}
                        <Bar dataKey="High" fill={COLORS['High']} radius={[4, 4, 0, 0]} barSize={20} name="High Anxiety" />
                        <Bar dataKey="Moderate" fill={COLORS['Moderate']} radius={[4, 4, 0, 0]} barSize={20} name="Moderate Anxiety" />
                        <Bar dataKey="Low" fill={COLORS['Low']} radius={[4, 4, 0, 0]} barSize={20} name="Low Anxiety" />
                        
                        {/* Lines for Trends (legendType="none" to hide duplicates) */}
                        <Line type="monotone" dataKey="High" stroke={COLORS['High']} strokeWidth={2} dot={{ r: 4, strokeWidth: 2, fill: '#fff' }} activeDot={{ r: 6 }} legendType="none" />
                        <Line type="monotone" dataKey="Moderate" stroke={COLORS['Moderate']} strokeWidth={2} dot={{ r: 4, strokeWidth: 2, fill: '#fff' }} activeDot={{ r: 6 }} legendType="none" />
                        <Line type="monotone" dataKey="Low" stroke={COLORS['Low']} strokeWidth={2} dot={{ r: 4, strokeWidth: 2, fill: '#fff' }} activeDot={{ r: 6 }} legendType="none" />
                    </ComposedChart>
                </ResponsiveContainer>
                
                <div className="mt-8 pt-8 border-t border-gray-50 flex flex-wrap justify-center gap-12">
                    {Object.entries(summary).map(([level, count]) => (
                        <div key={level} className="text-center">
                            <span className="block text-[0.65rem] font-black text-gray-400 uppercase tracking-widest mb-2">{level} Anxiety Total</span>
                            <span className="text-2xl font-black text-[#1a365d]">{count}</span>
                            <span className="text-[0.75rem] font-bold text-[#76919E] ml-2">({getPercentage(count)}%)</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Summary Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl text-center">
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
