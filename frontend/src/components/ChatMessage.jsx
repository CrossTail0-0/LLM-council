import React, { useState } from 'react';

const ChatMessage = ({ message }) => {
  const [showDetails, setShowDetails] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  if (message.type === 'user') {
    return (
      <div className="chat-message user-message">
        <div className="message-avatar user-avatar">You</div>
        <div className="message-content">
          <div className="message-text">{message.content}</div>
        </div>
      </div>
    );
  }

  if (message.type === 'assistant') {
    return (
      <div className="chat-message assistant-message">
        <div className="message-avatar assistant-avatar">🏛️</div>
        <div className="message-content">
          <div className="message-text">{message.content}</div>
          
          {message.data && (
            <div className="message-extras">
              <button 
                className="toggle-details-btn"
                onClick={() => setShowDetails(!showDetails)}
              >
                {showDetails ? '▼ Hide Details' : '▶ View Individual Responses & Rankings'}
              </button>

              {showDetails && (
                <div className="details-panel">
                  {/* Individual Responses */}
                  <div className="details-section">
                    <h4>Individual LLM Responses</h4>
                    <div className="tabs-mini">
                      {message.data.stage_1_responses.map((resp, idx) => (
                        <button
                          key={idx}
                          className={`tab-mini ${activeTab === idx ? 'active' : ''}`}
                          onClick={() => setActiveTab(idx)}
                        >
                          Model {resp.model_id}
                        </button>
                      ))}
                    </div>
                    <div className="tab-content-mini">
                      {message.data.stage_1_responses[activeTab] && (
                        <div className="response-detail">
                          <p className="model-name-small">
                            {message.data.stage_1_responses[activeTab].model_name.split('/').pop()}
                          </p>
                          <p className="response-text-small">
                            {message.data.stage_1_responses[activeTab].response}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Rankings */}
                  {message.data.stage_2_reviews && message.data.stage_2_reviews.length > 0 && (
                    <div className="details-section">
                      <h4>Cross-Review Rankings</h4>
                      {message.data.stage_2_reviews.map((review, idx) => (
                        <div key={idx} className="review-mini">
                          <p className="reviewer-name">
                            <strong>{review.reviewer_model.split('/').pop()}</strong>
                          </p>
                          <ul className="rankings-list">
                            {review.rankings.map((ranking, ridx) => (
                              <li key={ridx}>
                                <span className="rank-badge">#{ranking.rank}</span>
                                <span className="rank-id">Model {ranking.response_id}:</span>
                                <span className="rank-reason">{ranking.reasoning}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="processing-time-small">
                    ⏱️ Processed in {message.data.processing_time}s
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  return null;
};

export default ChatMessage;