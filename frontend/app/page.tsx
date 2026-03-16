"use client";

import { useState, useRef, useEffect } from "react";
import ChatMessage from "@/components/ChatMessage";
import TypingIndicator from "@/components/TypingIndicator";
import PortfolioChart from "@/components/PortfolioChart";

type Message = { role: "user" | "assistant"; content: string };

const SUGGESTED = [
  "What is Apple's current stock price?",
  "Show me the latest CPI data",
  "What is the Fed Funds rate right now?",
  "Give me TSLA's risk metrics",
];

type Tab = "chat" | "portfolio";

export default function Home() {
  const [tab, setTab] = useState<Tab>("chat");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const ping = () => fetch(`${API_URL}/health`).catch(() => {});
    const id = setInterval(ping, 10 * 60 * 1000);
    return () => clearInterval(id);
  }, []);

  async function send(text: string) {
    if (!text.trim() || loading) return;

    const userMsg: Message = { role: "user", content: text };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: nextMessages }),
      });
      const data = await res.json();
      setMessages([...nextMessages, { role: "assistant", content: data.message ?? data.error }]);
    } catch {
      setMessages([...nextMessages, { role: "assistant", content: "Error: could not reach server." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", maxWidth: 800, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ padding: "16px 20px", borderBottom: "1px solid #e0e0e0", background: "#fff" }}>
        <h1 style={{ margin: 0, fontSize: 20, fontWeight: 600 }}>AI Finance Assistant</h1>
        <div style={{ display: "flex", gap: 4, marginTop: 10 }}>
          {(["chat", "portfolio"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                padding: "6px 16px",
                borderRadius: 6,
                border: "none",
                background: tab === t ? "#0070f3" : "#f0f0f0",
                color: tab === t ? "#fff" : "#555",
                fontWeight: tab === t ? 600 : 400,
                cursor: "pointer",
                fontSize: 13,
                textTransform: "capitalize",
              }}
            >
              {t === "chat" ? "Chat" : "Portfolio Chart"}
            </button>
          ))}
        </div>
      </div>

      {tab === "portfolio" && <PortfolioChart />}

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "20px 16px", display: tab === "chat" ? "block" : "none" }}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", marginTop: 60, color: "#888" }}>
            <p style={{ fontSize: 16 }}>Try asking something:</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center", marginTop: 12 }}>
              {SUGGESTED.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  style={{
                    padding: "8px 14px",
                    border: "1px solid #ddd",
                    borderRadius: 20,
                    background: "#fff",
                    cursor: "pointer",
                    fontSize: 13,
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <ChatMessage key={i} role={m.role} content={m.content} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input — chat only */}
      <div style={{ display: tab === "chat" ? "contents" : "none" }}>
      <div
        style={{
          padding: "12px 16px",
          borderTop: "1px solid #e0e0e0",
          background: "#fff",
          display: "flex",
          gap: 8,
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing && send(input)}
          placeholder="Ask about a stock, macro indicator..."
          disabled={loading}
          style={{
            flex: 1,
            padding: "10px 14px",
            borderRadius: 8,
            border: "1px solid #ddd",
            fontSize: 14,
            outline: "none",
          }}
        />
        <button
          onClick={() => send(input)}
          disabled={loading || !input.trim()}
          style={{
            padding: "10px 20px",
            borderRadius: 8,
            border: "none",
            background: "#0070f3",
            color: "#fff",
            fontSize: 14,
            cursor: "pointer",
            opacity: loading || !input.trim() ? 0.5 : 1,
          }}
        >
          Send
        </button>
      </div>
      </div>
    </div>
  );
}
