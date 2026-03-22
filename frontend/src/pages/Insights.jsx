import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend as RechartsLegend } from 'recharts';
import { Smile, Meh, Frown, HelpCircle } from 'lucide-react';

const Insights = () => {
    const [trends, setTrends] = useState([]);
    const [loading, setLoading] = useState(true);
    const [counts, setCounts] = useState({ High: 0, Moderate: 0, Low: 0, Uncertain: 0 });

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_URL}/insights`);
                const distribution = response.data.anxiety_distribution || [];
                const dailyTrends = response.data.daily_trends || [];

                // Format dates for display
                const formattedTrends = dailyTrends.map(t => ({
                    ...t,
                    name: new Date(t.day).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })
                }));
                
                setTrends(formattedTrends);

                // Update summary counts
                const newCounts = { High: 0, Moderate: 0, Low: 0, Uncertain: 0 };
                distribution.forEach(item => {
                    const key = item._id;
                    if (newCounts.hasOwnProperty(key)) {
                        newCounts[key] = item.count;
                    }
                });
                setCounts(newCounts);
            } catch (error) {
                console.error("Error fetching insights:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Original Dusty Blue Palette
    const COLORS = {
        'Low': '#D1E9F6',
        'Moderate': '#B2C9D8',
        'High': '#94ADB8'
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#B2C9D8]"></div>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-start min-h-screen py-6 px-6 space-y-8">
            {/* Header Box */}
            <div className="w-full max-w-5xl bg-white/60 backdrop-blur-md rounded-[1.5rem] p-6 shadow-sm border border-white/40 text-center space-y-1">
                <h1 className="text-2xl font-black text-[#1a365d]">
                    Anxiety <span className="text-[#94ADB8]">Insights</span>
                </h1>
                <p className="text-gray-500 font-medium max-w-xl mx-auto leading-relaxed text-[0.65rem]">
                    Restored your "Bar + line" combination to visualize your emotional progress over time.
                </p>
            </div>

            {/* Combined Visualization Area */}
            <div className="w-full max-w-5xl bg-white rounded-[1.5rem] p-8 shadow-sm border border-white relative min-h-[450px] flex flex-col">
                <div className="text-[0.7rem] font-black tracking-widest text-[#1a365d] uppercase mb-10 text-center flex items-center justify-center space-x-2 w-full">
                    <span>Daily Progress Variation</span>
                </div>
                
                <div className="w-full h-[400px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={trends} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                            <XAxis 
                                dataKey="name" 
                                axisLine={false} 
                                tickLine={false} 
                                tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 700 }}
                                dy={10}
                            />
                            <YAxis 
                                axisLine={false} 
                                tickLine={false} 
                                tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 700 }}
                                dx={-5}
                            />
                            <RechartsTooltip 
                                contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                            />
                            <RechartsLegend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px' }}/>
                            
                            {/* Bars for Daily Counts */}
                            <Bar dataKey="Low" fill={COLORS.Low} radius={[8, 8, 0, 0]} barSize={20} />
                            <Bar dataKey="Moderate" fill={COLORS.Moderate} radius={[8, 8, 0, 0]} barSize={20} />
                            <Bar dataKey="High" fill={COLORS.High} radius={[8, 8, 0, 0]} barSize={20} />
                            
                            {/* Lines for Trend Variation */}
                            <Line type="monotone" dataKey="Low" stroke={COLORS.Low} strokeWidth={4} dot={{ r: 4 }} />
                            <Line type="monotone" dataKey="Moderate" stroke={COLORS.Moderate} strokeWidth={4} dot={{ r: 4 }} />
                            <Line type="monotone" dataKey="High" stroke={COLORS.High} strokeWidth={4} dot={{ r: 4 }} />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Summary Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 w-full max-w-5xl text-center">
                <SummaryCard
                    title="Low Anxiety"
                    count={counts.Low}
                    icon={Smile}
                    color="text-[#D1E9F6]"
                    borderColor="border-[#D1E9F6]"
                />
                <SummaryCard
                    title="Moderate Anxiety"
                    count={counts.Moderate}
                    icon={Meh}
                    color="text-[#B2C9D8]"
                    borderColor="border-[#B2C9D8]"
                />
                <SummaryCard
                    title="High Anxiety"
                    count={counts.High}
                    icon={Frown}
                    color="text-[#94ADB8]"
                    borderColor="border-[#94ADB8]"
                />
                <SummaryCard
                    title="Uncertain"
                    count={counts.Uncertain}
                    icon={HelpCircle}
                    color="text-slate-300"
                    borderColor="border-slate-100"
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
