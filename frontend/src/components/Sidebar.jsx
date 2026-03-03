import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, MessageSquare, History, BarChart2, ChevronsLeft, ChevronsRight, Leaf } from 'lucide-react';

const Sidebar = ({ isCollapsed, setIsCollapsed }) => {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    const navItems = [
        { path: '/', name: 'Home', icon: Home },
        { path: '/chat', name: 'Chat', icon: MessageSquare },
        { path: '/history', name: 'History', icon: History },
        { path: '/insights', name: 'Insights', icon: BarChart2 },
    ];

    return (
        <div className={`h-screen ${isCollapsed ? 'w-24' : 'w-72'} bg-gradient-to-b from-[#B2C9D8] via-[#D1E9F6] to-[#D1E9F6] flex flex-col fixed left-0 top-0 rounded-r-[3rem] shadow-xl z-50 transition-all duration-300`}>
            {/* Collapse Icon */}
            <div className={`flex ${isCollapsed ? 'justify-center' : 'justify-end'} p-4`}>
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="text-[#587584] hover:text-[#1a365d] transition-colors"
                >
                    {isCollapsed ? <ChevronsRight size={24} /> : <ChevronsLeft size={20} />}
                </button>
            </div>

            {/* Brand Card */}
            <div className={`px-6 mb-8 transition-opacity duration-300 ${isCollapsed ? 'opacity-0 h-0 overflow-hidden mb-0' : 'opacity-100'}`}>
                <div className="bg-white/60 backdrop-blur-md rounded-[2.5rem] p-8 shadow-sm border border-white/20 flex flex-col items-center justify-center text-center">
                    <div className="w-16 h-16 bg-white/40 rounded-2xl flex items-center justify-center mb-4 shadow-inner border border-[#B2C9D8]/30">
                        <Leaf className="text-[#587584] fill-[#587584]/10" size={32} />
                    </div>
                    <h1 className="text-2xl font-bold text-[#1a365d] mb-1">
                        MindCare
                    </h1>
                    <p className="text-[0.65rem] font-bold tracking-[0.15em] text-[#587584] uppercase">
                        SOCIAL ANXIETY DETECTION
                    </p>
                </div>
            </div>

            {/* Navigation */}
            <nav className={`flex-1 ${isCollapsed ? 'px-4' : 'px-8'} space-y-4`}>
                {navItems.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={`flex items-center ${isCollapsed ? 'justify-center' : 'px-4'} py-3 rounded-2xl transition-all duration-300 font-semibold text-lg ${isActive(item.path)
                            ? 'bg-white text-[#1a365d] shadow-sm'
                            : 'text-[#4a5568] hover:bg-white/40 hover:text-[#1a365d]'
                            }`}
                        title={isCollapsed ? item.name : ""}
                    >
                        <item.icon size={24} className={isCollapsed ? "" : "mr-3 h-0 w-0 md:h-6 md:w-6 overflow-hidden"} />
                        {!isCollapsed && <span>{item.name}</span>}
                    </Link>
                ))}
            </nav>
        </div>
    );
};

export default Sidebar;
