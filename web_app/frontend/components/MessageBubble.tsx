import { User, Sparkles, ThumbsUp, ThumbsDown } from 'lucide-react';
import { useState } from 'react';

export type Mode = 'chat' | 'translate';
export type Theme = 'light' | 'dark';

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    translatedContent?: string;
    feedback?: 'good' | 'bad' | null;
}

interface MessageBubbleProps {
    message: Message;
    theme: Theme;
    mode: Mode;
    onFeedback?: (messageId: string, feedback: 'good' | 'bad') => void;
}

export function MessageBubble({ message, theme, mode, onFeedback }: MessageBubbleProps) {
    const isUser = message.role === 'user';
    const [localFeedback, setLocalFeedback] = useState<'good' | 'bad' | null>(message.feedback || null);

    const handleFeedback = (feedback: 'good' | 'bad') => {
        const newFeedback = localFeedback === feedback ? null : feedback;
        setLocalFeedback(newFeedback);
        if (onFeedback && newFeedback) {
            onFeedback(message.id, newFeedback);
        }
    };

    // Different colors for chat vs translate mode
    const getAssistantBgColor = () => {
        if (theme === 'dark') {
            return mode === 'translate'
                ? 'bg-[#1a2a35] border border-[#2a3f4f]'
                : 'bg-[#1f1f1f]';
        } else {
            return mode === 'translate'
                ? 'bg-blue-50/80 border border-blue-100'
                : 'bg-gray-100';
        }
    };

    return (
        <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {!isUser && (
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${theme === 'dark'
                    ? 'bg-gradient-to-br from-amber-700/20 to-amber-900/20'
                    : 'bg-gradient-to-br from-amber-100 to-amber-200'
                    }`}>
                    <Sparkles className={`w-4 h-4 ${theme === 'dark' ? 'text-amber-500' : 'text-amber-700'}`} />
                </div>
            )}

            <div className={`max-w-[70%] space-y-2`}>
                <div className={`p-4 rounded-2xl ${isUser
                    ? theme === 'dark'
                        ? 'bg-white text-gray-900'
                        : 'bg-gray-800 text-white'
                    : `${getAssistantBgColor()} ${theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}`
                    }`}>
                    <p className="whitespace-pre-wrap break-words">{message.content}</p>
                </div>

                {mode === 'translate' && message.translatedContent && !isUser && (
                    <div className={`p-3 rounded-xl border ${theme === 'dark'
                        ? 'bg-blue-950/30 border-blue-900/30'
                        : 'bg-blue-50 border-blue-100'
                        }`}>
                        <p className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                            {message.translatedContent}
                        </p>
                    </div>
                )}

                <div className="flex items-center gap-3">
                    <div className={`text-xs ${theme === 'dark' ? 'text-gray-600' : 'text-gray-500'} px-1`}>
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>

                    {!isUser && (
                        <div className="flex items-center gap-1">
                            <button
                                onClick={() => handleFeedback('good')}
                                className={`p-1 rounded transition-colors ${localFeedback === 'good'
                                    ? theme === 'dark'
                                        ? 'bg-green-900/30 text-green-500'
                                        : 'bg-green-100 text-green-700'
                                    : theme === 'dark'
                                        ? 'text-gray-600 hover:text-green-500 hover:bg-green-900/20'
                                        : 'text-gray-400 hover:text-green-600 hover:bg-green-50'
                                    }`}
                                aria-label="Good response"
                            >
                                <ThumbsUp className="w-3 h-3" />
                            </button>
                            <button
                                onClick={() => handleFeedback('bad')}
                                className={`p-1 rounded transition-colors ${localFeedback === 'bad'
                                    ? theme === 'dark'
                                        ? 'bg-red-900/30 text-red-500'
                                        : 'bg-red-100 text-red-700'
                                    : theme === 'dark'
                                        ? 'text-gray-600 hover:text-red-500 hover:bg-red-900/20'
                                        : 'text-gray-400 hover:text-red-600 hover:bg-red-50'
                                    }`}
                                aria-label="Bad response"
                            >
                                <ThumbsDown className="w-3 h-3" />
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {isUser && (
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-300'
                    }`}>
                    <User className={`w-4 h-4 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-700'}`} />
                </div>
            )}
        </div>
    );
}
