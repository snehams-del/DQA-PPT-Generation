import { Target, Settings, LogOut, Plus } from 'lucide-react';

export default function Sidebar() {
   return (
      <div className="w-72 shrink-0 h-full flex flex-col border-r border-white/5 glass-panel py-5 px-3">
         {/* Brand */}
         <div className="flex items-center gap-3 px-3 mb-8">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--color-accent-purple)] to-[var(--color-accent-blue)] flex items-center justify-center">
               <Target className="w-4 h-4 text-white" />
            </div>
            <div>
               <h1 className="text-white font-bold leading-tight tracking-wide">Automated Competitive Intelligence</h1>
               {/* <p className="text-xs text-white/50">CI Engine</p> */}
            </div>
         </div>

         {/* Nav Actions */}
         <nav className="flex flex-col gap-2 mb-8 px-2">
            <button onClick={() => window.location.reload()} className="flex items-center gap-3 w-full px-3 py-2.5 text-sm rounded-lg text-white bg-gradient-to-r from-[var(--color-accent-purple)]/40 to-transparent hover:from-[var(--color-accent-purple)]/60 transition-colors border border-[var(--color-accent-purple)]/30 shadow-sm">
               <Plus className="w-4 h-4 text-[var(--color-accent-blue)] shrink-0" />
               <span className="font-semibold tracking-wide">New Chat Session</span>
            </button>
         </nav>

         {/* About App */}
         <div className="px-4 mb-3 flex-1 overflow-y-auto pr-2 custom-scrollbar">
            <h3 className="text-sm font-semibold text-white/90 mb-3 uppercase tracking-wider">About This App</h3>
            <p className="text-sm text-white/80 mb-5 leading-relaxed">
               I am your dedicated <strong>Competitive Intelligence Analyst</strong>.
            </p>

            <p className="text-xs text-white/60 mb-3 leading-relaxed">
               My purpose is to help you analyze entities across any industry by following a structured, multi-step process:
            </p>

            <div className="text-xs text-white/50 space-y-4 leading-relaxed">
               <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                  <strong className="text-white/80 block mb-1">1. Find Source Documents</strong>
                  I can search our database for source document URLs based on an entity name or unique identifier.
               </div>

               <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                  <strong className="text-white/80 block mb-1">2. Extract & Analyze</strong>
                  With your approval, I will dynamically extract key intelligence attributes from a document and perform a web search to find and compare market competitors.
               </div>

               <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                  <strong className="text-white/80 block mb-1">3. Summarize</strong>
                  Finally, if you ask, I can generate a concise summary of the entire analysis.
               </div>
            </div>
         </div>

         {/* Bottom Settings */}
         <div className="mt-auto flex flex-col gap-2 px-2 pt-4 border-t border-white/5">
            <button className="flex items-center gap-3 w-full px-3 py-2 text-sm rounded-lg text-white/60 hover:bg-white/5 transition-colors">
               <Settings className="w-4 h-4" />
               <span className="font-medium">Settings</span>
            </button>
            <button className="flex items-center gap-3 w-full px-3 py-2 text-sm rounded-lg text-white/60 hover:bg-white/5 transition-colors">
               <LogOut className="w-4 h-4" />
               <span className="font-medium">Logout</span>
            </button>
         </div>
      </div>
   );
}
