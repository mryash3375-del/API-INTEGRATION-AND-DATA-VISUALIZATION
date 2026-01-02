## 2026-01-02 - Scrollable Container Accessibility
**Learning:** Scrollable containers (like those with `overflow-auto`) are often inaccessible to keyboard users because they lack focusability.
**Action:** Always add `tabindex="0"`, `role="region"`, and a descriptive `aria-label` to scrollable containers to ensure they can be focused and scrolled via keyboard.
