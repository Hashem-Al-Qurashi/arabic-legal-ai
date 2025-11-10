import { useState, useEffect } from 'react';
import { Keyboard, KeyboardEvent, Platform } from 'react-native';

interface UseKeyboardReturn {
  keyboardVisible: boolean;
  keyboardHeight: number;
}

export function useKeyboard(): UseKeyboardReturn {
  const [keyboardVisible, setKeyboardVisible] = useState(false);
  const [keyboardHeight, setKeyboardHeight] = useState(0);

  useEffect(() => {
    const showEventName = Platform.OS === 'ios' ? 'keyboardWillShow' : 'keyboardDidShow';
    const hideEventName = Platform.OS === 'ios' ? 'keyboardWillHide' : 'keyboardDidHide';

    const onKeyboardShow = (event: KeyboardEvent): void => {
      setKeyboardVisible(true);
      setKeyboardHeight(event.endCoordinates.height);
    };

    const onKeyboardHide = (): void => {
      setKeyboardVisible(false);
      setKeyboardHeight(0);
    };

    const showSubscription = Keyboard.addListener(showEventName, onKeyboardShow);
    const hideSubscription = Keyboard.addListener(hideEventName, onKeyboardHide);

    return () => {
      showSubscription.remove();
      hideSubscription.remove();
    };
  }, []);

  return {
    keyboardVisible,
    keyboardHeight,
  };
}
