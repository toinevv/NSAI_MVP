/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // NewSystem.AI Brand Colors from CLAUDE.md
        'primary-dark': '#03202F',
        'primary-teal': '#2DD4BF', 
        'surface-white': '#FFFFFF',
        'text-primary': '#000000',
        'text-secondary': '#7B7B7B',
        'automation-high': '#10B981',    // Green - High potential
        'automation-medium': '#F59E0B',  // Amber - Medium potential  
        'automation-low': '#6B7280',     // Gray - Low potential
      },
      fontFamily: {
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}