'use client'

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Theme } from './MessageBubble';
import Link from 'next/link';

interface SignupFormProps {
    theme: Theme;
}

export function SignupForm({ theme }: SignupFormProps) {
    const router = useRouter();
    const { signup } = useAuth();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const validatePassword = (pwd: string) => {
        if (pwd.length < 8) {
            return 'Password must be at least 8 characters';
        }
        if (!/[A-Z]/.test(pwd)) {
            return 'Password must contain an uppercase letter';
        }
        if (!/[0-9]/.test(pwd)) {
            return 'Password must contain a number';
        }
        return null;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Validation
        const passwordError = validatePassword(password);
        if (passwordError) {
            setError(passwordError);
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);

        try {
            await signup({ name, email, password });
            router.push('/');
        } catch (err: any) {
            setError(err.message || 'Signup failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md">
            <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                    <div className={`p-4 rounded-lg ${theme === 'dark'
                        ? 'bg-red-900/20 border border-red-800/50 text-red-400'
                        : 'bg-red-50 border border-red-200 text-red-700'
                        }`}>
                        <p className="text-sm">{error}</p>
                    </div>
                )}

                <div>
                    <label htmlFor="name" className={`block text-sm font-medium mb-2 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                        Name
                    </label>
                    <input
                        type="text"
                        id="name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                        className={`w-full px-4 py-3 rounded-lg transition-all ${theme === 'dark'
                            ? 'bg-[#1f1f1f] border border-[#333333] text-white placeholder:text-gray-500 focus:border-amber-600/50'
                            : 'bg-white border border-gray-200 text-gray-900 placeholder:text-gray-500 focus:border-amber-600/50'
                            } focus:outline-none focus:ring-1 focus:ring-amber-600/30`}
                        placeholder="Your name"
                        disabled={loading}
                    />
                </div>

                <div>
                    <label htmlFor="email" className={`block text-sm font-medium mb-2 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                        Email
                    </label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className={`w-full px-4 py-3 rounded-lg transition-all ${theme === 'dark'
                            ? 'bg-[#1f1f1f] border border-[#333333] text-white placeholder:text-gray-500 focus:border-amber-600/50'
                            : 'bg-white border border-gray-200 text-gray-900 placeholder:text-gray-500 focus:border-amber-600/50'
                            } focus:outline-none focus:ring-1 focus:ring-amber-600/30`}
                        placeholder="you@example.com"
                        disabled={loading}
                    />
                </div>

                <div>
                    <label htmlFor="password" className={`block text-sm font-medium mb-2 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                        Password
                    </label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        minLength={8}
                        className={`w-full px-4 py-3 rounded-lg transition-all ${theme === 'dark'
                            ? 'bg-[#1f1f1f] border border-[#333333] text-white placeholder:text-gray-500 focus:border-amber-600/50'
                            : 'bg-white border border-gray-200 text-gray-900 placeholder:text-gray-500 focus:border-amber-600/50'
                            } focus:outline-none focus:ring-1 focus:ring-amber-600/30`}
                        placeholder="At least 8 characters"
                        disabled={loading}
                    />
                    <p className={`mt-1 text-xs ${theme === 'dark' ? 'text-gray-500' : 'text-gray-600'}`}>
                        Must include uppercase letter and number
                    </p>
                </div>

                <div>
                    <label htmlFor="confirmPassword" className={`block text-sm font-medium mb-2 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                        Confirm Password
                    </label>
                    <input
                        type="password"
                        id="confirmPassword"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        minLength={8}
                        className={`w-full px-4 py-3 rounded-lg transition-all ${theme === 'dark'
                            ? 'bg-[#1f1f1f] border border-[#333333] text-white placeholder:text-gray-500 focus:border-amber-600/50'
                            : 'bg-white border border-gray-200 text-gray-900 placeholder:text-gray-500 focus:border-amber-600/50'
                            } focus:outline-none focus:ring-1 focus:ring-amber-600/30`}
                        placeholder="Confirm your password"
                        disabled={loading}
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className={`w-full px-6 py-3 rounded-lg font-medium transition-all ${loading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-amber-600 hover:bg-amber-700'
                        } text-white shadow-lg`}
                >
                    {loading ? 'Creating account...' : 'Create Account'}
                </button>

                <p className={`text-center text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
                    }`}>
                    Already have an account?{' '}
                    <Link
                        href="/login"
                        className="text-amber-600 hover:text-amber-700 font-medium"
                    >
                        Sign in
                    </Link>
                </p>
            </form>
        </div>
    );
}
