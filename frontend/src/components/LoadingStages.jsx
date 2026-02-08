import React from 'react';

const LoadingStages = ({ currentStage }) => {
  const stages = [
    { id: 1, name: 'Initial Responses', description: 'Consulting all LLMs...' },
    { id: 2, name: 'Cross Review', description: 'LLMs reviewing each other...' },
    { id: 3, name: 'Synthesis', description: 'Chairman preparing final answer...' }
  ];

  return (
    <div className="loading-stages">
      <h3>Processing Your Query</h3>
      <div className="stages-container">
        {stages.map((stage) => (
          <div 
            key={stage.id} 
            className={`stage ${currentStage === stage.id ? 'active' : ''} ${currentStage > stage.id ? 'completed' : ''}`}
          >
            <div className="stage-number">{stage.id}</div>
            <div className="stage-content">
              <div className="stage-name">{stage.name}</div>
              <div className="stage-description">{stage.description}</div>
            </div>
            {currentStage === stage.id && (
              <div className="spinner"></div>
            )}
            {currentStage > stage.id && (
              <div className="checkmark">✓</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LoadingStages;