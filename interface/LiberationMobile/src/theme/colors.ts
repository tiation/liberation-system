export const LiberationTheme = {
  // Main Colors
  primary: '#00ffff',        // Cyan
  secondary: '#9333ea',      // Purple
  accent: '#f59e0b',         // Orange/Yellow
  
  // Background Colors
  background: '#0a0a0a',     // Deep black
  surface: '#1a1a1a',       // Dark surface
  surfaceVariant: '#2a2a2a', // Lighter surface
  
  // Text Colors
  text: '#ffffff',           // White text
  textSecondary: '#a0a0a0',  // Secondary text
  textMuted: '#606060',      // Muted text
  
  // Status Colors
  success: '#10b981',        // Green
  warning: '#f59e0b',        // Orange
  error: '#ef4444',          // Red
  info: '#3b82f6',           // Blue
  
  // Neon Effects
  neonCyan: '#00ffff',
  neonPurple: '#9333ea',
  neonPink: '#ec4899',
  neonGreen: '#10b981',
  neonOrange: '#f59e0b',
  
  // Gradient Colors
  gradients: {
    primary: ['#00ffff', '#9333ea'],
    secondary: ['#9333ea', '#ec4899'],
    accent: ['#f59e0b', '#ef4444'],
    background: ['#0a0a0a', '#1a1a1a', '#2a2a2a'],
    neonGlow: ['#00ffff', '#9333ea', '#ec4899'],
  },
  
  // Border Colors
  border: '#333333',
  borderActive: '#00ffff',
  borderHover: '#666666',
  
  // Shadow Colors
  shadow: {
    primary: 'rgba(0, 255, 255, 0.3)',
    secondary: 'rgba(147, 51, 234, 0.3)',
    accent: 'rgba(245, 158, 11, 0.3)',
    dark: 'rgba(0, 0, 0, 0.5)',
  },
  
  // Opacity Levels
  opacity: {
    disabled: 0.6,
    overlay: 0.8,
    backdrop: 0.9,
    subtle: 0.1,
    medium: 0.3,
    strong: 0.7,
  },
  
  // Spacing
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  
  // Border Radius
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    full: 9999,
  },
  
  // Typography
  fontSize: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
    xxxl: 32,
  },
  
  // Animation Duration
  animation: {
    fast: 150,
    normal: 300,
    slow: 500,
  },
};

export const createNeonGlow = (color: string, intensity: number = 0.3) => ({
  shadowColor: color,
  shadowOffset: {
    width: 0,
    height: 0,
  },
  shadowOpacity: intensity,
  shadowRadius: 10,
  elevation: 5,
});

export const createGradientStyle = (colors: string[]) => ({
  colors,
  start: { x: 0, y: 0 },
  end: { x: 1, y: 1 },
});

export type LiberationThemeType = typeof LiberationTheme;
