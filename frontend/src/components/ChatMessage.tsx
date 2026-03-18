import React from 'react';
import type { Message } from '../types';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-header">
        <span className="role">{isUser ? '👤 你' : '🤖 AI'}</span>
        <span className="timestamp">
          {message.timestamp.toLocaleTimeString()}
        </span>
      </div>
      <div className="message-content">{message.content}</div>
    </div>
  );
};
