import React, { useState } from 'react';

const TabView = ({ responses }) => {
  const [activeTab, setActiveTab] = useState(0);

  if (!responses || responses.length === 0) {
    return null;
  }

  return (
    <div className="tab-view">
      <h3>Individual LLM Responses</h3>
      
      <div className="tabs-header">
        {responses.map((response, index) => (
          <button
            key={index}
            className={`tab-button ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
          >
            <span className="model-id">{response.model_id}</span>
            <span className="model-name">{response.model_name.split('/').pop().split(':')[0]}</span>
          </button>
        ))}
      </div>

      <div className="tab-content">
        {responses.map((response, index) => (
          <div
            key={index}
            className={`tab-panel ${activeTab === index ? 'active' : ''}`}
            style={{ display: activeTab === index ? 'block' : 'none' }}
          >
            <div className="response-header">
              <span className="model-full-name">{response.model_name}</span>
            </div>
            <div className="response-content">
              {response.response}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TabView;