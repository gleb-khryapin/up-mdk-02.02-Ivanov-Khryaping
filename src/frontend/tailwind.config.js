/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#f4f5f7",
        card: "#ffffff",
        accent: "#2563eb",
      },
    },
  },
  plugins: [],
};
