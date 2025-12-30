## 2025-10-26 - Horizontal Scroll Traps
**Learning:** `overflow-auto` containers (like the forecast list) are inaccessible to keyboard users unless they are explicitly focusable.
**Action:** Always add `tabindex="0"`, `role="region"`, and a descriptive `aria-label` to any container that scrolls internally.
