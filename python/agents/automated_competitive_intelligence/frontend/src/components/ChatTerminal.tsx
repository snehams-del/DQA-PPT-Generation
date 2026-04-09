import { useState, useRef, useEffect } from "react";
import type { Message } from "../hooks/useAgentStream";
import { Send, Bot, User, Loader2, Download } from "lucide-react";
import { motion } from "framer-motion";
import { clsx } from "clsx";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
interface Props {
  messages: Message[];
  isStreaming: boolean;
  onSendMessage: (msg: string) => void;
}

export default function ChatTerminal({ messages, isStreaming, onSendMessage }: Props) {
  const [input, setInput] = useState("");
  const autoScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScrollRef.current) {
      autoScrollRef.current.scrollTop = autoScrollRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    onSendMessage(input);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full mx-4 py-4 max-w-4xl w-full xl:mx-auto">
      <div className="w-full pt-4"></div>

      <div 
        ref={autoScrollRef}
        className="flex-1 overflow-y-auto pr-4 mb-4 flex flex-col gap-6"
      >
        {messages.length === 0 ? (
          <div className="m-auto text-center text-white/30 p-8 glass-panel rounded-2xl w-full max-w-sm">
            <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Initiate a query to target competitors.</p>
          </div>
        ) : (
          messages.map((msg, i) => (
             <motion.div 
               initial={{ opacity: 0, y: 10 }}
               animate={{ opacity: 1, y: 0 }}
               key={i} 
               className={clsx(
                 "flex w-full gap-4", 
                 msg.role === "user" ? "justify-end" : "justify-start"
               )}
             >
                {msg.role === "assistant" && (
                   <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[var(--color-accent-purple)] to-[var(--color-accent-blue)] flex items-center justify-center shrink-0 mt-1">
                      <Bot className="w-4 h-4 text-white" />
                   </div>
                )}
                
                <div className={clsx(
                  "px-5 py-3.5 rounded-2xl max-w-[85%] leading-relaxed text-[15px] shadow-lg",
                  msg.role === "user" 
                    ? "bg-white/10 text-white rounded-br-sm border border-white/5" 
                    : "glass-panel text-white/90 rounded-tl-sm"
                )}>
                  {msg.role === "assistant" && msg.content === "" && isStreaming ? (
                    <div className="flex gap-1.5 items-center h-5">
                       <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1.4 }} className="w-2 h-2 rounded-full bg-[var(--color-accent-blue)]" />
                       <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1.4, delay: 0.2 }} className="w-2 h-2 rounded-full bg-[var(--color-accent-blue)]" />
                       <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1.4, delay: 0.4 }} className="w-2 h-2 rounded-full bg-[var(--color-accent-blue)]" />
                    </div>
                  ) : (
                    <div className="custom-prose w-full overflow-hidden">
                      <ReactMarkdown
                         remarkPlugins={[remarkGfm]}
                         components={{
                         table: ({node, ...props}) => <div className="overflow-x-auto my-3"><table className="w-full text-sm text-left border-collapse bg-white/[0.02] border border-white/10 rounded-lg overflow-hidden" {...props} /></div>,
                         thead: ({node, ...props}) => <thead className="text-xs uppercase bg-white/5 border-b border-white/10 text-white/60" {...props} />,
                         th: ({node, ...props}) => <th className="px-4 py-3 font-medium border-x border-white/5 first:border-l-0 last:border-r-0" {...props} />,
                         td: ({node, ...props}) => <td className="px-4 py-3 border-b border-x border-white/5 text-white/80 first:border-l-0 last:border-r-0" {...props} />,
                         tr: ({node, ...props}) => <tr className="hover:bg-white/[0.04] transition-colors" {...props} />,
                         p: ({node, ...props}) => <p className="whitespace-pre-wrap mb-2 last:mb-0" {...props} />,
                         ul: ({node, ...props}) => <ul className="list-disc list-outside ml-4 mb-2 space-y-1" {...props} />,
                         ol: ({node, ...props}) => <ol className="list-decimal list-outside ml-4 mb-2 space-y-1" {...props} />,
                         li: ({node, ...props}) => <li className="" {...props} />
                       }}
                    >
                      {msg.content}
                      </ReactMarkdown>
                      {msg.role === "assistant" && (i === messages.length - 1 ? !isStreaming : true) && 
                        msg.content.includes("|") && msg.content.replace(/ /g, "").includes("|-") && 
                        (msg.content.toLowerCase().includes("competitor") || msg.content.toLowerCase().includes("original entity") || msg.content.toLowerCase().includes("original product")) && (
                        <div className="mt-3 flex justify-start">
                           <button 
                             onClick={() => {
                               const lines = msg.content.split('\n').filter(line => line.trim().startsWith('|') && line.trim().endsWith('|'));
                               if (lines.length < 2) return;
                               let csvContent = "";
                               for (let j = 0; j < lines.length; j++) {
                                 const line = lines[j];
                                 if (j === 1 && line.replace(/[|\-:\s]/g, '').length === 0) continue;
                                 const cells = line.split('|').slice(1, -1).map(c => {
                                   const cleanText = c.trim()
                                       .replace(/<br\s*\/?>/gi, '\n')
                                       .replace(/<\/?[^>]+(>|$)/g, '')
                                       .replace(/\*\*/g, '')
                                       .replace(/__/g, '');
                                   return `"${cleanText.replace(/"/g, '""')}"`;
                                 });
                                 csvContent += cells.join(',') + "\n";
                               }
                               let productName = "PRODUCT";
                               try {
                                 const headerCells = lines[0].split('|').slice(1, -1).map(c => c.trim());
                                 if (headerCells.length > 1 && headerCells[1]) {
                                   const cleanName = headerCells[1].replace(/[^a-zA-Z0-9_\- ]/g, "");
                                   if (cleanName) {
                                     productName = cleanName.replace(/ /g, "_").toUpperCase();
                                   }
                                 }
                               } catch (e) {}

                               const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                               const url = URL.createObjectURL(blob);
                               const link = document.createElement('a');
                               link.href = url;
                               link.download = `${productName}_CompetitorComparison.csv`;
                               document.body.appendChild(link);
                               link.click();
                               document.body.removeChild(link);
                             }}
                             className="flex items-center gap-2 text-xs bg-[var(--color-accent-blue)]/20 hover:bg-[var(--color-accent-blue)]/30 text-[var(--color-accent-blue)] px-3 py-1.5 rounded-lg border border-[var(--color-accent-blue)]/20 transition-colors font-medium cursor-pointer"
                           >
                              <Download className="w-3.5 h-3.5" />
                              Download Comparison CSV
                           </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {msg.role === "user" && (
                   <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0 mt-1 border border-white/5">
                      <User className="w-4 h-4 text-white/70" />
                   </div>
                )}
             </motion.div>
          ))
        )}
      </div>

      <div className="relative mt-auto">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isStreaming}
            placeholder="Ask about competitors, strategies, or features..."
            className="w-full glass-panel border border-white/10 rounded-2xl py-4 pl-5 pr-14 text-white placeholder-white/40 focus:outline-none focus:border-[var(--color-accent-blue)]/50 focus:ring-1 focus:ring-[var(--color-accent-blue)]/50 transition-all disabled:opacity-50"
          />
          <button 
            type="submit" 
            disabled={isStreaming || !input.trim()}
            className="absolute right-2 p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white disabled:opacity-30 transition-colors"
          >
             {isStreaming ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </form>
      </div>
    </div>
  );
}
