import React, { useState, useEffect } from 'react';
import api from '../api/config';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { ArrowLeft, Activity, AlertTriangle } from 'lucide-react';

const Analysis = ({ onNavigate }) => {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await api.get('/get_insights/guest');
            const stats = response.data;

            const chartData = [
                { name: 'Low', count: stats.low, color: '#10B981' },
                { name: 'Moderate', count: stats.moderate, color: '#F59E0B' },
                { name: 'High', count: stats.high, color: '#EF4444' },
            ];

            setData(chartData);
        } catch (error) {
            console.error("Error fetching stats:", error);
        }
    };

    const total = data.reduce((a, b) => a + b.count, 0);

    return (
        <div className="view-container">
            <div className="view-header">
                <button
                    onClick={() => onNavigate('home')}
                    className="btn-back-view"
                    title="Back to Home"
                >
                    <ArrowLeft size={24} />
                </button>
                <h2 className="view-title">Insights & Trends</h2>
            </div>

            <div className="insights-dashboard">
                <div className="chart-card">
                    <div className="chart-header">
                        <h3 className="card-title">Anxiety Level Distribution</h3>
                        {total < 3 && (
                            <div className="data-warning">
                                <AlertTriangle size={14} />
                                <span>More data needed for accurate trends</span>
                            </div>
                        )}
                    </div>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                <XAxis
                                    dataKey="name"
                                    stroke="#94a3b8"
                                    tick={{ fill: '#64748b', fontSize: 13, fontWeight: 500 }}
                                    axisLine={false}
                                    tickLine={false}
                                    dy={10}
                                />
                                <YAxis
                                    stroke="#94a3b8"
                                    allowDecimals={false}
                                    tick={{ fill: '#64748b', fontSize: 12 }}
                                    axisLine={false}
                                    tickLine={false}
                                    dx={-10}
                                />
                                <Tooltip
                                    cursor={{ fill: 'rgba(241, 245, 249, 0.4)', radius: 8 }}
                                    contentStyle={{
                                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                                        borderColor: '#e2e8f0',
                                        borderRadius: '12px',
                                        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                                        color: '#1e293b',
                                        padding: '12px 16px',
                                        backdropFilter: 'blur(8px)'
                                    }}
                                    itemStyle={{ color: '#334155', fontWeight: 600 }}
                                />
                                <Bar dataKey="count" radius={[8, 8, 0, 0]} barSize={60} animationDuration={1500}>
                                    {data.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} strokeWidth={0} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="stats-grid">
                    {data.map((item) => (
                        <div key={item.name} className={`stat-card ${item.name.toLowerCase()}`}>
                            <div className="stat-info">
                                <p className="stat-label">{item.name} Anxiety</p>
                                <p className="stat-value">{item.count}</p>
                            </div>
                            <div className="stat-percentage">
                                <span style={{ color: item.color }}>
                                    {total > 0 ? Math.round((item.count / total) * 100) : 0}%
                                </span>
                            </div>
                            <div className="stat-bg-icon">
                                <Activity />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Analysis;
