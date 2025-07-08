import React from 'react';

interface ProgressBarProps {
  progress: number; // 0-100
  message: string;
  isVisible: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  message,
  isVisible
}) => {
  if (!isVisible) return null;

  return (
    <div style={{ 
      marginBottom: '20px',
      padding: '15px',
      border: '1px solid #e0e0e0',
      borderRadius: '8px',
      backgroundColor: '#f9f9f9'
    }}>
      <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>
        📊 {message}
      </p>
      
      <div style={{
        width: '100%',
        height: '20px',
        backgroundColor: '#e0e0e0',
        borderRadius: '10px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${progress}%`,
          height: '100%',
          backgroundColor: '#4CAF50',
          borderRadius: '10px',
          transition: 'width 0.3s ease'
        }} />
      </div>
      
      <p style={{ 
        margin: '5px 0 0 0', 
        fontSize: '14px', 
        textAlign: 'right',
        color: '#666' 
      }}>
        {Math.round(progress)}%
      </p>
    </div>
  );
};

export {};