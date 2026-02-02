/**
 * API Service for communicating with the Financial Planner backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Token storage key
const TOKEN_KEY = "financial_planner_token";

export interface ChatResponse {
  reply: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
  message: string;
}

/**
 * Get the stored auth token.
 */
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Set the auth token.
 */
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Clear the auth token (logout).
 */
export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}

/**
 * Login with email and password.
 */
export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Login failed: ${response.status} ${response.statusText}`);
  }

  const data: LoginResponse = await response.json();
  setToken(data.access_token);
  return data;
}

/**
 * Register a new user.
 */
export async function register(email: string, password: string): Promise<RegisterResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Registration failed: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Logout the current user.
 */
export function logout(): void {
  clearToken();
}

/**
 * Send a message to the Financial Planner agent.
 * 
 * @param message - The user's message
 * @returns The agent's response string
 */
export async function sendMessage(message: string): Promise<string> {
  const token = getToken();
  
  if (!token) {
    throw new Error("Not authenticated. Please login first.");
  }

  const response = await fetch(`${API_BASE_URL}/agent/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({ message }),
  });

  if (response.status === 401) {
    clearToken();
    throw new Error("Session expired. Please login again.");
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  const data: ChatResponse = await response.json();
  return data.reply;
}
