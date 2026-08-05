---
name: Quantitive Dark
colors:
  surface: '#111415'
  surface-dim: '#111415'
  surface-bright: '#373a3b'
  surface-container-lowest: '#0c0f10'
  surface-container-low: '#191c1d'
  surface-container: '#1d2021'
  surface-container-high: '#282a2b'
  surface-container-highest: '#323536'
  on-surface: '#e1e3e4'
  on-surface-variant: '#bacac1'
  inverse-surface: '#e1e3e4'
  inverse-on-surface: '#2e3132'
  outline: '#85948c'
  outline-variant: '#3c4a43'
  surface-tint: '#2fe0aa'
  primary: '#44edb7'
  on-primary: '#003828'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#006c4f'
  secondary: '#c0c6db'
  on-secondary: '#293040'
  secondary-container: '#404758'
  on-secondary-container: '#aeb5c9'
  tertiary: '#ffc8a3'
  on-tertiary: '#502500'
  tertiary-container: '#ffa15b'
  on-tertiary-container: '#733800'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#dce2f7'
  secondary-fixed-dim: '#c0c6db'
  on-secondary-fixed: '#141b2b'
  on-secondary-fixed-variant: '#404758'
  tertiary-fixed: '#ffdcc6'
  tertiary-fixed-dim: '#ffb785'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#713700'
  background: '#111415'
  on-background: '#e1e3e4'
  surface-variant: '#323536'
typography:
  display:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  mono-data:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: -0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 20px
  margin-mobile: 16px
  margin-desktop: 32px
  max-width: 1200px
---

## Brand & Style
The design system is engineered for a mutual fund assistant, prioritizing clarity, precision, and high-level trust. The brand personality is "The Expert Strategist": knowledgeable, calm, and efficient. 

The aesthetic follows a **Modern Minimalist** direction with a focus on **High-Contrast Readability**. It utilizes a deep monochromatic foundation to reduce eye strain during financial analysis, punctuated by vibrant accents to highlight growth and actionable insights. The interface avoids unnecessary decoration, opting for structural integrity and data-first visualization.

## Colors
The palette is rooted in a deep-sea professional dark mode. 

- **Primary (#00d09c):** A "Groww-style" teal-green used exclusively for success states, growth indicators, primary call-to-action buttons, and active interactive elements.
- **Backgrounds:** The foundation uses `#0a0e14` for the base layer to ensure true depth, while `#111827` acts as the primary container color.
- **Typography:** Primary text is `#f9fafb` (95% white) for maximum contrast against dark backgrounds. Secondary text uses a muted slate-gray to establish hierarchy.
- **Accents:** Use subtle variations of the primary teal for hover states (darkened) and transparent glows (10% opacity) for high-end elevation.

## Typography
This design system utilizes **Inter** for all roles to maintain a systematic, utilitarian, and highly legible appearance. 

- **Numerical Data:** For fund returns and percentages, use `mono-data` with medium weight to ensure numbers align vertically in tables and lists.
- **Hierarchy:** Use `label-caps` for small metadata (e.g., "RISK LEVEL" or "NAV DATE") to provide a structural feel.
- **Readability:** Maintain a minimum body size of 14px for accessibility. Large display sizes should use negative letter spacing to feel tighter and more premium.

## Layout & Spacing
The design system employs a **Fluid Grid** model with strict 4px increments (the 4px square).

- **Grid:** A 12-column layout for desktop with 20px gutters. On mobile, transition to a single-column layout with 16px side margins.
- **Chat Layout:** The central assistant interface should be constrained to a max-width of 800px even on wide screens to ensure line lengths remain readable.
- **Rhythm:** Use `lg` (40px) spacing between major sections and `sm` (16px) for internal card padding. 
- **Fixed Elements:** The input area is anchored to the bottom with a background blur (Glassmorphism) to allow content to scroll behind it.

## Elevation & Depth
Depth is created through **Tonal Layering** and **Low-Contrast Outlines** rather than heavy shadows.

- **Level 0 (Base):** Background color `#0a0e14`.
- **Level 1 (Cards/Bubbles):** Surface color `#111827` with a 1px solid border of `#374151`.
- **Level 2 (Modals/Popovers):** Surface color `#1f2937` with a subtle 10% white inner glow and a 24px blur shadow with 30% opacity.
- **Interaction:** On hover, elevated cards should increase their border brightness to the primary teal at 50% opacity, providing immediate tactile feedback.

## Shapes
The shape language is "Soft Professional." 

- **Base Radius:** 8px (0.5rem) for cards, input fields, and standard buttons.
- **Large Radius:** 16px (1rem) for the main chat container and bottom sheets.
- **Circular:** Used exclusively for user avatars and icon containers. 
- **Chat Bubbles:** User bubbles feature a rounded-xl (24px) radius on three corners, with the corner pointing to the user remaining at 4px to indicate origin.

## Components
- **Chat Bubbles:** 
    - *Assistant:* Surface `#111827`, border `#374151`, text `#f9fafb`. 
    - *User:* Surface `#1f2937`, no border, text `#f9fafb`.
- **Suggestion Cards:** Interactive tiles for "Compare Funds" or "Calculate SIP." Use `Level 1` elevation with a primary teal icon.
- **Primary Buttons:** Solid `#00d09c` background with `#0a0e14` (dark) text for maximum visibility.
- **Input Field:** Fixed to the bottom. Background is a semi-transparent `#111827` with a `backdrop-filter: blur(12px)`. The text entry area is a simple underlined or low-border-radius box.
- **Chips:** Small pill-shaped containers for fund categories (e.g., "Equity," "Debt"). Use a subtle teal outline and 12px `label-caps` typography.
- **Data Visuals:** Charts should use the primary teal for growth lines and a secondary muted coral for loss/expense ratios.