import { Dimensions, Platform } from 'react-native';

const { width, height } = Dimensions.get('window');

// Device type detection
const isSmallDevice = width < 375;
const isTablet = width > 600;
const isLandscape = height < width;

// Responsive scaling function
export const scale = (size) => {
  const baseWidth = 375; // iPhone baseline
  return (width / baseWidth) * size;
};

// Responsive font sizes
export const responsiveFontSize = {
  xs: scale(11),
  sm: scale(12),
  base: scale(14),
  lg: scale(16),
  xl: scale(18),
  '2xl': scale(20),
  '3xl': scale(24),
  '4xl': scale(28),
};

// Responsive spacing
export const responsiveSpacing = {
  xs: scale(4),
  sm: scale(8),
  md: scale(12),
  lg: scale(16),
  xl: scale(20),
  '2xl': scale(24),
  '3xl': scale(32),
};

// Responsive padding
export const responsivePadding = {
  horizontal: scale(15),
  vertical: scale(10),
};

// Device info
export const deviceInfo = {
  width,
  height,
  isSmallDevice,
  isTablet,
  isLandscape,
  isAndroid: Platform.OS === 'android',
  isIOS: Platform.OS === 'ios',
};

// Responsive column count for grid layouts
export const getGridColumns = () => {
  if (isTablet) return 3;
  return 2;
};

// Responsive header height
export const responsiveHeaderHeight = isTablet ? 70 : 60;

// Responsive border radius
export const responsiveBorderRadius = {
  sm: scale(6),
  md: scale(8),
  lg: scale(12),
  xl: scale(16),
};

// Responsive shadows
export const responsiveShadow = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
};

export default {
  scale,
  responsiveFontSize,
  responsiveSpacing,
  responsivePadding,
  deviceInfo,
  getGridColumns,
  responsiveHeaderHeight,
  responsiveBorderRadius,
  responsiveShadow,
};
