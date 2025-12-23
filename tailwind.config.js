/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/frontend/index.html",
    "./src/frontend/src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gdot: {
          blue: '#005F87',
          gray: '#6D6E71',
          yellow: '#F0B323'
        }
      }
    },
  },
  plugins: [],
}






