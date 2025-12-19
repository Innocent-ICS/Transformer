import { ArrowLeftRight } from 'lucide-react';
import { Theme } from './MessageBubble';

interface TranslationToggleProps {
    direction: 'en-sn' | 'sn-en';
    onToggle: () => void;
    theme: Theme;
}

export function TranslationToggle({ direction, onToggle, theme }: TranslationToggleProps) {
    return (
        <div className={`px-4 py-3 flex items-center justify-between ${theme === 'dark'
            ? 'bg-[#1a1a1a] border-t border-[#2a2a2a]'
            : 'bg-white border-t border-gray-200'
            }`}>
            <span className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
                }`}>
                Translation Direction
            </span>
            <button
                onClick={onToggle}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all ${theme === 'dark'
                    ? 'bg-[#1f1f1f] border border-[#333333] hover:border-amber-600/50 text-white'
                    : 'bg-white border border-gray-300 hover:border-amber-600/50 text-gray-900'
                    }`}
            >
                <span className="text-sm font-medium">
                    {direction === 'en-sn' ? 'English' : 'Shona'}
                </span>
                <ArrowLeftRight className="w-4 h-4" />
                <span className="text-sm font-medium">
                    {direction === 'en-sn' ? 'Shona' : 'English'}
                </span>
            </button>
        </div>
    );
}
