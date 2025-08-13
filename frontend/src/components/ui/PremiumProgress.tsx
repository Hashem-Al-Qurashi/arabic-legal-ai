import React from 'react';

interface PremiumProgressProps {
  current: number;
  max: number;
  label: string;
  type: 'messages' | 'exports' | 'exchanges' | 'citations';
}

const PremiumProgress: React.FC<PremiumProgressProps> = ({ current, max, label, type }) => {
  const percentage = (current / max) * 100;
  const isNearLimit = percentage > 70;
  const isAtLimit = current >= max;

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%)',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '12px',
      padding: '12px 16px',
      margin: '8px 0',
      boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      transform: isNearLimit ? 'scale(1.02)' : 'scale(1)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px'
      }}>
        <span style={{
          fontSize: '14px',
          fontWeight: '500',
          color: isAtLimit ? '#DC2626' : isNearLimit ? '#D97706' : '#6B7280',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
        }}>
          {label}
        </span>
        <span style={{
          fontSize: '13px',
          fontWeight: '600',
          color: isAtLimit ? '#DC2626' : isNearLimit ? '#D97706' : '#374151'
        }}>
          {current}/{max}
        </span>
      </div>
      
      {/* Elegant progress bar */}
      <div style={{
        width: '100%',
        height: '4px',
        background: 'rgba(0, 0, 0, 0.1)',
        borderRadius: '2px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${Math.min(percentage, 100)}%`,
          height: '100%',
          background: isAtLimit 
            ? 'linear-gradient(90deg, #DC2626 0%, #EF4444 100%)'
            : isNearLimit
            ? 'linear-gradient(90deg, #D97706 0%, #F59E0B 100%)'
            : 'linear-gradient(90deg, #006C35 0%, #10B981 100%)',
          borderRadius: '2px',
          transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: isNearLimit ? '0 0 8px rgba(217, 119, 6, 0.4)' : 'none'
        }} />
      </div>
      
      {/* Clean upgrade hint */}
      {isNearLimit && (
        <div style={{
          marginTop: '8px',
          fontSize: '11px',
          color: '#6B7280',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          fontWeight: '500',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <div style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: isAtLimit ? '#DC2626' : '#D97706'
          }} />
          {isAtLimit ? 'حد مجاني مكتمل' : 'قريباً من الحد'}
        </div>
      )}
    </div>
  );
};

export default PremiumProgress;