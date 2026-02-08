import React, { useState } from 'react';

const QueryInput = ({ onSubmit, isLoading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
    }
  };

  return (
    <div className="query-input-container">
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask your question to the LLM Council..."
            disabled={isLoading}
            rows={4}
            className="query-textarea"
          />
        </div>
        <button 
          type="submit" 
          disabled={isLoading || !query.trim()}
          className="submit-button"
        >
          {isLoading ? 'Processing...' : 'Submit to Council'}
        </button>
      </form>
    </div>
  );
};

export default QueryInput;