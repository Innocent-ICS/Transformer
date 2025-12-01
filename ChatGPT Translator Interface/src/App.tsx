import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { UserMenu } from './components/UserMenu';
import { Moon, Sun } from 'lucide-react';

export type Mode = 'chat' | 'translate';
export type Theme = 'light' | 'dark';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  translatedContent?: string;
}

export interface Session {
  id: string;
  title: string;
  mode: Mode;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Metrics {
  wer?: number;
  cer?: number;
  bleuScore?: number;
  perplexity?: number;
  accuracy?: number;
}

export default function App() {
  const [theme, setTheme] = useState<Theme>('dark');
  const [mode, setMode] = useState<Mode>('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState<Session[]>([
    {
      id: '1',
      title: 'Mhosva yaKudya kweZimbabwe',
      mode: 'chat',
      messages: [],
      createdAt: new Date(Date.now() - 86400000),
      updatedAt: new Date(Date.now() - 86400000),
    },
    {
      id: '2',
      title: 'Translation: Greetings',
      mode: 'translate',
      messages: [],
      createdAt: new Date(Date.now() - 172800000),
      updatedAt: new Date(Date.now() - 172800000),
    },
  ]);
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
      <div className="h-full w-full flex bg-white dark:bg-[#0A0A0A] text-gray-900 dark:text-gray-100 transition-colors duration-300">
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSessionSelect={setActiveSessionId}
          onNewSession={createNewSession}
          onDeleteSession={deleteSession}
          isOpen={isSidebarOpen}
          onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
          theme={theme}
          currentMode={mode}
          onThemeToggle={toggleTheme}
        />

        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="h-14 flex items-center justify-between px-6 bg-gradient-to-b from-white to-white/80 dark:from-[#0A0A0A] dark:to-[#0A0A0A]/80">
            <div className="flex items-center gap-4">
              <h1 className="font-medium text-gray-900 dark:text-white">
                Shona AI
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