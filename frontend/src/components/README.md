components styles

This folder now uses a shared `components-base.css` to provide a consistent dashboard theme across components.

How it works

- Each component CSS imports `components-base.css` at the top:

  @import './components-base.css';

- `components-base.css` defines CSS variables (colors, radii), base `.card`/`.component-card` rules, and shared form/button styles.

Customizing a component

- Keep component-specific selectors (like `.sentiment-card`, `.risk-analysis`) in the component file. These should only override or extend the base rules.
- If a component should not use the dashboard theme, remove the `@import` line and apply custom styles.

Notes

- The base file intentionally keeps styles conservative. If you want to adjust global colors or radii, edit `components-base.css`.
- Avoid using CSS-in-CSS features like `composes:` (from CSS Modules) unless your build supports them.
