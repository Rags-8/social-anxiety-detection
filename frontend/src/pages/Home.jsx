import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Zap, Target, Lock } from 'lucide-react';

const Home = () => {
    const navigate = useNavigate();

    return (
        <div className="flex flex-col items-center justify-start min-h-screen py-6 px-6 space-y-8">
            {/* Header Box */}
            <div className="w-full max-w-4xl bg-white/60 backdrop-blur-md rounded-[2rem] p-8 shadow-sm border border-white/40 text-center space-y-2">
                <h1 className="text-3xl font-black text-[#1a365d]">
                    MindCare AI <span className="text-[#76919E]">Social Anxiety Detection</span>
                </h1>
                <p className="text-gray-500 font-medium max-w-xl mx-auto leading-relaxed text-sm">
                    Your personal companion for real-time anxiety analysis and supportive coping strategies.
                    <br />
                    Powered by Advanced AI to help you find balance.
                </p>
            </div>

            {/* Feature Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 w-full max-w-6xl">
                <FeatureCard
                    icon={MessageSquare}
                    title="Share Feelings"
                    description="Express yourself freely in a safe, judgment-free space."
                    borderColor="border-[#D1E9F6]"
                />
                <FeatureCard
                    icon={Zap}
                    title="AI Analysis"
                    description="Instant feedback on your anxiety levels."
                    borderColor="border-[#B2C9D8]"
                />
                <FeatureCard
                    icon={Target}
                    title="Track Progress"
                    description="Monitor your emotional journey with insights."
                    borderColor="border-[#94ADB8]"
                />
                <FeatureCard
                    icon={Lock}
                    title="Private & Secure"
                    description="Your data is processed locally and kept private."
                    borderColor="border-[#76919E]"
                />
            </div>

            {/* Bottom Button */}
            <button
                onClick={() => navigate('/chat')}
                className="bg-gradient-to-r from-[#94ADB8] to-[#587584] hover:from-[#587584] hover:to-[#94ADB8] text-white px-12 py-5 rounded-2xl font-bold tracking-widest text-sm shadow-xl shadow-slate-200 transition-all uppercase active:scale-[0.98]"
            >
                START CHATTING NOW
            </button>
        </div>
    );
};

const FeatureCard = ({ icon: Icon, title, description, borderColor }) => (
    <div className={`bg-white rounded-3xl p-6 shadow-sm border-l-4 ${borderColor} space-y-4 flex flex-col items-start min-h-[220px]`}>
        <div className="p-2.5 rounded-xl bg-gray-50 border border-gray-100">
            <Icon size={20} className="text-gray-700" />
        </div>
        <div className="space-y-2">
            <h3 className="text-lg font-bold text-[#1a365d]">{title}</h3>
            <p className="text-xs text-gray-500 leading-relaxed font-medium">
                {description}
            </p>
        </div>
    </div>
);

export default Home;
