/** @type {import('tailwindcss').Config} */
export default {
  content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        keyframes: {
          fadeIn: {
            '0%': { opacity: 0, transform: 'scale(0.9)' },  // Ensure this line ends with a semicolon
            '100%': { opacity: 1, transform: 'scale(1)' },  // Ensure this line ends with a semicolon
          },
        },
        animation: {
          fadeIn: 'fadeIn 1s ease-in-out',
        },
      },
    },
plugins: [],
}