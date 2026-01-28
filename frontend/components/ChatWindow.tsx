/**
 * ChatWindow Component
 * Renders the scrollable list of chat messages.
 */

import React, { useEffect, useRef } from "react";
import ChatMessage, { Message } from "./ChatMessage";
import styles from "@/styles/Chat.module.css";

interface ChatWindowProps {
  messages: Message[];
  isLoading?: boolean;
}

export default function ChatWindow({ messages, isLoading = false }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className={styles.chatWindow}>
      {messages.length === 0 ? (
        <div className={styles.welcomeMessage}>
          <h2>💰 Financial Planner</h2>
          <p>Welcome! I can help you with:</p>
          <ul>
            <li>📊 Budget planning and tracking</li>
            <li>💸 Expense management</li>
            <li>📈 Investment strategies</li>
            <li>🎯 Financial goal setting</li>
          </ul>
          <p>Start by telling me your monthly income!</p>
        </div>
      ) : (
        messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))
      )}
      
      {isLoading && (
        <div className={styles.loadingIndicator}>
          <span className={styles.typingDots}>
            <span>.</span><span>.</span><span>.</span>
          </span>
          <span>Financial Planner is thinking...</span>
        </div>
      )}
      
      <div ref={bottomRef} />
    </div>
  );
}
