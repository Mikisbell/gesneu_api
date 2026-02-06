import type { Config } from 'tailwindcss'

const config: Config = {
	darkMode: ['class'],
	content: [
		'./src/pages/**/*.{js,ts,jsx,tsx,mdx}',
		'./src/components/**/*.{js,ts,jsx,tsx,mdx}',
		'./src/app/**/*.{js,ts,jsx,tsx,mdx}',
	],
	theme: {
		extend: {
			// ✅ 2026: Container queries support
			container: {
				center: true,
				padding: '2rem',
				screens: {
					'2xl': '1400px',
				},
			},
			backgroundImage: {
				'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
				'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
			},
			// ✅ 2026: Advanced animations
			animation: {
				'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
				'fade-in': 'fadeIn 0.2s ease-out',
				'fade-out': 'fadeOut 0.2s ease-in',
				'slide-in-bottom': 'slideInBottom 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
				'slide-in-top': 'slideInTop 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
				'slide-out-bottom': 'slideOutBottom 0.2s cubic-bezier(0.4, 0, 1, 1)',
				'scale-in': 'scaleIn 0.15s ease-out',
				'scale-out': 'scaleOut 0.15s ease-in',
				'spin-slow': 'spin 3s linear infinite',
			},
			keyframes: {
				fadeIn: {
					'0%': { opacity: '0' },
					'100%': { opacity: '1' },
				},
				fadeOut: {
					'0%': { opacity: '1' },
					'100%': { opacity: '0' },
				},
				slideInBottom: {
					'0%': { transform: 'translateY(16px)', opacity: '0' },
					'100%': { transform: 'translateY(0)', opacity: '1' },
				},
				slideInTop: {
					'0%': { transform: 'translateY(-16px)', opacity: '0' },
					'100%': { transform: 'translateY(0)', opacity: '1' },
				},
				slideOutBottom: {
					'0%': { transform: 'translateY(0)', opacity: '1' },
					'100%': { transform: 'translateY(16px)', opacity: '0' },
				},
				scaleIn: {
					'0%': { transform: 'scale(0.95)', opacity: '0' },
					'100%': { transform: 'scale(1)', opacity: '1' },
				},
				scaleOut: {
					'0%': { transform: 'scale(1)', opacity: '1' },
					'100%': { transform: 'scale(0.95)', opacity: '0' },
				},
			},
			// ✅ 2026: Fluid border radius
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)',
			},
			// ✅ 2026: Semantic color system
			colors: {
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))',
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))',
				},
				primary: {
					DEFAULT: 'hsl(var(--primary))',
					foreground: 'hsl(var(--primary-foreground))',
				},
				secondary: {
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))',
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))',
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))',
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))',
				},
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				chart: {
					'1': 'hsl(var(--chart-1))',
					'2': 'hsl(var(--chart-2))',
					'3': 'hsl(var(--chart-3))',
					'4': 'hsl(var(--chart-4))',
					'5': 'hsl(var(--chart-5))',
				},
			},
		},
	},
	plugins: [
		require("tailwindcss-animate"),
		// ✅ 2026: Container queries plugin
		require('@tailwindcss/container-queries'),
	],
}
export default config
