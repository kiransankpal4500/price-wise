/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0284c7',
          600: '#0284c7',
          700: '#0369a1',
        },
        bestpick: {
          badge: '#059669',
          bg: '#ecfdf5',
          border: '#10b981',
          accent: '#047857'
        }
      },
    },
  },
  plugins: [],
};
