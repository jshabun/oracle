/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'oracle-orange': '#FF6B35',
        'oracle-blue': '#004E89',
        'oracle-dark': '#1A1A2E',
      }
    },
  },
  plugins: [],
}
