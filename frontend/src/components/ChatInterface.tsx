import React, { useState, useRef, useEffect } from 'react';
import { Send, Cloud } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { WordCloud } from './WordCloud';
import type { Message } from '../types';

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<Message | null>(null);
  const [selectedWords, setSelectedWords] = useState<string[]>([]);
  const [showWordCloud, setShowWordCloud] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const messageContent = selectedWords.length > 0
      ? `${input.trim()} [词云：${selectedWords.join(', ')}]`
      : input.trim();

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageContent,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const assistantMessageId = (Date.now() + 1).toString();
    
    setStreamingMessage({
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    });

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader');

      let accumulatedContent = '';
      let hasReceivedFirstChunk = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;

            try {
              const parsed = JSON.parse(data);
              if (parsed.chunk) {
                accumulatedContent += parsed.chunk;
                
                if (!hasReceivedFirstChunk) {
                  hasReceivedFirstChunk = true;
                }
                
                setStreamingMessage({
                  id: assistantMessageId,
                  role: 'assistant',
                  content: accumulatedContent,
                  timestamp: new Date(),
                });
              }
              if (parsed.error) {
                throw new Error(parsed.error);
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }

      if (accumulatedContent) {
        setMessages((prev) => [
          ...prev,
          {
            id: assistantMessageId,
            role: 'assistant',
            content: accumulatedContent,
            timestamp: new Date(),
          },
        ]);
        setStreamingMessage(null);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: assistantMessageId,
          role: 'assistant',
          content: '连接服务器失败，请确保后端服务已启动',
          timestamp: new Date(),
        },
      ]);
      setStreamingMessage(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>👻 Ghost Idea</h1>
        <p>AI 创意助手</p>
        <button
          className={`wordcloud-toggle ${showWordCloud ? 'active' : ''}`}
          onClick={() => setShowWordCloud(!showWordCloud)}
          title="词云"
        >
          <Cloud size={20} />
        </button>
      </div>

      <div className="chat-body">
        <div className={`messages-wrapper ${showWordCloud ? 'with-sidebar' : ''}`}>
          <div className="messages-container">
        {messages.length === 0 && !streamingMessage ? (
          <div className="welcome-message">
            <p>👋 你好！我是 Ghost Idea</p>
            <p>有什么创意想法想和我聊聊吗？</p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {streamingMessage && (
              <ChatMessage key={streamingMessage.id} message={streamingMessage} />
            )}
            {isLoading && !streamingMessage && (
              <div className="chat-message assistant">
                <div className="message-header">
                  <span className="role">🤖 AI</span>
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

        <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入你的想法..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          <Send size={20} />
        </button>
      </form>
        </div>

        {showWordCloud && (
          <div className="wordcloud-sidebar">
            <WordCloud onWordsSelected={setSelectedWords} />
          </div>
        )}
      </div>
    </div>
  );
};
