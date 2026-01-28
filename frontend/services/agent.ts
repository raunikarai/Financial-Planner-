/**
 * API Service for communicating with the Financial Planner backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatResponse {
  reply: string;
}

/**
 * Send a message to the Financial Planner agent.
 * 
 * @param message - The user's message
 * @returns The agent's response string
 */
export async function sendMessage(message: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/agent/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  const data: ChatResponse = await response.json();
  return data.reply;
}
