"use client";

import { useState, useRef, useEffect } from "react";
import ChatMessage from "@/components/ChatMessage";
import TypingIndicator from "@/components/TypingIndicator";
import PortfolioChart from "@/components/PortfolioChart";
import SessionSidebar from "@/components/SessionSidebar";

type Message = { role: "user" | "assistant"; content: string };

const CATEGORIES = [
  {
    label: "Stocks",
    icon: "📈",
    prompts: [
      { text: "Analyze TSMC's financial statements", display: "Analyze TSMC financials" },
      { text: "Compare AAPL, MSFT, and GOOGL", display: "Compare AAPL · MSFT · GOOGL" },
    ],
  },
  {
    label: "Macro",
    icon: "🌐",
    prompts: [
      { text: "Show me the latest CPI data", display: "Latest CPI data" },
      { text: "What is the Fed Funds rate right now?", display: "Fed Funds rate" },
    ],
  },
  {
    label: "Portfolio",
    icon: "📊",
    prompts: [
      { text: "Analyze my portfolio: AAPL 30%, NVDA 40%, MSFT 30%", display: "Analyze AAPL · NVDA · MSFT portfolio" },
      { text: "Give me TSLA's risk metrics", display: "TSLA risk metrics" },
    ],
  },
];

type Tab = "chat" | "portfolio";

export default function Home() {
  const [tab, setTab] = useState<Tab>("chat");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
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
        body: JSON.stringify({ messages: nextMessages, session_id: sessionId }),
      });
      const data = await res.json();
      if (data.session_id) setSessionId(data.session_id);
      setMessages([...nextMessages, { role: "assistant", content: data.message ?? data.error }]);
    } catch {
      setMessages([...nextMessages, { role: "assistant", content: "Error: could not reach server." }]);
    } finally {
      setLoading(false);
    }
  }

  async function loadSession(id: string) {
    setSessionId(id);
    setTab("chat");
    try {
      const res = await fetch(`/api/sessions/${id}/messages`);
      const data: Message[] = await res.json();
      setMessages(data);
    } catch {}
  }

  function newChat() {
    setSessionId(null);
    setMessages([]);
  }

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
      {/* Session sidebar */}
      <SessionSidebar
        currentSessionId={sessionId}
        onSelect={loadSession}
        onNew={newChat}
      />

      {/* Main area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        {/* Header */}
        <div style={{ padding: "16px 20px", borderBottom: "1px solid #e8e8e8", background: "#fff" }}>
          <h1 style={{ margin: 0, fontSize: 18, fontWeight: 700, letterSpacing: "-0.3px" }}>AI Finance Assistant</h1>
          <div style={{ display: "flex", gap: 4, marginTop: 10 }}>
            {(["chat", "portfolio"] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                style={{
                  padding: "5px 14px",
                  borderRadius: 6,
                  border: "none",
                  background: tab === t ? "#0070f3" : "#f0f0f0",
                  color: tab === t ? "#fff" : "#555",
                  fontWeight: tab === t ? 600 : 400,
                  cursor: "pointer",
                  fontSize: 13,
                }}
              >
                {t === "chat" ? "Chat" : "Portfolio Chart"}
              </button>
            ))}
          </div>
        </div>

        {/* Portfolio tab */}
        {tab === "portfolio" && <PortfolioChart />}

        {/* Chat tab */}
        <div style={{ flex: 1, overflowY: "auto", padding: "20px 16px", display: tab === "chat" ? "flex" : "none", flexDirection: "column" }}>

          {/* Empty state: hero + category cards */}
          {messages.length === 0 && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", paddingBottom: 40 }}>
              {/* Hero */}
              <div style={{ textAlign: "center", marginBottom: 36 }}>
                <p style={{ fontSize: 26, fontWeight: 700, margin: "0 0 8px", letterSpacing: "-0.5px" }}>
                  What would you like to know?
                </p>
                <p style={{ fontSize: 14, color: "#888", margin: 0, lineHeight: 1.6 }}>
                  Ask about stock quotes, earnings, CPI, interest rates, or portfolio risk.<br />
                  Powered by real-time data from Yahoo Finance and FRED.
                </p>
              </div>

              {/* Category cards */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
                {CATEGORIES.map((cat) => (
                  <div
                    key={cat.label}
                    style={{ background: "#fff", borderRadius: 12, border: "1px solid #e8e8e8", padding: "14px 16px", boxShadow: "0 1px 4px rgba(0,0,0,0.05)" }}
                  >
                    <div style={{ fontSize: 13, fontWeight: 600, color: "#444", marginBottom: 10, display: "flex", alignItems: "center", gap: 6 }}>
                      <span>{cat.icon}</span> {cat.label}
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                      {cat.prompts.map((p) => (
                        <button
                          key={p.text}
                          onClick={() => send(p.text)}
                          style={{
                            padding: "8px 10px",
                            borderRadius: 8,
                            border: "1px solid #ebebeb",
                            background: "#fafafa",
                            cursor: "pointer",
                            fontSize: 12,
                            color: "#333",
                            textAlign: "left",
                            lineHeight: 1.4,
                            transition: "background 0.15s",
                          }}
                          onMouseEnter={(e) => (e.currentTarget.style.background = "#f0f4ff")}
                          onMouseLeave={(e) => (e.currentTarget.style.background = "#fafafa")}
                        >
                          {p.display}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
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
              borderTop: "1px solid #e8e8e8",
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
    </div>
  );
}
