/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tmdb: {
          primary: '#01b4e4',
          secondary: '#032541',
        }
      }
    },
  },
  plugins: [],
}
