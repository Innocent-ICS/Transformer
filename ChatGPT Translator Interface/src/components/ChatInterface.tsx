import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, ArrowRight } from 'lucide-react';
import { Session, Message, Mode, Theme, Metrics } from '../App';
import { MessageBubble } from './MessageBubble';
import { MetricsPanel } from './MetricsPanel';

interface ChatInterfaceProps {
  session: Session | undefined;
  mode: Mode;
  theme: Theme;
  onSendMessage: (message: Message) => void;
  onCreateSession: (mode: Mode) => void;
  onModeChange: (mode: Mode) => void;
}

export function ChatInterface({ session, mode, theme, onSendMessage, onCreateSession, onModeChange }: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [metrics, setMetrics] = useState<Metrics>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [session?.messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  const generateMockMetrics = (): Metrics => {
    return {
      wer: Math.random() * 0.15, // 0-15%
      cer: Math.random() * 0.1, // 0-10%
      bleuScore: 0.6 + Math.random() * 0.35, // 0.6-0.95
      perplexity: 10 + Math.random() * 40, // 10-50
      accuracy: 0.85 + Math.random() * 0.14, // 85-99%
    };
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Create session if none exists
    if (!session) {
      onCreateSession(mode);
      // Wait a bit for session to be created
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    onSendMessage(userMessage);
    setInput('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      let assistantContent = '';
      let translatedContent = '';

      if (mode === 'chat') {
        // Mock Shona AI response
        assistantContent = `Ndiri kunzwisisa mubvunzo wenyu. ${input.includes('hello') || input.includes('mhoro') 
          ? 'Mhoro! Ndakafara kukubatai. Ndingakubatsirei sei nhasi?' 
          : 'Ndiri pano kukubatsirai. Ndingakupa ruzivo rwakawanda pamusoro pemibvunzo yenyu.'}`;
      } else {
        // Mock translation
        const isEnglish = /^[a-zA-Z\s.,!?]+$/.test(input.trim());
        if (isEnglish) {
          assistantContent = 'Translation to Shona: ';
          translatedContent = input.toLowerCase().includes('hello') 
            ? 'Mhoro' 
            : `Shanduro yemazwi enyu muShona: ${input.substring(0, 30)}...`;
        } else {
          assistantContent = 'Translation to English: ';
          translatedContent = input.toLowerCase().includes('mhoro') 
            ? 'Hello' 
            : `Translation of your text in English: ${input.substring(0, 30)}...`;
        }
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: mode === 'translate' ? assistantContent + translatedContent : assistantContent,
        timestamp: new Date(),
        translatedContent: mode === 'translate' ? translatedContent : undefined,
      };

      onSendMessage(assistantMessage);
      setMetrics(generateMockMetrics());
      setIsLoading(false);
    }, 1000 + Math.random() * 1500);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const starterPrompts = mode === 'chat' 
    ? [
        'Ndipei ruzivo nezve tsika dzechiShona',
        'What are traditional Shona values?',
        'Ndingaita sei kuti ndive munhu akanaka?',
        'Tell me about Zimbabwean culture',
      ]
    : [
        'Hello, how are you?',
        'Mhoro, makadini?',
        'I would like to learn Shona',
        'Ndiri kuda kudzidza chiRungu',
      ];

  if (!session) {
    return (
      <div className="flex-1 flex items-center justify-center p-6 relative">
        {/* Graffiti/Pattern Background */}
        <div className={`absolute inset-0 opacity-[0.03] dark:opacity-[0.015] pointer-events-none ${
          theme === 'dark' ? 'mix-blend-lighten' : 'mix-blend-darken'
        }`} style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
        
        <div className="max-w-3xl w-full space-y-8 relative z-10">
          <div className="text-center space-y-4">
            <div className={`inline-flex p-4 rounded-full ${
              theme === 'dark' 
                ? 'bg-gradient-to-br from-amber-700/20 to-amber-900/20 shadow-lg shadow-amber-700/10' 
                : 'bg-gradient-to-br from-amber-50 to-amber-100'
            }`}>
              {mode === 'chat' ? (
                <Sparkles className={`w-8 h-8 ${theme === 'dark' ? 'text-amber-500' : 'text-amber-600'}`} />
              ) : (
                <ArrowRight className={`w-8 h-8 ${theme === 'dark' ? 'text-amber-500' : 'text-amber-600'}`} />
              )}
            </div>
            <h2 className={`${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
              {mode === 'chat' ? 'Start a conversation' : 'Translate between English and Shona'}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {mode === 'chat' 
                ? 'Chat with the AI in Shona or English' 
                : 'Enter text to translate between languages'}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {starterPrompts.map((prompt, index) => (
              <button
                key={index}
                onClick={() => {
                  onCreateSession(mode);
                  setInput(prompt);
                }}
                className={`p-4 rounded-xl text-left transition-all ${
                  theme === 'dark'
                    ? 'bg-gray-900 hover:bg-gray-800 border border-gray-800 hover:border-gray-700 text-gray-300 hover:shadow-lg hover:shadow-amber-700/10'
                    : 'bg-white hover:bg-gray-50 border border-gray-200 hover:border-gray-300 text-gray-700 shadow-sm hover:shadow-md'
                }`}
              >
                <span className="text-sm">{prompt}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Messages Area with graffiti background */}
      <div className="flex-1 overflow-y-auto relative bg-gradient-to-b from-transparent to-white/30 dark:to-[#0A0A0A]/30">
        {/* Graffiti/Pattern Background */}
        <div className={`absolute inset-0 opacity-[0.03] dark:opacity-[0.015] pointer-events-none ${
          theme === 'dark' ? 'mix-blend-lighten' : 'mix-blend-darken'
        }`} style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
        
        <div className="max-w-3xl mx-auto px-6 py-6 space-y-6 relative z-10">
          {session.messages.map((message) => (
            <MessageBubble key={message.id} message={message} theme={theme} mode={mode} />
          ))}
          {isLoading && (
            <div className="flex gap-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                theme === 'dark' ? 'bg-gray-800' : 'bg-gray-100'
              }`}>
                <Sparkles className={`w-4 h-4 ${theme === 'dark' ? 'text-amber-500' : 'text-amber-600'}`} />
              </div>
              <div className={`flex gap-1 p-4 rounded-2xl ${
                theme === 'dark' ? 'bg-gray-900' : 'bg-gray-100'
              }`}>
                <span className={`w-2 h-2 rounded-full animate-bounce ${
                  theme === 'dark' ? 'bg-gray-600' : 'bg-gray-400'
                }`} style={{ animationDelay: '0ms' }} />
                <span className={`w-2 h-2 rounded-full animate-bounce ${
                  theme === 'dark' ? 'bg-gray-600' : 'bg-gray-400'
                }`} style={{ animationDelay: '150ms' }} />
                <span className={`w-2 h-2 rounded-full animate-bounce ${
                  theme === 'dark' ? 'bg-gray-600' : 'bg-gray-400'
                }`} style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Metrics Panel */}
      {session.messages.length > 0 && (
        <MetricsPanel metrics={metrics} theme={theme} mode={mode} />
      )}

      {/* Input Area */}
      <div className="bg-gradient-to-t from-white via-white/95 to-white/80 dark:from-[#0A0A0A] dark:via-[#0A0A0A]/95 dark:to-[#0A0A0A]/80">
        <div className="max-w-3xl mx-auto px-6 py-4">
          <div className={`relative rounded-2xl overflow-visible ${
            theme === 'dark'
              ? 'bg-gray-900/50 border border-gray-800/50 focus-within:border-gray-700/50 shadow-lg focus-within:shadow-blue-500/10'
              : 'bg-gray-100/50 border border-gray-200/50 focus-within:border-gray-300/50 shadow-sm'
          } transition-all`}>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={mode === 'chat' ? 'Ask anything...' : 'Enter text to translate...'}
              rows={1}
              className={`w-full px-4 pt-3.5 pb-10 pr-12 bg-transparent resize-none focus:outline-none ${
                theme === 'dark' ? 'text-white placeholder:text-gray-500' : 'text-gray-900 placeholder:text-gray-500'
              }`}
              style={{ maxHeight: '200px' }}
            />
            
            {/* Mode Toggle - Subtle inline chips */}
            <div className="absolute left-4 bottom-3 flex items-center gap-2">
              <button
                onClick={() => onModeChange('chat')}
                className={`px-2.5 py-1 rounded-full text-xs transition-all ${
                  mode === 'chat'
                    ? theme === 'dark'
                      ? 'bg-amber-700/30 text-amber-500 border border-amber-600/40'
                      : 'bg-amber-600/15 text-amber-700 border border-amber-600/30'
                    : theme === 'dark'
                      ? 'text-gray-600 hover:text-gray-400 border border-transparent hover:border-gray-700/50'
                      : 'text-gray-500 hover:text-gray-700 border border-transparent hover:border-gray-300/50'
                }`}
              >
                Chat
              </button>
              <button
                onClick={() => onModeChange('translate')}
                className={`px-2.5 py-1 rounded-full text-xs transition-all ${
                  mode === 'translate'
                    ? theme === 'dark'
                      ? 'bg-amber-700/30 text-amber-500 border border-amber-600/40'
                      : 'bg-amber-600/15 text-amber-700 border border-amber-600/30'
                    : theme === 'dark'
                      ? 'text-gray-600 hover:text-gray-400 border border-transparent hover:border-gray-700/50'
                      : 'text-gray-500 hover:text-gray-700 border border-transparent hover:border-gray-300/50'
                }`}
              >
                Translate
              </button>
            </div>

            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className={`absolute right-2 bottom-2 p-2 rounded-lg transition-all ${
                input.trim() && !isLoading
                  ? theme === 'dark'
                    ? 'bg-white text-gray-900 hover:bg-gray-100 shadow-lg'
                    : 'bg-gray-900 text-white hover:bg-gray-800 shadow-md'
                  : theme === 'dark'
                    ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="mt-2 text-xs text-center text-gray-500 dark:text-gray-500">
            {mode === 'chat' 
              ? 'Shona AI can make mistakes. Verify important information.' 
              : 'Translations are generated by AI and may not be perfect.'}
          </p>
        </div>
      </div>
    </div>
  );
}