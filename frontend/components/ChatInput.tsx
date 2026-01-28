/**
 * ChatInput Component
 * Input box with send button for composing messages.
 */

import React, { useState, KeyboardEvent } from "react";
import styles from "@/styles/Chat.module.css";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    const trimmed = input.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setInput("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.inputContainer}>
      <input
        type="text"
        className={styles.input}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "Waiting for response..." : "Type a message..."}
        disabled={disabled}
        autoFocus
      />
      <button
        className={styles.sendButton}
        onClick={handleSend}
        disabled={disabled || !input.trim()}
      >
        {disabled ? (
          <span className={styles.spinner}>⏳</span>
        ) : (
          "Send"
        )}
      </button>
    </div>
  );
}
