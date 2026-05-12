import Sidebar from './components/Sidebar'
import ChatTerminal from './components/ChatTerminal'
import { useAgentStream } from './hooks/useAgentStream'

function App() {
  const { messages, isStreaming, sendMessage } = useAgentStream();

  return (
    <div className="flex h-screen w-full bg-[var(--color-dark-surface)] overflow-hidden">
      {/* Background Graphic Effects */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
          <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[var(--color-accent-purple)]/10 blur-[120px] rounded-full" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-[var(--color-accent-blue)]/5 blur-[120px] rounded-full" />
      </div>

      <div className="z-10 flex w-full h-full">
         {/* Left Panel */}
         <Sidebar />
         
         {/* Center Main Chat Panel */}
         <div className="flex-1 flex justify-center">
            <ChatTerminal 
               messages={messages} 
               isStreaming={isStreaming} 
               onSendMessage={sendMessage} 
            />
         </div>
      </div>
    </div>
  )
}

export default App
