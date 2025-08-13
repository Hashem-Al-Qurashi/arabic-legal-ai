import React from 'react';

interface FeatureTeaseProps {
  title: string;
  description: string;
  icon: string;
  disabled: boolean;
  onUpgrade: () => void;
}

const FeatureTease: React.FC<FeatureTeaseProps> = ({ title, description, icon, disabled, onUpgrade }) => {
  if (!disabled) return null;

  return (
    <div 
      onClick={onUpgrade}
      style={{
        background: 'linear-gradient(135deg, rgba(0, 108, 53, 0.05) 0%, rgba(0, 74, 36, 0.05) 100%)',
        border: '1px dashed rgba(0, 108, 53, 0.2)',
        borderRadius: '12px',
        padding: '16px',
        margin: '12px 0',
        cursor: 'pointer',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        overflow: 'hidden'
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 0.1) 0%, rgba(0, 74, 36, 0.1) 100%)';
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 108, 53, 0.15)';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 0.05) 0%, rgba(0, 74, 36, 0.05) 100%)';
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <span style={{ fontSize: '24px' }}>{icon}</span>
        <div style={{ flex: 1 }}>
          <h4 style={{
            margin: '0 0 4px 0',
            fontSize: '16px',
            fontWeight: '600',
            color: '#006C35',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
          }}>
            {title}
          </h4>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: '#6B7280',
            lineHeight: '1.4'
          }}>
            {description}
          </p>
        </div>
        <div style={{
          background: 'linear-gradient(135deg, #006C35 0%, #004A24 100%)',
          color: 'white',
          borderRadius: '6px',
          padding: '4px 8px',
          fontSize: '11px',
          fontWeight: '600',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          PRO
        </div>
      </div>
      
      {/* Subtle shimmer effect */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: '-100%',
        width: '100%',
        height: '100%',
        background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)',
        animation: 'shimmer 3s ease-in-out infinite'
      }} />
    </div>
  );
};

export default FeatureTease;