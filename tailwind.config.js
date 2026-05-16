/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#1a2b3d',
        secondary: '#2ecc71',
        accent: '#e74c3c',
        'accent-teal': '#14b8a6',
        'accent-gold': '#f59e0b',
        dark: {
          bg: '#0f172a',
          surface: '#1e293b',
          border: '#334155',
        },
        'text-main': '#0f172a',
        'text-muted': '#64748b',
        danger: '#ef4444',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
      },
    },
  },
  plugins: [],
}
