# Design Tokens

This document describes the design tokens used in the Proxy Manager Frontend.

## Colors

### Background Colors
- `--bg: #020204` - Main background (near-black)
- `--panel: #071023` - Panel/card background (dark blue)

### Accent Colors
- `--neon-cyan: #00FFF7` - Primary accent color (cyan)
- `--neon-magenta: #FF00E1` - Secondary accent color (magenta)
- `--accent: #0FF0D8` - Hover/focus accent (lighter cyan)
- `--muted: #6b7684` - Muted text color (gray)

## Typography

- Font Family: Inter, system fonts
- Font Sizes: Defined by Tailwind's default scale
- Font Weights: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

## Spacing

- Uses Tailwind's default spacing scale (4px base unit)

## Shadows

- `neon-cyan`: Cyan glow shadow
- `neon-magenta`: Magenta glow shadow
- `neon-cyan-sm`: Small cyan glow
- `neon-magenta-sm`: Small magenta glow

## Borders

- Border radius: `rounded-lg` (0.5rem / 8px)
- Border width: 1px
- Border color: `--neon-cyan`

## Transitions

- Duration: 200ms for most transitions
- Easing: Default (ease-in-out)

## Usage

Design tokens are defined in `packages/ui/src/theme.css` and consumed via Tailwind CSS variables. To use them in components:

```tsx
// Using Tailwind classes
<div className="bg-bg text-neon-cyan border-neon-cyan">
  Content
</div>

// Using CSS variables directly
<div style={{ backgroundColor: 'var(--bg)', color: 'var(--neon-cyan)' }}>
  Content
</div>
```

## Customization

To change the theme colors, update the CSS variables in `packages/ui/src/theme.css`. The changes will automatically apply throughout the application.

