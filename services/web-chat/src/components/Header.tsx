import { Bot, User } from 'lucide-react';

export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-[#1a1a2e]/95 backdrop-blur-sm border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#e94560] to-[#0f3460] flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">解决方案专家 Agent</h1>
            <p className="text-xs text-white/50">Solution Expert Agent Console</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-sm text-white font-medium">售前顾问</p>
            <p className="text-xs text-white/40">在线</p>
          </div>
          <div className="w-9 h-9 rounded-full bg-[#0f3460] flex items-center justify-center">
            <User className="w-5 h-5 text-white/70" />
          </div>
        </div>
      </div>
    </header>
  );
}
