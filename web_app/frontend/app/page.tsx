'use client'

import { useState } from 'react';
import { Sidebar, Session } from '@/components/Sidebar';
import { ChatInterface } from '@/components/ChatInterface';
import { Mode, Theme, Message } from '@/components/MessageBubble';

export default function Home() {
  const [theme, setTheme] = useState<Theme>('dark');
  const [mode, setMode] = useState<Mode>('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const activeSession = sessions.find(s => s.id === activeSessionId);

  const createNewSession = (sessionMode: Mode = mode) => {
    const newSession: Session = {
      id: Date.now().toString(),
      title: sessionMode === 'chat' ? 'Mushandirapamwe Mutsva' : 'New Translation',
      mode: sessionMode,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setSessions([newSession, ...sessions]);
    setActiveSessionId(newSession.id);
    setMode(sessionMode);
  };

  const deleteSession = (sessionId: string) => {
    setSessions(sessions.filter(s => s.id !== sessionId));
    if (activeSessionId === sessionId) {
      setActiveSessionId(null);
    }
  };

  const updateSession = (sessionId: string, updates: Partial<Session>) => {
    setSessions(sessions.map(s => s.id === sessionId ? { ...s, ...updates, updatedAt: new Date() } : s));
  };

  const addMessage = (message: Message) => {
    if (!activeSessionId) return;

    const session = sessions.find(s => s.id === activeSessionId);
    if (!session) return;

    const updatedMessages = [...session.messages, message];

    // Auto-generate title from first message
    if (updatedMessages.length === 1 && message.role === 'user') {
      const title = message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '');
      updateSession(activeSessionId, { messages: updatedMessages, title });
    } else {
      updateSession(activeSessionId, { messages: updatedMessages });
    }
  };

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <div className={`h-screen flex overflow-hidden ${theme === 'dark' ? 'dark' : ''}`}>
      <div className="h-full w-full flex bg-white dark:bg-[#141414] text-gray-900 dark:text-gray-100 transition-colors duration-300">
        {isSidebarOpen && (
          <Sidebar
            sessions={sessions}
            activeSessionId={activeSession?.id}
            onSessionSelect={setActiveSessionId}
            onNewSession={createNewSession}
            onDeleteSession={deleteSession}
            isOpen={isSidebarOpen}
            theme={theme}
            currentMode={mode}
            onThemeToggle={toggleTheme}
            onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
          />
        )}
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="h-14 flex items-center justify-between px-6 bg-white dark:bg-[#1a1a1a] border-b border-gray-200/50 dark:border-[#2a2a2a]/50">
            <div className="flex items-center gap-4">
              <h1 className="font-medium text-gray-900 dark:text-white">
                Runyoro
              </h1>
            </div>
          </header>

          {/* Main Chat Interface */}
          <ChatInterface
            session={activeSession}
            mode={mode}
            theme={theme}
            onSendMessage={addMessage}
            onCreateSession={createNewSession}
            onModeChange={setMode}
          />
        </div>
      </div>
    </div>
  );
}
