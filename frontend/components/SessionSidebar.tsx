"use client";

import { useEffect, useState } from "react";

type SessionItem = { id: string; title: string | null; created_at: string };

export default function SessionSidebar({
  currentSessionId,
  onSelect,
  onNew,
}: {
  currentSessionId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
}) {
  const [sessions, setSessions] = useState<SessionItem[]>([]);

  useEffect(() => {
    fetch("/api/sessions")
      .then((r) => r.json())
      .then(setSessions)
      .catch(() => {});
  }, [currentSessionId]);

  return (
    <div
      style={{
        width: 220,
        minWidth: 220,
        borderRight: "1px solid #e8e8e8",
        display: "flex",
        flexDirection: "column",
        background: "#fafafa",
        height: "100%",
        overflow: "hidden",
      }}
    >
      <div style={{ padding: "12px 10px 8px" }}>
        <button
          onClick={onNew}
          style={{
            width: "100%",
            padding: "8px 12px",
            borderRadius: 8,
            border: "1px solid #ddd",
            background: "#fff",
            cursor: "pointer",
            fontSize: 13,
            fontWeight: 600,
            color: "#333",
          }}
        >
          + New Chat
        </button>
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: "0 6px" }}>
        {sessions.map((s) => (
          <button
            key={s.id}
            onClick={() => onSelect(s.id)}
            style={{
              display: "block",
              width: "100%",
              textAlign: "left",
              padding: "8px 10px",
              border: "none",
              background: s.id === currentSessionId ? "#e8f0fe" : "transparent",
              cursor: "pointer",
              fontSize: 12,
              color: "#333",
              borderRadius: 6,
              marginBottom: 2,
              overflow: "hidden",
              whiteSpace: "nowrap",
              textOverflow: "ellipsis",
            }}
          >
            {s.title ?? "New conversation"}
          </button>
        ))}
      </div>
    </div>
  );
}
