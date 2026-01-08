'use client'

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { SignupForm } from '@/components/SignupForm';
import { Theme } from '@/components/MessageBubble';

export default function SignupPage() {
    const router = useRouter();
    const { user, loading } = useAuth();
    const [theme, setTheme] = useState<Theme>('dark');

    // Check system/localStorage theme preference
    useEffect(() => {
        const savedTheme = localStorage.getItem('theme') as Theme;
        if (savedTheme) {
            setTheme(savedTheme);
        } else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
            setTheme('light');
        }
    }, []);

    // Redirect if already logged in
    useEffect(() => {
        if (!loading && user) {
            router.push('/');
        }
    }, [user, loading, router]);

    if (loading) {
        return (
            <div className={`min-h-screen flex items-center justify-center ${theme === 'dark' ? 'bg-[#121212]' : 'bg-gray-50'
                }`}>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
            </div>
        );
    }

    return (
        <div className={`min-h-screen flex items-center justify-center p-4 ${theme === 'dark' ? 'bg-[#121212]' : 'bg-gray-50'
            }`}>
            <div className="w-full max-w-md">
                {/* Logo and Title */}
                <div className="text-center mb-8">
                    <h1 className={`text-3xl font-bold mb-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'
                        }`}>
                        Join Runyoro
                    </h1>
                    <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
                        }`}>
                        Create your account to get started
                    </p>
                </div>

                {/* Signup Form */}
                <div className={`p-8 rounded-2xl shadow-xl ${theme === 'dark'
                    ? 'bg-[#1a1a1a] border border-[#2a2a2a]'
                    : 'bg-white border border-gray-200'
                    }`}>
                    <SignupForm theme={theme} />
                </div>
            </div>
        </div>
    );
}
