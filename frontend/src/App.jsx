import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Sparkles, Loader2, Play } from 'lucide-react';
import './App.css';

function App() {
  const [task, setTask] = useState('');
  const [history, setHistory] = useState([]);
  const [finalResult, setFinalResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [history, finalResult]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!task.trim()) return;

    setIsLoading(true);
    setHistory([{ agent: 'User', content: task }]);
    setFinalResult('');
    
    try {
      // Create a temporary history so the user sees something immediately
      const currentTask = task;
      setTask('');
      
      const response = await axios.post('http://localhost:8000/api/chat', {
        task: currentTask
      });

      setHistory(response.data.history);
      setFinalResult(response.data.final_result);
    } catch (error) {
      console.error("Error communicating with the backend agents:", error);
      setHistory(prev => [...prev, { agent: 'System', content: 'An error occurred while processing your request.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const getAgentIcon = (agentName) => {
    switch (agentName) {
      case 'User': return <User size={18} />;
      case 'FrontendAgent': return <Bot size={18} className="text-blue-500" />;
      case 'BackendAgent': return <Sparkles size={18} className="text-purple-500" />;
      default: return <Bot size={18} />;
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo-container">
          <div className="logo-icon"><Bot size={24} color="#fff" /></div>
          <h1>Agentic Flow</h1>
        </div>
        <p>Frontend & Backend Agent Collaboration</p>
      </header>

      <main className="main-content">
        <div className="chat-section">
          <div className="messages-container">
            {history.length === 0 && !isLoading && (
              <div className="empty-state">
                <Sparkles size={48} strokeWidth={1} />
                <h2>Start a Task</h2>
                <p>Give the agents a task, like "Create a short blog about AI in hiring."</p>
              </div>
            )}
            
            {history.map((msg, idx) => (
              <div key={idx} className={`message-wrapper ${msg.agent.toLowerCase()}`}>
                <div className="message-header">
                  {getAgentIcon(msg.agent)}
                  <span className="agent-name">
                    {msg.agent === 'User' ? 'You' : 
                     msg.agent === 'FrontendAgent' ? 'Frontend Agent' : 'Backend Agent'}
                  </span>
                </div>
                <div className="message-content">{msg.content}</div>
              </div>
            ))}
            
            {isLoading && (
              <div className="loading-indicator">
                <Loader2 size={24} className="spinner" />
                <span>Agents are communicating...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="input-form">
            <input
              type="text"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="e.g. Create a short blog about AI in hiring"
              disabled={isLoading}
              autoFocus
            />
            <button type="submit" disabled={isLoading || !task.trim()} className="send-btn">
              {isLoading ? <Loader2 size={20} className="spinner" /> : <Send size={20} />}
            </button>
          </form>
        </div>

        <div className={`result-section ${finalResult ? 'visible' : ''}`}>
          <div className="result-card">
            <div className="result-header">
              <Sparkles size={20} />
              <h2>Final Result</h2>
            </div>
            <div className="result-content">
              {finalResult ? (
                <div dangerouslySetInnerHTML={{ __html: finalResult.replace(/\n/g, '<br/>') }} />
              ) : (
                <div className="placeholder-text">
                  The final output will appear here once the agents complete the task.
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
