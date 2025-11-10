import { useState, useEffect } from 'react';
import { Dimensions } from 'react-native';
import type { Orientation } from '@/types';

interface UseOrientationReturn {
  orientation: Orientation;
  screenWidth: number;
  screenHeight: number;
  isLandscape: boolean;
  isPortrait: boolean;
}

export function useOrientation(): UseOrientationReturn {
  const [dimensions, setDimensions] = useState(() => {
    const { width, height } = Dimensions.get('screen');
    return { width, height };
  });

  useEffect(() => {
    const subscription = Dimensions.addEventListener('change', ({ screen }) => {
      setDimensions({ width: screen.width, height: screen.height });
    });

    return () => subscription?.remove();
  }, []);

  const isLandscape = dimensions.width > dimensions.height;
  const orientation: Orientation = isLandscape ? 'landscape' : 'portrait';

  return {
    orientation,
    screenWidth: dimensions.width,
    screenHeight: dimensions.height,
    isLandscape,
    isPortrait: !isLandscape,
  };
}
