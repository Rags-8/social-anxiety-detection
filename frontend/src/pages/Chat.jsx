import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Loader2, Send, User, Bot, Sparkles } from 'lucide-react';

const Chat = () => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSend = async (e) => {
        if (e) e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMsg = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setIsLoading(true);

        try {
            const response = await axios.post(`${import.meta.env.VITE_API_URL}/predict`, { text: userMsg });
            const botText = response.data.prediction === 'Uncertain' 
                ? response.data.suggestion 
                : "I've analyzed your thoughts. Here are my insights:";
            
            setMessages(prev => [...prev, {
                role: 'bot',
                text: botText,
                data: response.data
            }]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                role: 'bot',
                text: "Stay calm. I'm having a little trouble connecting right now. Please try again in a moment."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full overflow-hidden max-w-5xl mx-auto px-4 relative">
            {/* Header Area */}
            <div className="py-6 flex flex-col items-center flex-shrink-0">
                <h1 className="text-2xl font-black text-[#1a365d]">
                    MindCare <span className="text-[#76919E]">Chat</span>
                </h1>
                <p className="text-[0.65rem] font-bold tracking-[0.2em] text-[#94ADB8] uppercase mt-1">
                    Your safe space for emotional support
                </p>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-2 space-y-8 pb-32 scrollbar-hide">
                {messages.length === 0 && !isLoading && (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-4 opacity-60">
                        <div className="w-16 h-16 bg-white/40 rounded-3xl flex items-center justify-center border border-white/40">
                            <Sparkles className="text-[#94ADB8]" size={32} />
                        </div>
                        <p className="text-lg font-medium text-[#1a365d]">Start a conversation by sharing how you feel.</p>
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                        <div className={`flex max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start gap-4`}>
                            {/* Avatar */}
                            <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm border ${msg.role === 'user'
                                ? 'bg-[#587584] border-white/20'
                                : 'bg-white/80 border-white/40'
                                }`}>
                                {msg.role === 'user' ? <User size={18} className="text-white" /> : <Bot size={18} className="text-[#76919E]" />}
                            </div>

                            {/* Bubble */}
                            <div className="flex flex-col space-y-2">
                                <div className={`px-6 py-4 rounded-[2rem] shadow-sm ${msg.role === 'user'
                                    ? 'bg-[#587584] text-white rounded-tr-none'
                                    : 'bg-white/80 backdrop-blur-md rounded-tl-none border border-white/40'
                                    }`}>
                                    <p className="text-sm font-medium leading-relaxed">
                                        {Array.isArray(msg.text) ? msg.text.join(' ') : msg.text}
                                    </p>
                                </div>

                                {/* Bot Analysis Details */}
                                {msg.role === 'bot' && msg.data && msg.data.prediction !== 'Uncertain' && (
                                    <div className="bg-white/40 backdrop-blur-sm rounded-[2rem] p-6 border border-white/20 space-y-6 mt-2 ml-2">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[0.6rem] font-black uppercase tracking-widest text-[#94ADB8]">Analysis</span>
                                            <div className="flex gap-2">
                                                <span className={`px-3 py-1 rounded-full text-[0.6rem] font-black tracking-widest uppercase ${
                                                    msg.data.prediction === 'High Anxiety' ? 'bg-red-100 text-red-800' :
                                                    msg.data.prediction === 'Moderate Anxiety' ? 'bg-orange-100 text-orange-800' :
                                                    msg.data.prediction === 'Low Anxiety' ? 'bg-green-100 text-green-800' :
                                                    'bg-[#B2C9D8]/20 text-[#587584]'
                                                }`}>
                                                    {msg.data.prediction}
                                                </span>
                                                {msg.data.confidence !== undefined && (
                                                    <span className="px-3 py-1 rounded-full text-[0.6rem] font-black tracking-widest uppercase bg-white/60 text-[#587584] border border-white/40 shadow-sm">
                                                        {(msg.data.confidence * 100).toFixed(1)}% Conf
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                        {msg.data.reason && (
                                            <div className="bg-white/20 p-4 rounded-xl border border-white/10">
                                                <p className="text-[0.65rem] font-black text-[#76919E] uppercase tracking-widest mb-1">Reasoning</p>
                                                <p className="text-[0.7rem] font-bold text-gray-600 leading-tight">{msg.data.reason}</p>
                                            </div>
                                        )}

                                        {msg.data.detected_words && msg.data.detected_words.length > 0 && (
                                            <div>
                                                <p className="text-[0.65rem] font-black text-[#94ADB8] uppercase tracking-widest mb-2">Detected Words</p>
                                                <div className="flex flex-wrap gap-2">
                                                    {msg.data.detected_words.map((dw, i) => {
                                                        const isHigh = dw.label === 'High';
                                                        const isMod = dw.label === 'Moderate';
                                                        return (
                                                            <div key={i} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-[0.65rem] font-bold tracking-wide ${
                                                                isHigh ? 'bg-red-50 text-red-700 border-red-100' : 
                                                                isMod ? 'bg-amber-50 text-amber-700 border-amber-100' : 
                                                                'bg-emerald-50 text-emerald-700 border-emerald-100'
                                                            }`}>
                                                                {dw.word}
                                                                <span className="opacity-60 font-black border-l border-current pl-1.5 ml-0.5 uppercase tracking-widest text-[0.55rem]">
                                                                    {dw.label}
                                                                </span>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        )}

                                        {msg.data.suggestions && msg.data.suggestions.length > 0 && (
                                            <div className="grid grid-cols-1 gap-3 mt-4">
                                                <p className="text-[0.65rem] font-black text-[#94ADB8] uppercase tracking-widest mb-1">Tailored Suggestions</p>
                                                {msg.data.suggestions.slice(0, 3).map((s, i) => (
                                                    <div key={i} className="flex items-center gap-3 bg-white/20 p-3 rounded-xl border border-white/10">
                                                        <div className="w-1.5 h-1.5 bg-[#76919E] rounded-full" />
                                                        <p className="text-[0.7rem] font-bold text-gray-600 leading-tight">{s}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                )}
                                
                                {msg.role === 'bot' && msg.data && msg.data.prediction === 'Uncertain' && msg.data.follow_up && (
                                    <div className="bg-blue-50/50 p-6 rounded-[2rem] border border-blue-100/50 mt-2 ml-2">
                                        <p className="text-[0.65rem] font-black text-blue-600 uppercase tracking-widest mb-3">Questions for Clarity</p>
                                        <ul className="list-disc list-inside text-[0.7rem] font-bold text-blue-800 leading-relaxed space-y-1">
                                            {msg.data.follow_up.map((q, i) => (
                                                <li key={i}>{q}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start animate-in fade-in duration-300">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-2xl bg-white/80 border border-white/40 flex items-center justify-center shadow-sm">
                                <Bot size={18} className="text-[#76919E]" />
                            </div>
                            <div className="bg-white/40 backdrop-blur-md px-6 py-4 rounded-[2rem] rounded-tl-none border border-white/20">
                                <div className="flex gap-1.5">
                                    <div className="w-2 h-2 bg-[#94ADB8] rounded-full animate-bounce delay-75" />
                                    <div className="w-2 h-2 bg-[#94ADB8] rounded-full animate-bounce delay-150" />
                                    <div className="w-2 h-2 bg-[#94ADB8] rounded-full animate-bounce delay-300" />
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Fixed at Bottom */}
            <div className="absolute bottom-8 left-0 right-0 px-4">
                <form
                    onSubmit={handleSend}
                    className="max-w-4xl mx-auto relative group"
                >
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#B2C9D8] to-[#94ADB8] rounded-[2.5rem] blur opacity-20 group-focus-within:opacity-40 transition duration-500"></div>
                    <div className="relative flex items-center bg-white/80 backdrop-blur-xl rounded-[2.5rem] shadow-lg border border-white/60 p-2 pl-8">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSend();
                                }
                            }}
                            placeholder="Share your thoughts..."
                            className="flex-1 bg-transparent py-4 text-[#1a365d] placeholder-[#94ADB8] focus:outline-none resize-none max-h-32 text-sm font-medium"
                            rows="1"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="ml-4 w-12 h-12 bg-gradient-to-br from-[#76919E] to-[#587584] rounded-2xl flex items-center justify-center text-white shadow-md hover:scale-105 active:scale-95 transition-all disabled:opacity-40 disabled:hover:scale-100"
                        >
                            <Send size={18} />
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Chat;
