## 2025-10-27 - [Forecast List Accessibility]
**Learning:** Scrollable containers with `overflow: auto` are a keyboard trap if they lack `tabindex="0"`. Adding `role="region"` and `aria-labelledby` provides necessary context for screen readers.
**Action:** Always audit `overflow-auto` elements for keyboard accessibility.
