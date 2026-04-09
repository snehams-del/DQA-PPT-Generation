import { useState, useCallback } from "react";

export type Role = "user" | "assistant" | "system";

export interface Message {
  role: Role;
  content: string;
}

export function isSqlOrJson(text: string): boolean {
  const stripped = text.trim();
  const upper = stripped.toUpperCase();
  if (upper.startsWith("SELECT") || upper.startsWith("WITH") || upper.startsWith("INSERT") || upper.startsWith("UPDATE") || upper.startsWith("DELETE") || upper.startsWith("CREATE")) return true;
  if ((stripped.startsWith("{") && stripped.endsWith("}")) || (stripped.startsWith("[") && stripped.endsWith("]"))) {
     try {
         JSON.parse(stripped);
         return true;
     } catch(e) { return false; }
  }
  return false;
}

export function useAgentStream() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState<string>(() => `session_${Math.random().toString(36).substring(2, 11)}`);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;
    
    // Add User Message Optimistically
    setMessages(prev => [...prev, { role: "user", content: text }]);
    setIsStreaming(true);
    setError(null);
    
    // Create connection to the FastAPI stream endpoint
    try {
      // For SSE with POST we would typically use standard fetch and read the stream, 
      // since EventSource only handles GET. 
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          user_id: "default_user",
          session_id: sessionId
        })
      });

      if (!response.body) {
         throw new Error("No readable stream available");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      // Setup Assistant Message Placeholder
      setMessages(prev => [...prev, { role: "assistant", content: "" }]);
      
      let done = false;
      let streamedResponse = "";
      
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          // Parse SSE payload (chunk could contain multiple 'data: {...}\n\n' lines)
          const lines = chunk.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
               try {
                  const data = JSON.parse(line.slice(6));
                  if (data.error) {
                     setError(data.error);
                     continue;
                  }
                  
                  if (data.content) {
                      if (!isSqlOrJson(data.content)) {
                          streamedResponse = data.content;
                          // Update the last assistant message
                          setMessages(prev => {
                              const updated = [...prev];
                              updated[updated.length - 1] = { role: "assistant", content: streamedResponse };
                              return updated;
                          });
                      }
                  }
               } catch (e) {
                 // Ignore parsing errors for incomplete chunks
               }
            }
          }
        }
      }
    } catch (err: any) {
      setError(err.message || 'Stream connection failed.');
    } finally {
      setIsStreaming(false);
    }
  }, []);

  return { messages, isStreaming, error, sendMessage };
}
