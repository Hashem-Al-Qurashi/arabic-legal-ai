import React from 'react';
import type { MessageElement } from '../../types';

interface MessageRendererProps {
  elements: MessageElement[];
}

export const MessageRenderer: React.FC<MessageRendererProps> = ({ elements }) => {
  const renderElement = (element: MessageElement, index: number): React.ReactNode => {
    const baseStyle = {
      margin: 0,
      padding: 0,
      textAlign: 'right' as const,
      direction: 'rtl' as const,
      fontFamily: "'Noto Sans Arabic', sans-serif"
    };
    
    switch (element.type) {
      case 'heading':
        const HeadingTag = `h${element.level || 2}` as keyof JSX.IntrinsicElements;
        return (
          <HeadingTag
            key={index}
            style={{
              ...baseStyle,
              fontSize: element.level === 1 ? '2rem' : element.level === 2 ? '1.8rem' : '1.6rem',
              fontWeight: '700',
              color: element.level === 1 ? '#1e40af' : element.level === 2 ? '#059669' : '#dc2626',
              marginBottom: '0.5rem',
              marginTop: index === 0 ? '0' : '1rem'
            }}
          >
            {element.content}
          </HeadingTag>
        );
        
      case 'paragraph':
        return (
          <p
            key={index}
            style={{
              ...baseStyle,
              fontSize: '15px',
              lineHeight: '1.5',
              marginBottom: '0.8rem',
              marginTop: index === 0 ? '0' : '0.3rem'
            }}
          >
            {element.children ? renderInlineElements(element.children) : element.content}
          </p>
        );
        
      case 'listItem':
        return (
          <li
            key={index}
            style={{
              ...baseStyle,
              fontSize: '24px',
              lineHeight: '1.4',
              marginBottom: '0.3rem',
              listStylePosition: 'inside'
            }}
          >
            {element.content}
          </li>
        );
        
      default:
        return null;
    }
  };
  
  const renderInlineElements = (elements: MessageElement[]): React.ReactNode => {
    return elements.map((element, index) => {
      switch (element.type) {
        case 'strong':
          return (
            <strong key={index} style={{ color: '#1e40af', fontWeight: '700' }}>
              {element.content}
            </strong>
          );
        case 'emphasis':
          return (
            <em key={index} style={{ color: '#059669', fontStyle: 'italic' }}>
              {element.content}
            </em>
          );
        case 'text':
        default:
          return element.content;
      }
    });
  };
  
  // Group consecutive list items
  const groupedElements: React.ReactNode[] = [];
  let currentListItems: MessageElement[] = [];
  
  elements.forEach((element, index) => {
    if (element.type === 'listItem') {
      currentListItems.push(element);
    } else {
      if (currentListItems.length > 0) {
        groupedElements.push(
          <ul key={`list-${index}`} style={{ margin: '0.5rem 0', paddingRight: '1.5rem' }}>
            {currentListItems.map((item, i) => renderElement(item, i))}
          </ul>
        );
        currentListItems = [];
      }
      groupedElements.push(renderElement(element, index));
    }
  });
  
  // Handle remaining list items
  if (currentListItems.length > 0) {
    groupedElements.push(
      <ul key="list-final" style={{ margin: '0.5rem 0', paddingRight: '1.5rem' }}>
        {currentListItems.map((item, i) => renderElement(item, i))}
      </ul>
    );
  }
  
  return <div style={{ direction: 'rtl', textAlign: 'right' }}>{groupedElements}</div>;
};