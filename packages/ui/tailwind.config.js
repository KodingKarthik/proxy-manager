/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    '../../client/app/src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)',
        panel: 'var(--panel)',
        'neon-cyan': 'var(--neon-cyan)',
        'neon-magenta': 'var(--neon-magenta)',
        accent: 'var(--accent)',
        muted: 'var(--muted)',
      },
      boxShadow: {
        'neon-cyan': '0 0 10px var(--neon-cyan), 0 0 20px var(--neon-cyan), 0 0 30px var(--neon-cyan)',
        'neon-magenta': '0 0 10px var(--neon-magenta), 0 0 20px var(--neon-magenta), 0 0 30px var(--neon-magenta)',
        'neon-cyan-sm': '0 0 5px var(--neon-cyan), 0 0 10px var(--neon-cyan)',
        'neon-magenta-sm': '0 0 5px var(--neon-magenta), 0 0 10px var(--neon-magenta)',
      },
    },
  },
  plugins: [],
};

