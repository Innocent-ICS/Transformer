'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/lib/api';
import { User, AuthContextType, SignupData, LoginData } from '@/lib/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Check auth status and load user on mount
    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const token_from_storage = localStorage.getItem('auth_token');
            if (token_from_storage) {
                setToken(token_from_storage);
                const currentUser = await apiClient.getCurrentUser();
                setUser(currentUser);
                setError(null);
            }
        } catch (err: any) {
            // Token is invalid or expired
            localStorage.removeItem('auth_token');
            setToken(null);
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const signup = async (data: SignupData) => {
        try {
            setLoading(true);
            setError(null);
            const response = await apiClient.signup(data);
            setUser(response.user);
            setToken(response.token);
        } catch (err: any) {
            setError(err.message || 'Signup failed');
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const login = async (data: LoginData) => {
        try {
            setLoading(true);
            setError(null);
            const response = await apiClient.login(data);
            setUser(response.user);
            setToken(response.token);
        } catch (err: any) {
            setError(err.message || 'Login failed');
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        setError(null);
        apiClient.logout().catch(() => {
            // Ignore logout errors, clear local state anyway
        });
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, error, signup, login, logout, checkAuth }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
