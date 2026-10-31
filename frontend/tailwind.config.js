/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: 'var(--color-navy, #0B2A5B)',
          dark: 'var(--color-navy-dark, #071C3D)',
          light: 'var(--color-navy-light, #163B75)',
        },
        saffron: {
          DEFAULT: 'var(--color-saffron, #FF9933)',
          dark: 'var(--color-saffron-dark, #9A4A00)',
          light: 'var(--color-saffron-light, #FFF4E5)',
        },
        govgreen: {
          DEFAULT: 'var(--color-green, #138808)',
          dark: 'var(--color-green-dark, #0E6606)',
          light: 'var(--color-green-light, #EAF5EA)',
        },
        surface: {
          page: 'var(--color-page-bg, #F7F9FC)',
          card: 'var(--color-card-bg, #FFFFFF)',
        },
        border: {
          DEFAULT: 'var(--color-border, #D9E0EA)',
          subtle: 'var(--color-border-subtle, #E8EEF5)',
        },
        text: {
          primary: 'var(--color-text-primary, #1A2433)',
          muted: 'var(--color-text-muted, #55627A)',
        },
        govred: {
          DEFAULT: 'var(--color-error, #B3261E)',
          light: 'var(--color-error-light, #FDF2F2)',
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          'Noto Sans Devanagari',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
        hindi: ['Noto Sans Devanagari', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 2px 8px -1px rgba(11, 42, 91, 0.06), 0 1px 4px -1px rgba(11, 42, 91, 0.04)',
        'soft-md':
          '0 4px 14px -2px rgba(11, 42, 91, 0.08), 0 2px 6px -1px rgba(11, 42, 91, 0.04)',
        'soft-lg':
          '0 10px 25px -3px rgba(11, 42, 91, 0.1), 0 4px 10px -2px rgba(11, 42, 91, 0.05)',
      },
      borderRadius: {
        card: '12px',
      },
      maxWidth: {
        shell: '1200px',
      },
      minHeight: {
        tap: '44px',
      },
      minWidth: {
        tap: '44px',
      },
    },
  },
  plugins: [],
};
