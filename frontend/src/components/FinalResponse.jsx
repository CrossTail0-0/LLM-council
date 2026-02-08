import React from 'react';

const FinalResponse = ({ finalResponse, processingTime }) => {
  if (!finalResponse) {
    return null;
  }

  return (
    <div className="final-response">
      <div className="final-response-header">
        <h2>Council's Final Answer</h2>
        <div className="metadata">
          <span className="chairman-badge">
            👨‍⚖️ Chairman: {finalResponse.chairman_model.split('/').pop().split(':')[0]}
          </span>
          {processingTime && (
            <span className="processing-time">
              ⏱️ {processingTime}s
            </span>
          )}
        </div>
      </div>
      
      <div className="final-content">
        {finalResponse.content}
      </div>
    </div>
  );
};

export default FinalResponse;