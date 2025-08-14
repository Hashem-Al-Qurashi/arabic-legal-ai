import { useState, useEffect } from 'react';

export const useTheme = () => {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('dark-mode');
    return saved ? JSON.parse(saved) : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark-mode', isDark);
    localStorage.setItem('dark-mode', JSON.stringify(isDark));
  }, [isDark]);

  return { isDark, toggleTheme: () => setIsDark(!isDark) };
};