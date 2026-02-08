import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import LoadingStages from './components/LoadingStages';
import { submitQuery, checkHealth } from './services/api';
import './App.css';

function App() {
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);
  const messagesEndRef = useRef(null);

  // Load conversation from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('llm-council-conversation');
    if (saved) {
      try {
        setConversation(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load conversation:', e);
      }
    }
  }, []);

  // Save conversation to localStorage whenever it changes
  useEffect(() => {
    if (conversation.length > 0) {
      localStorage.setItem('llm-council-conversation', JSON.stringify(conversation));
    }
  }, [conversation]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation, isLoading]);

  // Check API health on mount
  useEffect(() => {
    checkHealth()
      .then(data => setHealth(data))
      .catch(err => console.error('Health check failed:', err));
  }, []);

  const handleSendMessage = async (message) => {
    // Add user message to conversation
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    
    setConversation(prev => [...prev, userMessage]);
    setIsLoading(true);
    setCurrentStage(1);
    setError(null);

    try {
      // Simulate stage progression
      const stageInterval = setInterval(() => {
        setCurrentStage(prev => {
          if (prev < 3) return prev + 1;
          return prev;
        });
      }, 3000);

      const data = await submitQuery(message);
      
      clearInterval(stageInterval);
      setCurrentStage(3);

      // Add assistant response to conversation
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.stage_3_final.content,
        data: data, // Store full response data for details
        timestamp: new Date().toISOString()
      };

      setConversation(prev => [...prev, assistantMessage]);
      
    } catch (err) {
      console.error('Error submitting query:', err);
      setError(err.response?.data?.detail || 'Failed to process query. Please try again.');
      
      // Add error message to conversation
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `Sorry, I encountered an error: ${err.response?.data?.detail || 'Failed to process query'}`,
        timestamp: new Date().toISOString()
      };
      setConversation(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setCurrentStage(0);
    }
  };

  const handleClearConversation = () => {
    if (window.confirm('Are you sure you want to clear the conversation history?')) {
      setConversation([]);
      localStorage.removeItem('llm-council-conversation');
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <h1>🏛️ LLM Council</h1>
            <p className="subtitle">Collective Intelligence from Multiple AI Models</p>
          </div>
          <div className="header-right">
            {health && (
              <div className="health-status">
                <span className="status-indicator">●</span>
                {health.models_configured} models
              </div>
            )}
            {conversation.length > 0 && (
              <button className="clear-btn" onClick={handleClearConversation}>
                🗑️ Clear Chat
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="chat-container">
          {conversation.length === 0 && !isLoading && (
            <div className="welcome-screen">
              <div className="welcome-icon">🏛️</div>
              <h2>Welcome to the LLM Council</h2>
              <p>Ask a question and get insights from multiple AI models working together</p>
              <div className="example-questions">
                <p><strong>Try asking:</strong></p>
                <ul>
                  <li>"What is quantum computing?"</li>
                  <li>"How do I learn programming?"</li>
                  <li>"Explain blockchain in simple terms"</li>
                </ul>
              </div>
            </div>
          )}

          <div className="messages-list">
            {conversation.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            
            {isLoading && (
              <div className="loading-message">
                <LoadingStages currentStage={currentStage} />
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
      </main>

      <footer className="app-footer">
        <p>Powered by HuggingFace Router • GPT OSS Safeguard, Kimi K2, Llama 3.3</p>
      </footer>
    </div>
  );
}

export default App;