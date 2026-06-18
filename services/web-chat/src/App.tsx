import { ChatPanel } from "./components/ChatPanel";

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm p-4 text-center">
        <h1 className="text-xl font-bold text-gray-800">解决方案专家 Agent</h1>
        <p className="text-sm text-gray-500">面向售前团队的自动化提案生成系统</p>
      </header>
      <ChatPanel />
    </div>
  );
}

export default App;