/**
 * Main Chat Page
 * Entry point for the Financial Planner chat UI.
 */

"use client";

import React, { useState, useCallback } from "react";
import ChatWindow from "@/components/ChatWindow";
import ChatInput from "@/components/ChatInput";
import { Message } from "@/components/ChatMessage";
import { sendMessage } from "@/services/agent";
import styles from "@/styles/Chat.module.css";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateId = () => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const handleSend = useCallback(async (content: string) => {
    // Clear any previous error
    setError(null);

    // Add user message to chat
    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Set loading state
    setIsLoading(true);

    try {
      // Call the backend API
      const response = await sendMessage(content);

      // Add agent response to chat
      const agentMessage: Message = {
        id: generateId(),
        role: "agent",
        content: response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, agentMessage]);
    } catch (err) {
      console.error("Failed to send message:", err);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to connect to the server. Make sure the backend is running."
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  const dismissError = () => setError(null);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>💰 Financial Planner</h1>
      </header>

      <ChatWindow messages={messages} isLoading={isLoading} />

      {error && (
        <div className={styles.errorMessage}>
          <span>⚠️ {error}</span>
          <button className={styles.errorDismiss} onClick={dismissError}>
            ×
          </button>
        </div>
      )}

      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
