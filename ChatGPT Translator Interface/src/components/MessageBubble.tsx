import { User, Sparkles, ArrowRight } from 'lucide-react';
import { Message, Mode, Theme } from '../App';

interface MessageBubbleProps {
  message: Message;
  theme: Theme;
  mode: Mode;
}

export function MessageBubble({ message, theme, mode }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          theme === 'dark' 
            ? 'bg-gradient-to-br from-amber-700/20 to-amber-900/20' 
            : 'bg-gradient-to-br from-amber-50 to-amber-100'
        }`}>
          <Sparkles className={`w-4 h-4 ${theme === 'dark' ? 'text-amber-500' : 'text-amber-600'}`} />
        </div>
      )}

      <div className={`max-w-[70%] space-y-2`}>
        <div className={`p-4 rounded-2xl ${
          isUser
            ? theme === 'dark'
              ? 'bg-white text-gray-900'
              : 'bg-gray-900 text-white'
            : theme === 'dark'
              ? 'bg-gray-900 text-gray-100'
              : 'bg-gray-100 text-gray-900'
        }`}>
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>

        {mode === 'translate' && message.translatedContent && !isUser && (
          <div className={`p-3 rounded-xl border ${
            theme === 'dark'
              ? 'bg-gray-900/50 border-gray-800'
              : 'bg-white border-gray-200'
          }`}>
            <p className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              {message.translatedContent}
            </p>
          </div>
        )}

        <div className={`text-xs ${theme === 'dark' ? 'text-gray-600' : 'text-gray-500'} px-1`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>

      {isUser && (
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          theme === 'dark' ? 'bg-gray-800' : 'bg-gray-200'
        }`}>
          <User className={`w-4 h-4 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`} />
        </div>
      )}
    </div>
  );
}