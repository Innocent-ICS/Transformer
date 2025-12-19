'use client'

import { PanelLeftClose, PanelLeft, Plus, MessageSquare, Languages, Trash2, Search } from 'lucide-react';
import { useState } from 'react';
import { UserMenu } from './UserMenu';
import { Mode, Theme } from './MessageBubble';

export interface Session {
    id: string;
    title: string;
    mode: Mode;
    messages: any[];
    createdAt: Date;
    updatedAt: Date;
}

interface SidebarProps {
    sessions: Session[];
    activeSessionId: string | null | undefined;
    onSessionSelect: (id: string) => void;
    onNewSession: (mode?: Mode) => void;
    onDeleteSession: (id: string) => void;
    isOpen: boolean;
    onToggle: () => void;
    theme: Theme;
    currentMode: Mode;
    onThemeToggle: () => void;
}

export function Sidebar({
    sessions,
    activeSessionId,
    onSessionSelect,
    onNewSession,
    onDeleteSession,
    isOpen,
    onToggle,
    theme,
    currentMode,
    onThemeToggle,
}: SidebarProps) {
    const [searchQuery, setSearchQuery] = useState('');

    const filteredSessions = sessions.filter(session =>
        session.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const groupedSessions = {
        today: filteredSessions.filter(s => {
            const diff = Date.now() - s.updatedAt.getTime();
            return diff < 86400000; // 24 hours
        }),
        yesterday: filteredSessions.filter(s => {
            const diff = Date.now() - s.updatedAt.getTime();
            return diff >= 86400000 && diff < 172800000; // 24-48 hours
        }),
        previous7Days: filteredSessions.filter(s => {
            const diff = Date.now() - s.updatedAt.getTime();
            return diff >= 172800000 && diff < 604800000; // 2-7 days
        }),
        older: filteredSessions.filter(s => {
            const diff = Date.now() - s.updatedAt.getTime();
            return diff >= 604800000; // >7 days
        }),
    };



    return (
        <aside className={`h-full bg-white dark:bg-[#1a1a1a] flex flex-col border-r border-gray-200 dark:border-[#2a2a2a]/50 transition-all duration-300 ease-in-out ${isOpen ? 'w-72' : 'w-16'}`}>
            {/* Sidebar Header */}
            <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                    {isOpen && <h2 className="text-sm text-gray-600 dark:text-gray-400">Sessions</h2>}
                    <button
                        onClick={onToggle}
                        className="p-1.5 rounded-lg hover:bg-gray-200/50 dark:hover:bg-[#252525] transition-colors"
                        aria-label={isOpen ? "Close sidebar" : "Open sidebar"}
                    >
                        {isOpen ? (
                            <PanelLeftClose className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        ) : (
                            <PanelLeft className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        )}
                    </button>
                </div>

                <button
                    onClick={() => onNewSession(currentMode)}
                    className={`w-full flex items-center gap-2 px-4 py-2.5 bg-amber-600 dark:bg-white text-white dark:text-gray-900 rounded-lg hover:bg-amber-700 dark:hover:bg-gray-100 transition-all shadow-sm ${isOpen ? 'justify-center' : 'justify-center'}`}
                    title={!isOpen ? `New ${currentMode === 'chat' ? 'Chat' : 'Translation'}` : undefined}
                >
                    <Plus className="w-4 h-4" />
                    {isOpen && <span>New {currentMode === 'chat' ? 'Chat' : 'Translation'}</span>}
                </button>

                {/* Search */}
                {isOpen && (
                    <div className="mt-3 relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search sessions..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-9 pr-3 py-2 bg-white dark:bg-[#222222] border border-gray-200 dark:border-[#333333] rounded-lg text-sm text-gray-900 placeholder:text-gray-400 dark:text-white focus:outline-none focus:ring-1 focus:ring-amber-600/30 dark:focus:ring-amber-700/30 focus:border-amber-600/50 dark:focus:border-amber-600/50"
                        />
                    </div>
                )}
            </div>

            {/* Sessions List */}
            {isOpen && (
                <div className="flex-1 overflow-y-auto px-3 py-3">
                    {Object.entries(groupedSessions).map(([group, groupSessions]) => {
                        if (groupSessions.length === 0) return null;

                        const groupLabels = {
                            today: 'Today',
                            yesterday: 'Yesterday',
                            previous7Days: 'Previous 7 Days',
                            older: 'Older',
                        };

                        return (
                            <div key={group} className="mb-4">
                                <h3 className="px-3 py-1.5 text-xs text-gray-500 dark:text-gray-500">
                                    {groupLabels[group as keyof typeof groupLabels]}
                                </h3>
                                <div className="space-y-1">
                                    {groupSessions.map((session) => (
                                        <div
                                            key={session.id}
                                            className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all ${activeSessionId === session.id
                                                ? 'bg-white/60 dark:bg-[#2a2a2a] shadow-sm'
                                                : 'hover:bg-white/30 dark:hover:bg-[#222222]'
                                                }`}
                                            onClick={() => onSessionSelect(session.id)}
                                        >
                                            <div className={`flex-shrink-0 ${theme === 'dark' && activeSessionId === session.id
                                                ? 'text-amber-500'
                                                : 'text-gray-500 dark:text-gray-500'
                                                }`}>
                                                {session.mode === 'chat' ? (
                                                    <MessageSquare className="w-4 h-4" />
                                                ) : (
                                                    <Languages className="w-4 h-4" />
                                                )}
                                            </div>
                                            <span className={`flex-1 text-sm truncate ${activeSessionId === session.id
                                                ? 'text-gray-900 dark:text-white'
                                                : 'text-gray-700 dark:text-gray-300'
                                                }`}>
                                                {session.title}
                                            </span>
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    onDeleteSession(session.id);
                                                }}
                                                className="flex-shrink-0 opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200/50 dark:hover:bg-[#333333] rounded transition-all"
                                                aria-label="Delete session"
                                            >
                                                <Trash2 className="w-3.5 h-3.5 text-gray-500 dark:text-gray-500" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })}

                    {filteredSessions.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-12 text-center">
                            <MessageSquare className="w-12 h-12 text-gray-300 dark:text-gray-700 mb-3" />
                            <p className="text-sm text-gray-500 dark:text-gray-500">
                                {searchQuery ? 'No sessions found' : 'No sessions yet'}
                            </p>
                        </div>
                    )}
                </div>
            )}

            {/* User Menu at Bottom */}
            <div className="p-4 border-t border-gray-200/30 dark:border-[#2a2a2a]/50">
                <UserMenu theme={theme} onThemeToggle={onThemeToggle} />
            </div>
        </aside>
    );
}
