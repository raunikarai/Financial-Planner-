/**
 * Main Chat Page
 * Entry point for the Financial Planner chat UI.
 */

"use client";

import React, { useState, useCallback, useEffect } from "react";
import ChatWindow from "@/components/ChatWindow";
import ChatInput from "@/components/ChatInput";
import LoginForm from "@/components/LoginForm";
import { Message } from "@/components/ChatMessage";
import { sendMessage, isAuthenticated, logout } from "@/services/agent";
import styles from "@/styles/Chat.module.css";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);

  // Check authentication status on mount
  useEffect(() => {
    setIsLoggedIn(isAuthenticated());
    setCheckingAuth(false);
  }, []);

  const generateId = () => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    setMessages([]);
    setError(null);
  };

  const handleLogout = () => {
    logout();
    setIsLoggedIn(false);
    setMessages([]);
    setError(null);
  };

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
      const errorMessage = err instanceof Error ? err.message : "Failed to connect to the server.";
      
      // Check if it's an auth error
      if (errorMessage.includes("Session expired") || errorMessage.includes("Not authenticated")) {
        setIsLoggedIn(false);
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const dismissError = () => setError(null);

  // Show loading while checking auth
  if (checkingAuth) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>Loading...</div>
      </div>
    );
  }

  // Show login form if not authenticated
  if (!isLoggedIn) {
    return <LoginForm onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>💰 Financial Planner</h1>
        <button onClick={handleLogout} className={styles.logoutButton}>
          Logout
        </button>
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
