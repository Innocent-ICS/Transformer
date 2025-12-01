'use client'

import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Loader } from 'lucide-react';

interface SpeechToTextButtonProps {
    onTranscription: (text: string) => void;
    theme: 'light' | 'dark';
    disabled?: boolean;
}

export function SpeechToTextButton({ onTranscription, theme, disabled = false }: SpeechToTextButtonProps) {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    useEffect(() => {
        // Cleanup on unmount
        return () => {
            if (mediaRecorderRef.current && isRecording) {
                mediaRecorderRef.current.stop();
            }
        };
    }, [isRecording]);

    const startRecording = async () => {
        try {
            setError(null);
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm'
            });

            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                stream.getTracks().forEach(track => track.stop());

                await sendAudioToBackend(audioBlob);
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (err: any) {
            setError(err.message || 'Failed to access microphone');
            console.error('Microphone error:', err);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const sendAudioToBackend = async (audioBlob: Blob) => {
        setIsProcessing(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            const response = await fetch('http://localhost:8000/api/transcribe', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.transcription) {
                onTranscription(data.transcription);
            } else {
                throw new Error('No transcription returned');
            }
        } catch (err: any) {
            setError(err.message || 'Transcription failed');
            console.error('Transcription error:', err);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleClick = () => {
        if (disabled || isProcessing) return;

        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    return (
        <div className="relative">
            <button
                onClick={handleClick}
                disabled={disabled || isProcessing}
                className={`p-2 rounded-lg transition-all ${isRecording
                        ? theme === 'dark'
                            ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse'
                            : 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                        : isProcessing
                            ? theme === 'dark'
                                ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
                                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                            : disabled
                                ? theme === 'dark'
                                    ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
                                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                : theme === 'dark'
                                    ? 'bg-gray-800 hover:bg-gray-700 text-gray-300'
                                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    }`}
                title={isRecording ? 'Click to stop recording' : 'Click to start recording'}
            >
                {isProcessing ? (
                    <Loader className="w-4 h-4 animate-spin" />
                ) : isRecording ? (
                    <MicOff className="w-4 h-4" />
                ) : (
                    <Mic className="w-4 h-4" />
                )}
            </button>

            {error && (
                <div className={`absolute bottom-full mb-2 right-0 px-3 py-2 rounded-lg text-xs whitespace-nowrap ${theme === 'dark' ? 'bg-red-900/80 text-red-200' : 'bg-red-100 text-red-800'
                    }`}>
                    {error}
                </div>
            )}
        </div>
    );
}
