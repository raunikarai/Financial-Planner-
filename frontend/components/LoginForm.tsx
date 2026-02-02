/**
 * LoginForm Component
 * Handles user login and registration.
 */

"use client";

import React, { useState } from "react";
import { login, register } from "@/services/agent";
import styles from "@/styles/Chat.module.css";

interface LoginFormProps {
  onLoginSuccess: () => void;
}

export default function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
        onLoginSuccess();
      } else {
        await register(email, password);
        setSuccessMessage("Registration successful! Please login.");
        setIsLogin(true);
        setPassword("");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginBox}>
        <h2>💰 Financial Planner</h2>
        <p className={styles.loginSubtitle}>
          {isLogin ? "Sign in to your account" : "Create a new account"}
        </p>

        {error && <div className={styles.loginError}>{error}</div>}
        {successMessage && <div className={styles.loginSuccess}>{successMessage}</div>}

        <form onSubmit={handleSubmit} className={styles.loginForm}>
          <div className={styles.formGroup}>
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              disabled={isLoading}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              disabled={isLoading}
              minLength={6}
            />
          </div>

          <button type="submit" className={styles.loginButton} disabled={isLoading}>
            {isLoading ? "Please wait..." : isLogin ? "Sign In" : "Register"}
          </button>
        </form>

        <p className={styles.loginToggle}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError(null);
              setSuccessMessage(null);
            }}
            className={styles.linkButton}
          >
            {isLogin ? "Register" : "Sign In"}
          </button>
        </p>
      </div>
    </div>
  );
}
