# Palette's Journal - Critical Learnings

## 2025-01-28 - Initial Review
**Learning:** The application uses vanilla JS with Chart.js and Bootstrap. The scrollable forecast container (`#forecastList`) in `templates/index.html` is a horizontally scrollable area but lacks keyboard accessibility attributes (role, tabindex, aria-label).
**Action:** When making scrollable regions (overflow-auto), always add `tabindex="0"`, `role="region"`, and a descriptive `aria-label` to ensure keyboard users can scroll.

## 2025-01-28 - Button Accessibility
**Learning:** Icon-only buttons (like the search icon in the input group text, though that's decorative) and potential future buttons need care. The "Search" and "Use my location" buttons have text, which is good.
**Action:** Always check icon-only controls for `aria-label`.
