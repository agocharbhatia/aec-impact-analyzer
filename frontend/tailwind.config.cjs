/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        ink: '#0f172a',
        mist: '#e2e8f0',
        steel: '#334155',
        ember: '#f97316',
        signal: '#0ea5e9',
        alert: '#ef4444'
      },
      boxShadow: {
        panel: '0 10px 30px -18px rgba(15, 23, 42, 0.65)'
      }
    }
  },
  plugins: []
};
