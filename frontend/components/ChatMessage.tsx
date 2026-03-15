import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Props = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatMessage({ role, content }: Props) {
  const isUser = role === "user";
  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: 12,
      }}
    >
      <div
        style={{
          maxWidth: "70%",
          padding: "10px 14px",
          borderRadius: 12,
          background: isUser ? "#0070f3" : "#fff",
          color: isUser ? "#fff" : "#111",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          lineHeight: 1.6,
        }}
      >
        {isUser ? (
          content
        ) : (
          <Markdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => <p style={{ margin: "0 0 8px" }}>{children}</p>,
              ul: ({ children }) => <ul style={{ margin: "0 0 8px", paddingLeft: 20 }}>{children}</ul>,
              ol: ({ children }) => <ol style={{ margin: "0 0 8px", paddingLeft: 20 }}>{children}</ol>,
              li: ({ children }) => <li style={{ marginBottom: 2 }}>{children}</li>,
              code: ({ children }) => (
                <code style={{ background: "#f0f0f0", padding: "1px 5px", borderRadius: 4, fontSize: 13 }}>
                  {children}
                </code>
              ),
              pre: ({ children }) => (
                <pre style={{ background: "#f0f0f0", padding: 10, borderRadius: 6, overflowX: "auto", fontSize: 13 }}>
                  {children}
                </pre>
              ),
              table: ({ children }) => (
                <div style={{ overflowX: "auto", margin: "0 0 8px" }}>
                  <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 13 }}>
                    {children}
                  </table>
                </div>
              ),
              thead: ({ children }) => (
                <thead style={{ background: "#f5f5f5" }}>{children}</thead>
              ),
              th: ({ children }) => (
                <th style={{ padding: "6px 12px", border: "1px solid #e0e0e0", textAlign: "left", fontWeight: 600 }}>
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td style={{ padding: "6px 12px", border: "1px solid #e0e0e0" }}>
                  {children}
                </td>
              ),
              tr: ({ children }) => (
                <tr style={{ borderBottom: "1px solid #e0e0e0" }}>{children}</tr>
              ),
            }}
          >
            {content}
          </Markdown>
        )}
      </div>
    </div>
  );
}
