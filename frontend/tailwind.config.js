/** @type {import('tailwindcss').Config} */
export default {
<<<<<<< Updated upstream
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#f0f9ff',
                    100: '#e0f2fe',
                    200: '#bae6fd',
                    300: '#7dd3fc',
                    400: '#38bdf8',
                    500: '#0ea5e9',
                    600: '#0284c7',
                    700: '#0369a1',
                    800: '#075985',
                    900: '#0c4a6e',
                },
            },
        },
    },
    plugins: [],
}
=======
    content: ["./index.html", "./src/**/*.{js,jsx}"],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                serif: ['"Playfair Display"', 'serif'],
            },
            colors: {
                ssamz: {
                    navy: "#0B1F3B",
                    blue: "#2F80ED",
                    bg: "#F5F7FB",
                    border: "#E6EAF2",
                    text: "#1F2A37",
                },
            },
            boxShadow: {
                card: "0 6px 22px rgba(15, 23, 42, 0.08)",
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out forwards',
            },
        },
    },
    plugins: [],
};
>>>>>>> Stashed changes
