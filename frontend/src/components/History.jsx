import React, { useState, useEffect } from 'react';
import api from '../api/config';
import { Trash2, ArrowLeft, Clock, MessageSquare } from 'lucide-react';

const History = ({ onNavigate }) => {
    const [history, setHistory] = useState([]);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await api.get('/history/guest');
            setHistory(response.data.reverse()); // Show newest first
        } catch (error) {
            console.error("Error fetching history:", error);
        }
    };

    const deleteChat = async (id) => {
        if (!window.confirm("Are you sure you want to delete this record?")) return;
        try {
            await api.delete(`/history/${id}`);
            setHistory(prev => prev.filter(chat => chat.id !== id));
        } catch (error) {
            console.error("Error deleting chat:", error);
        }
    };

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
                <h2 className="view-title">Past Conversations</h2>
            </div>

            {history.length === 0 ? (
                <div className="empty-history-state">
                    <div className="empty-icon-wrapper">
                        <MessageSquare size={48} />
                    </div>
                    <h3 className="empty-title">No conversation history yet</h3>
                    <p className="empty-text">
                        Start a new chat to track your journey. Your conversations will appear here.
                    </p>
                </div>
            ) : (
                <div className="history-list">
                    <div className="history-table-header">
                        <div className="col-date">Date & Time</div>
                        <div className="col-message">Message</div>
                        <div className="col-anxiety">Anxiety Level</div>
                        <div className="col-action">Action</div>
                    </div>
                    <div className="history-items">
                        {history.map((chat) => (
                            <div key={chat.id} className="history-item-card">
                                <div className="history-cell date">
                                    <Clock size={16} className="cell-icon" />
                                    <span>{new Date(chat.timestamp).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}</span>
                                </div>
                                <div className="history-cell message">
                                    <p>{chat.message}</p>
                                </div>
                                <div className="history-cell anxiety">
                                    <span className={`status-badge ${chat.anxiety_level && chat.anxiety_level.includes('Low') ? 'low' :
                                        chat.anxiety_level && chat.anxiety_level.includes('Moderate') ? 'moderate' :
                                            'high'
                                        }`}>
                                        <span className="status-dot"></span>
                                        {chat.anxiety_level || 'Unknown'}
                                    </span>
                                </div>
                                <div className="history-cell action">
                                    <button
                                        onClick={() => deleteChat(chat.id)}
                                        className="btn-delete"
                                        title="Delete Record"
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default History;
