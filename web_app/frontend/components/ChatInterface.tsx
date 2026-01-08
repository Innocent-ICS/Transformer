'use client'

import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, ArrowRight, MoreVertical, Sliders } from 'lucide-react';
import { MessageBubble, Message, Mode, Theme } from './MessageBubble';
import { TranslationToggle } from './TranslationToggle';
import { SpeechToTextButton } from './SpeechToTextButton';
import { Session } from './Sidebar';
import { apiClient } from '@/lib/api';

interface ChatInterfaceProps {
    session: Session | undefined;
    mode: Mode;
    theme: Theme;
    onSendMessage: (message: Message) => void;
    onCreateSession: (mode: Mode) => void;
    onModeChange: (mode: Mode) => void;
}

type TranslationDirection = 'en-sn' | 'sn-en';

const SAMPLE_PAIRS = [
    { sn: 'Ndipei ruzivo nezve tsika dzechiShona', en: 'What are traditional Shona values?' },
    { sn: 'Ndingaita sei kuti ndive munhu akanaka?', en: 'Tell me about Zimbabwean culture' },
    { sn: 'Ko mhosva inorohwa sei muShona?', en: 'How is punishment handled in Shona culture?' },
    { sn: 'Ndiudze nezvetsika dzedu', en: 'Tell me about our traditions' }
];

export function ChatInterface({ session, mode, theme, onSendMessage, onCreateSession, onModeChange }: ChatInterfaceProps) {
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [translationDirection, setTranslationDirection] = useState<TranslationDirection>('en-sn');
    const [temperature, setTemperature] = useState(0.8);
    const [showSettings, setShowSettings] = useState(false);
    const [currentPairIndex, setCurrentPairIndex] = useState(0);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [session?.messages]);

    // Rotate starter prompts every 5 seconds
    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentPairIndex((prev) => (prev + 1) % SAMPLE_PAIRS.length);
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [input]);

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
        const currentInput = input.trim();
        setInput('');
        setIsLoading(true);

        try {
            let assistantContent = '';
            let translatedContent = '';
            let inferenceTime = 0;

            if (mode === 'chat') {
                // Use text generation for chat mode
                const result = await apiClient.generate({
                    prompt: currentInput,
                    model_id: 'shona-100K-final',
                    max_length: 100,
                    temperature: temperature
                });
                assistantContent = result.generated_text;
                inferenceTime = result.inference_time_ms;
            } else {
                // Use translation
                const result = await apiClient.translate({
                    text: currentInput,
                    model_id: 'translation-final',
                    max_length: 100
                });
                assistantContent = 'Translation: ';
                translatedContent = result.translation;
                inferenceTime = result.inference_time_ms;
            }

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: mode === 'translate' ? assistantContent + translatedContent : assistantContent,
                timestamp: new Date(),
                translatedContent: mode === 'translate' ? translatedContent : undefined,
            };

            onSendMessage(assistantMessage);
        } catch (error: any) {
            // Show error message
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: `Error: ${error.message || 'Failed to process request. Please try again.'}`,
                timestamp: new Date(),
            };
            onSendMessage(errorMessage);
        } finally {
            setIsLoading(false);
        }
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


                <div className="max-w-3xl w-full space-y-8 relative z-10">
                    <div className="text-center space-y-4">
                        <div className={`inline-flex p-4 rounded-full ${theme === 'dark'
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
                        {(mode === 'translate'
                            ? [SAMPLE_PAIRS[currentPairIndex].en, SAMPLE_PAIRS[currentPairIndex].sn, SAMPLE_PAIRS[(currentPairIndex + 1) % SAMPLE_PAIRS.length].en, SAMPLE_PAIRS[(currentPairIndex + 1) % SAMPLE_PAIRS.length].sn]
                            : ['Ndipei ruzivo nezve tsika dzechiShona', 'What are traditional Shona values?', 'Ndingaita sei kuti ndive munhu akanaka?', 'Tell me about Zimbabwean culture']
                        ).map((prompt, index) => (
                            <button
                                key={index}
                                onClick={() => {
                                    onCreateSession(mode);
                                    setInput(prompt);
                                }}
                                className={`p-4 rounded-xl text-left transition-all ${theme === 'dark'
                                    ? 'bg-[#1f1f1f] hover:bg-[#252525] border border-[#2a2a2a] hover:border-[#333333] text-gray-300 hover:shadow-lg hover:shadow-amber-700/10'
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
            {/* Messages Area with Afro Prime background */}
            <div
                className="flex-1 overflow-y-auto relative"
                style={{
                    backgroundImage: 'url(/Afro%20Prime.png)',
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    backgroundRepeat: 'no-repeat'
                }}
            >
                {/* Overlay to control opacity */}
                <div className="absolute inset-0 bg-white dark:bg-[#141414]" style={{ opacity: 0.8 }} />

                {/* Content with full opacity */}
                <div className="relative z-10 h-full">

                    <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
                        {session.messages.map((message) => (
                            <MessageBubble key={message.id} message={message} theme={theme} mode={mode} />
                        ))}
                        {isLoading && (
                            <div className="flex gap-3">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${theme === 'dark' ? 'bg-[#1f1f1f]' : 'bg-gray-100'
                                    }`}>
                                    <Sparkles className={`w-4 h-4 ${theme === 'dark' ? 'text-amber-500' : 'text-amber-600'}`} />
                                </div>
                                <div className={`flex gap-1 p-4 rounded-2xl ${theme === 'dark' ? 'bg-[#1f1f1f]' : 'bg-gray-100'
                                    }`}>
                                    <span className={`w-2 h-2 rounded-full animate-bounce ${theme === 'dark' ? 'bg-amber-500' : 'bg-gray-400'
                                        }`} style={{ animationDelay: '0ms' }} />
                                    <span className={`w-2 h-2 rounded-full animate-bounce ${theme === 'dark' ? 'bg-amber-500' : 'bg-gray-400'
                                        }`} style={{ animationDelay: '150ms' }} />
                                    <span className={`w-2 h-2 rounded-full animate-bounce ${theme === 'dark' ? 'bg-amber-500' : 'bg-gray-400'
                                        }`} style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                </div>
            </div>

            {/* Translation Toggle */}
            {mode === 'translate' && (
                <TranslationToggle
                    direction={translationDirection}
                    onToggle={() => setTranslationDirection(translationDirection === 'en-sn' ? 'sn-en' : 'en-sn')}
                    theme={theme}
                />
            )}

            {/* Input Area */}
            <div className="bg-gradient-to-t from-white via-white/95 to-white/80 dark:from-[#141414] dark:via-[#141414]/95 dark:to-[#141414]/80">
                <div className="max-w-3xl mx-auto px-6 py-4">
                    <div className={`relative rounded-2xl overflow-visible ${theme === 'dark'
                        ? 'bg-[#1f1f1f] border border-[#333333] focus-within:border-amber-600/50 shadow-lg'
                        : 'bg-white border border-gray-200 focus-within:border-amber-600/50 shadow-sm'
                        } transition-all`}>
                        <textarea
                            ref={textareaRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={mode === 'chat' ? 'Ask anything...' : 'Enter text to translate...'}
                            rows={1}
                            className={`w-full px-4 pt-3.5 pb-10 pr-12 bg-transparent resize-none focus:outline-none ${theme === 'dark' ? 'text-white placeholder:text-gray-500' : 'text-gray-900 placeholder:text-gray-500'
                                }`}
                            style={{ maxHeight: '200px' }}
                        />

                        {/* Mode Toggle and Speech Button - Subtle inline chips */}
                        <div className="absolute left-4 bottom-3 flex items-center gap-2">
                            <SpeechToTextButton
                                onTranscription={(text) => setInput(input + (input ? ' ' : '') + text)}
                                theme={theme}
                                disabled={isLoading}
                            />
                            <button
                                onClick={() => onModeChange('chat')}
                                className={`px-2.5 py-1 rounded-full text-xs transition-all ${mode === 'chat'
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
                                className={`px-2.5 py-1 rounded-full text-xs transition-all ${mode === 'translate'
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

                            {/* Settings Menu */}
                            <div className="relative ml-1">
                                <button
                                    onClick={() => setShowSettings(!showSettings)}
                                    className={`p-1.5 rounded-full text-xs transition-all ${theme === 'dark'
                                        ? 'text-gray-600 hover:text-gray-400 hover:bg-gray-800/50'
                                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200/50'
                                        }`}
                                    aria-label="Model settings"
                                >
                                    <MoreVertical className="w-3.5 h-3.5" />
                                </button>

                                {showSettings && (
                                    <div className={`absolute bottom-full left-0 mb-2 w-64 rounded-xl shadow-xl overflow-hidden z-50 border ${theme === 'dark'
                                        ? 'bg-gray-900 border-gray-800/50'
                                        : 'bg-white border-gray-200/50'
                                        }`}>
                                        <div className={`px-4 py-3 border-b ${theme === 'dark' ? 'border-gray-800/50' : 'border-gray-200/50'
                                            }`}>
                                            <div className="flex items-center gap-2">
                                                <Sliders className="w-4 h-4" />
                                                <span className={`text-sm font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                                                    Model Settings
                                                </span>
                                            </div>
                                        </div>

                                        <div className="p-4 space-y-4">
                                            <div>
                                                <label className={`text-xs ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'} mb-2 block`}>
                                                    Temperature: {temperature.toFixed(2)}
                                                </label>
                                                <input
                                                    type="range"
                                                    min="0.1"
                                                    max="1.5"
                                                    step="0.1"
                                                    value={temperature}
                                                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                                                    className="w-full h-2 rounded-lg appearance-none cursor-pointer"
                                                    style={{
                                                        background: theme === 'dark'
                                                            ? `linear-gradient(to right, rgb(245, 158, 11) 0%, rgb(245, 158, 11) ${((temperature - 0.1) / 1.4) * 100}%, rgb(31, 41, 55) ${((temperature - 0.1) / 1.4) * 100}%, rgb(31, 41, 55) 100%)`
                                                            : `linear-gradient(to right, rgb(217, 119, 6) 0%, rgb(217, 119, 6) ${((temperature - 0.1) / 1.4) * 100}%, rgb(229, 231, 235) ${((temperature - 0.1) / 1.4) * 100}%, rgb(229, 231, 235) 100%)`
                                                    }}
                                                />
                                                <div className="flex justify-between text-xs mt-1">
                                                    <span className={theme === 'dark' ? 'text-gray-600' : 'text-gray-500'}>Precise</span>
                                                    <span className={theme === 'dark' ? 'text-gray-600' : 'text-gray-500'}>Creative</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <button
                            onClick={handleSend}
                            disabled={!input.trim() || isLoading}
                            className={`absolute right-2 bottom-2 p-2 rounded-lg transition-all ${input.trim() && !isLoading
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
                            ? 'Runyoro can make mistakes. Verify important information.'
                            : 'Translations are generated by AI and may not be perfect.'}
                    </p>
                </div>
            </div>
        </div >
    );
}
