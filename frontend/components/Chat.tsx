'use client';

import { useState, useRef, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Also scroll when loading state changes (for streaming updates)
  useEffect(() => {
    if (isLoading) {
      scrollToBottom();
    }
  }, [isLoading]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Create a placeholder for the streaming response
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

    try {
      // Call our Next.js API route which uses the Anthropic SDK server-side
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `API error: ${response.status} ${response.statusText}`);
      }

      // Handle streaming response from our API route
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';

      if (!reader) {
        throw new Error('No response body reader available');
      }

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (!line.trim() || !line.startsWith('data: ')) continue;
            
            const data = line.slice(6).trim();
            if (data === '[DONE]') {
              break;
            }

            try {
              const parsed = JSON.parse(data);
              
              if (parsed.type === 'content_block_delta' && parsed.delta?.type === 'text_delta') {
                accumulatedText += parsed.delta.text;
                // Update the last message (assistant's response) with accumulated text
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastIndex = newMessages.length - 1;
                  if (lastIndex >= 0 && newMessages[lastIndex].role === 'assistant') {
                    newMessages[lastIndex] = {
                      ...newMessages[lastIndex],
                      content: accumulatedText,
                    };
                  }
                  return newMessages;
                });
              }
            } catch (parseError) {
              // Skip invalid JSON lines
              continue;
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error: unknown) {
      console.error('Error sending message:', error);
      // Remove the empty assistant message and add error message
      setMessages((prev) => {
        // Check if the last message is an empty assistant message
        const lastMessage = prev[prev.length - 1];
        const newMessages = lastMessage?.role === 'assistant' && lastMessage?.content === '' 
          ? prev.slice(0, -1) 
          : prev;
        
        // Get error message
        let errorMessage = 'Sorry, there was an error connecting to Claude.';
        if (error instanceof Error) {
          if (error.message.includes('API key') || error.message.includes('not set')) {
            errorMessage = 'Sorry, there was an error connecting to Claude. Please check your API key in .env.local file (use NEXT_PUBLIC_CLAUDE_API).';
          } else {
            errorMessage = `Sorry, there was an error: ${error.message}`;
          }
        }
        
        newMessages.push({
          role: 'assistant',
          content: errorMessage,
        });
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-3xl w-full mx-auto">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 mb-4">
        {messages.length === 0 ? (
          <div className="text-center text-zinc-500 py-8">
            <p className="text-lg font-medium mb-2">Start a conversation</p>
            <p className="text-sm">Ask me about research collaboration, finding researchers, or anything else!</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-zinc-100 text-zinc-900'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-zinc-100 rounded-lg px-4 py-2">
              <LoadingSpinner />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={sendMessage} className="border-t border-zinc-200 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 rounded-lg border border-zinc-300 bg-white text-zinc-900 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-400 disabled:cursor-not-allowed text-white font-medium transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

