declare module 'react-native-bottom-sheet' {
  import { Component } from 'react';
  import { ViewStyle } from 'react-native';

  interface BottomSheetProps {
    ref?: any;
    snapPoints: number[];
    index?: number;
    backgroundStyle?: ViewStyle;
    handleIndicatorStyle?: ViewStyle;
    children?: React.ReactNode;
  }

  export default class BottomSheet extends Component<BottomSheetProps> {
    expand(): void;
    close(): void;
    snapToIndex(index: number): void;
  }
}
