import React from 'react';
import Sidebar from './Sidebar';
import { } from 'lucide-react';

const Layout = ({ children }) => {
    const [isCollapsed, setIsCollapsed] = React.useState(false);

    return (
        <div className="flex bg-gradient-to-br from-[#D1E9F6]/30 to-[#B2C9D8]/20 min-h-screen font-sans text-[#1a365d]">
            <Sidebar isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />

            <div className={`flex-1 ${isCollapsed ? 'ml-24' : 'ml-72'} flex flex-col relative h-screen overflow-hidden transition-all duration-300`}>
                {/* Top Utility Bar - Removed as requested */}
                <div className="h-16"></div>

                {/* Main Content */}
                <div className="flex-1 overflow-y-auto px-12 py-4">
                    {children}
                </div>


            </div>
        </div>
    );
};

export default Layout;
