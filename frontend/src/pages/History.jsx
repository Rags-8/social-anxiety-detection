import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Trash2 } from 'lucide-react';

const History = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedItems, setExpandedItems] = useState(new Set());

    const toggleExpand = (id) => {
        setExpandedItems(prev => {
            const newSet = new Set(prev);
            if (newSet.has(id)) newSet.delete(id);
            else newSet.add(id);
            return newSet;
        });
    };

    const fetchHistory = async () => {
        try {
            const response = await axios.get(`${import.meta.env.VITE_API_URL}/history`);
            setHistory(response.data);
        } catch (error) {
            console.error("Error fetching history:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this conversation?")) return;

        try {
            await axios.delete(`${import.meta.env.VITE_API_URL}/history/${id}`);
            setHistory(history.filter(item => item.id !== id));
        } catch (error) {
            console.error("Error deleting item:", error);
            alert("Failed to delete the item. Please try again.");
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-start min-h-screen py-6 px-6 space-y-8">
            {/* Header Box */}
            <div className="w-full max-w-4xl bg-white/66 backdrop-blur-md rounded-[1.5rem] p-8 shadow-sm border border-white/40 text-center space-y-2">
                <h1 className="text-2xl font-black text-[#1a365d]">
                    Past <span className="text-[#76919E]">Conversations</span>
                </h1>
                <p className="text-gray-500 font-medium max-w-xl mx-auto leading-relaxed text-xs">
                    Review your journey and track your mental well-being over time.
                </p>
            </div>

            {/* Table-like Header Row */}
            <div className="w-full max-w-6xl bg-white/80 rounded-2xl px-10 py-5 flex justify-between items-center shadow-sm border border-white/40">
                <div className="w-1/4 text-[0.7rem] font-black tracking-widest text-[#1a365d] uppercase">Date & Time</div>
                <div className="w-2/4 text-[0.7rem] font-black tracking-widest text-[#1a365d] uppercase px-4">Message</div>
                <div className="w-1/4 text-[0.7rem] font-black tracking-widest text-[#1a365d] uppercase text-right">Anxiety Level</div>
                <div className="w-[80px] text-[0.7rem] font-black tracking-widest text-[#1a365d] uppercase text-right">Action</div>
            </div>

            {/* History Items */}
            <div className="w-full max-w-6xl space-y-4">
                {history.map((item) => (
                    <div key={item.id} className="bg-white/40 hover:bg-white/60 transition-all rounded-2xl px-10 py-6 flex justify-between items-start border border-white/20">
                        <div className="w-1/4 text-sm font-bold text-[#1a365d] pt-1">
                            {new Date(item.timestamp).toLocaleDateString()}
                            <span className="block text-[0.65rem] text-gray-400 font-medium mt-1">
                                {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                        <div
                            className={`w-2/4 text-sm text-[#4a5568] font-medium px-4 cursor-pointer hover:text-[#1a365d] transition-all duration-300 ${expandedItems.has(item.id) ? 'whitespace-pre-wrap' : 'truncate'}`}
                            onClick={() => toggleExpand(item.id)}
                            title={expandedItems.has(item.id) ? "Click to collapse" : "Click to view full message"}
                        >
                            {item.user_text}
                        </div>
                        <div className="w-1/4 flex justify-end pt-1">
                            <span className={`px-4 py-1.5 rounded-full text-[0.6rem] font-black tracking-widest uppercase ${item.anxiety_level === 'High' ? 'bg-[#587584]/15 text-[#1a365d]' :
                                item.anxiety_level === 'Moderate' ? 'bg-[#94ADB8]/15 text-[#587584]' :
                                    'bg-[#B2C9D8]/15 text-[#587584]'
                                }`}>
                                {item.anxiety_level}
                            </span>
                        </div>
                        <div className="w-[80px] flex justify-end pt-0.5">
                            <button
                                onClick={() => handleDelete(item.id)}
                                className="p-2 hover:bg-red-50 rounded-lg transition-colors text-gray-400 hover:text-red-500 group"
                                title="Delete Conversation"
                            >
                                <Trash2 size={18} className="group-hover:scale-110 transition-transform" />
                            </button>
                        </div>
                    </div>
                ))}
                {history.length === 0 && (
                    <div className="text-center py-20 text-gray-400 font-medium">
                        No conversations found. Start your journey today.
                    </div>
                )}
            </div>
        </div>
    );
};

export default History;
