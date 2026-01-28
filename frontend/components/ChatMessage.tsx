/**
 * ChatMessage Component
 * Renders a single message bubble for user or agent.
 */

import React from "react";
import styles from "@/styles/Chat.module.css";

export interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`${styles.messageContainer} ${
        isUser ? styles.userMessage : styles.agentMessage
      }`}
    >
      <div className={styles.messageHeader}>
        <span className={styles.messageRole}>
          {isUser ? "You" : "💰 Financial Planner"}
        </span>
        <span className={styles.messageTime}>
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
      <div className={styles.messageBubble}>
        <div className={styles.messageContent}>
          {(message.content || "").split("\n").map((line, index, arr) => (
            <React.Fragment key={index}>
              {line}
              {index < arr.length - 1 && <br />}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
