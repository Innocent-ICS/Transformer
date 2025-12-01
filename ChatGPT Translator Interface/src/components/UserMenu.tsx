import { useState, useRef, useEffect } from 'react';
import { User, Settings, LogOut, CreditCard, HelpCircle, Moon, Sun } from 'lucide-react';
import { Theme } from '../App';

interface UserMenuProps {
  theme: Theme;
  onThemeToggle: () => void;
}

export function UserMenu({ theme, onThemeToggle }: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const menuItems = [
    { icon: User, label: 'Profile', action: () => console.log('Profile') },
    { icon: Settings, label: 'Settings', action: () => console.log('Settings') },
    { icon: CreditCard, label: 'Subscription', action: () => console.log('Subscription') },
    { icon: theme === 'dark' ? Sun : Moon, label: `${theme === 'dark' ? 'Light' : 'Dark'} Mode`, action: onThemeToggle },
    { icon: HelpCircle, label: 'Help & Support', action: () => console.log('Help') },
    { icon: LogOut, label: 'Sign Out', action: () => console.log('Sign Out'), danger: true },
  ];

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
          theme === 'dark'
            ? 'hover:bg-gray-900/30 text-gray-300'
            : 'hover:bg-gray-200/30 text-gray-700'
        }`}
      >
        <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
          theme === 'dark'
            ? 'bg-gradient-to-br from-amber-600 to-amber-800'
            : 'bg-gradient-to-br from-amber-500 to-amber-700'
        }`}>
          <User className="w-4 h-4 text-white" />
        </div>
        <div className="flex-1 text-left min-w-0">
          <div className={`text-sm truncate ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            Takudzwa M.
          </div>
          <div className={`text-xs truncate ${theme === 'dark' ? 'text-gray-500' : 'text-gray-600'}`}>
            Pro Plan
          </div>
        </div>
      </button>

      {isOpen && (
        <div className={`absolute bottom-full left-0 right-0 mb-2 rounded-xl shadow-xl overflow-hidden z-50 border ${
          theme === 'dark'
            ? 'bg-gray-900 border-gray-800/50'
            : 'bg-white border-gray-200/50'
        }`}>
          <div className={`px-4 py-3 border-b ${
            theme === 'dark' ? 'border-gray-800/50' : 'border-gray-200/50'
          }`}>
            <p className={`text-sm ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
              Takudzwa Mutede
            </p>
            <p className={`text-xs ${theme === 'dark' ? 'text-gray-500' : 'text-gray-600'}`}>
              takudzwa@example.com
            </p>
            <div className={`mt-2 inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs ${
              theme === 'dark'
                ? 'bg-amber-700/20 text-amber-500'
                : 'bg-amber-50 text-amber-700'
            }`}>
              <span className="w-1.5 h-1.5 rounded-full bg-current" />
              Pro Plan
            </div>
          </div>

          <div className="py-1">
            {menuItems.map((item, index) => {
              const Icon = item.icon;
              return (
                <button
                  key={index}
                  onClick={() => {
                    item.action();
                    if (item.label !== `${theme === 'dark' ? 'Light' : 'Dark'} Mode`) {
                      setIsOpen(false);
                    }
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                    item.danger
                      ? theme === 'dark'
                        ? 'text-red-400 hover:bg-red-500/10'
                        : 'text-red-600 hover:bg-red-50'
                      : theme === 'dark'
                        ? 'text-gray-300 hover:bg-gray-800/50'
                        : 'text-gray-700 hover:bg-gray-100/50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}