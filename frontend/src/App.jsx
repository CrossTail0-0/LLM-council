import React, { useState, useEffect } from 'react';
import QueryInput from './components/QueryInput';
import LoadingStages from './components/LoadingStages';
import TabView from './components/TabView';
import FinalResponse from './components/FinalResponse';
import { submitQuery, checkHealth } from './services/api';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    // Check API health on mount
    checkHealth()
      .then(data => setHealth(data))
      .catch(err => console.error('Health check failed:', err));
  }, []);

  const handleSubmitQuery = async (query) => {
    setIsLoading(true);
    setCurrentStage(1);
    setError(null);
    setResult(null);

    try {
      // Simulate stage progression for better UX
      const stageInterval = setInterval(() => {
        setCurrentStage(prev => {
          if (prev < 3) return prev + 1;
          return prev;
        });
      }, 3000);

      const data = await submitQuery(query);
      
      clearInterval(stageInterval);
      setCurrentStage(3);
      setResult(data);
      
    } catch (err) {
      console.error('Error submitting query:', err);
      setError(err.response?.data?.detail || 'Failed to process query. Please try again.');
    } finally {
      setIsLoading(false);
      setCurrentStage(0);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🏛️ LLM Council</h1>
        <p className="subtitle">Collective Intelligence from Multiple AI Models</p>
        {health && (
          <div className="health-status">
            <span className="status-indicator">●</span>
            {health.models_configured} models configured
          </div>
        )}
      </header>

      <main className="app-main">
        <QueryInput onSubmit={handleSubmitQuery} isLoading={isLoading} />

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {isLoading && <LoadingStages currentStage={currentStage} />}

        {result && (
          <div className="results-container">
            <FinalResponse 
              finalResponse={result.stage_3_final} 
              processingTime={result.processing_time}
            />
            
            <TabView responses={result.stage_1_responses} />
            
            {result.stage_2_reviews && result.stage_2_reviews.length > 0 && (
              <details className="reviews-section">
                <summary>View Cross-Review Rankings</summary>
                <div className="reviews-content">
                  {result.stage_2_reviews.map((review, idx) => (
                    <div key={idx} className="review-item">
                      <h4>Review by {review.reviewer_model.split('/').pop()}</h4>
                      <ul>
                        {review.rankings.map((ranking, ridx) => (
                          <li key={ridx}>
                            <strong>#{ranking.rank} - Response {ranking.response_id}:</strong> {ranking.reasoning}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by HuggingFace Router • GPT OSS Safeguard, Kimi K2, Llama 3.3</p>
      </footer>
    </div>
  );
}

export default App;