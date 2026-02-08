import React, { useState, useEffect, useRef } from 'react';
import api from '../api/config'; // Use configured api
import { Send, Loader, ArrowLeft } from 'lucide-react';

const ChatInterface = ({ onNavigate }) => {
    const [messages, setMessages] = useState([
        {
            text: "Hello! I'm here to listen. How are you feeling today?",
            sender: 'bot',
            timestamp: new Date().toISOString()
        }
    ]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!inputText.trim()) return;

        const userMessage = {
            text: inputText,
            sender: 'user',
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputText('');
        setIsLoading(true);

        try {
            const response = await api.post('/predict', {
                text: userMessage.text,
                user_id: 'guest'
            });

            const data = response.data;

            const botMessage = {
                text: data.explanation,
                sender: 'bot',
                anxiety_level: data.anxiety_level,
                suggestions: data.suggestions,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, botMessage]);

        } catch (error) {
            console.error("Error sending message:", error);
            setMessages(prev => [...prev, {
                text: "I'm having trouble connecting to the server. Please check if the backend is running.",
                sender: 'bot',
                anxiety_level: 'Error'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chat-container">
            {/* Header */}
            <div className="chat-header">
                <button
                    onClick={() => onNavigate('home')}
                    className="btn-back"
                    title="Back to Home"
                >
                    <ArrowLeft size={24} />
                </button>
                <div>
                    <h2 className="chat-title">Chat Session</h2>
                    <p className="chat-subtitle">MindCare AI - Anxiety Assistant</p>
                </div>
            </div>

            {/* Messages Area */}
            <div className="chat-messages-area">
                {messages.length <= 1 ? (
                    <div className="chat-empty-state">
                        <div className="empty-state-icon">
                            <Send size={32} />
                        </div>
                        <h3 className="empty-state-title">Start by typing how you're feeling...</h3>
                        <p className="empty-state-text">
                            Our AI is ready to listen and analyze your sentiment to provide helpful insights.
                        </p>
                    </div>
                ) : (
                    messages.map((msg, idx) => (
                        <div key={idx} className={`message-wrapper ${msg.sender === 'user' ? 'user' : 'bot'}`}>
                            <div className={`message-bubble ${msg.sender === 'user' ? 'user' : 'bot'}`}>
                                <p>{msg.text}</p>
                            </div>

                            {msg.sender === 'bot' && msg.anxiety_level && msg.anxiety_level !== 'Error' && (
                                <div className={`anxiety-card ${msg.anxiety_level.includes('Low') ? 'low' : msg.anxiety_level.includes('Moderate') ? 'moderate' : 'high'}`}>
                                    <div className="anxiety-header">
                                        <div className={`anxiety-indicator ${msg.anxiety_level.includes('Low') ? 'low' : msg.anxiety_level.includes('Moderate') ? 'moderate' : 'high'}`}></div>
                                        <span className="anxiety-label">Detected: {msg.anxiety_level}</span>
                                    </div>

                                    {msg.suggestions && msg.suggestions.length > 0 && (
                                        <div className="suggestions-list">
                                            <p className="suggestions-title">Suggestions</p>
                                            <ul>
                                                {msg.suggestions.map((s, i) => (
                                                    <li key={i}>{s}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            )}
                            <span className="message-time">
                                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                    ))
                )}
                {isLoading && (
                    <div className="loading-indicator">
                        <span>Anxiety Assistant is analyzing...</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form className="chat-input-form" onSubmit={handleSend}>
                <div className="chat-input-wrapper">
                    <input
                        type="text"
                        className="chat-input"
                        placeholder="Share how you're feeling today..."
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !inputText.trim()}
                        className="btn-send"
                    >
                        <Send size={20} />
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ChatInterface;
