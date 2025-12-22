# UX Guidelines

## Purpose
This file defines UX standards and user-facing communication for AI agents. Helps agents write consistent UI text and follow design patterns.

---

## Interface Language

**Primary language:** [e.g., "Russian" / "English" / "Both (i18n support)"]

**Localization:** [e.g., "Single language - no i18n" / "Multi-language via `/locales/`" / "Using react-i18next"]

<!-- If multilingual, specify which language is default and where translation files are -->

---

## Tone of Voice

**Overall tone:** [Choose: Formal / Professional / Casual / Friendly / Technical / Simple]

**Writing style:** [Describe in detail - not just keywords. E.g., "Short, direct sentences. Active voice. Focus on user actions. Avoid corporate jargon and passive constructions. Technical accuracy without overwhelming with details."]

**Voice characteristics:**
- **Formality level:** [e.g., "Professional but approachable - use 'you' but avoid slang" / "Casual and friendly - contractions OK, conversational"]
- **Emotional tone:** [e.g., "Warm and supportive" / "Neutral and factual" / "Confident and authoritative"]
- **Technical complexity:** [e.g., "Explain technical concepts simply" / "Assume technical audience" / "Balance - simple for common tasks, detailed for advanced"]
- **Humor:** [e.g., "Light humor in empty states, serious in errors" / "No humor - strictly professional" / "Playful but not distracting"]

**Example phrases by context:**

- ✅ Good: ""

- ❌ Avoid: ""


---

## Domain Glossary

[**Instructions - remove this section after filling:**

**When to add terms:**
- Domain-specific concepts that appear frequently in UI (e.g., in fintech: "wallet" vs "account" vs "balance")
- Terms that might be confused with similar concepts (e.g., "order" vs "booking" vs "reservation")
- Product-specific jargon that needs consistent naming across all text

**What NOT to add:**
- Generic UI words (button, form, page, menu, settings, etc.)
- Self-explanatory terms that don't need clarification
- One-time mentions or obvious concepts

**Important:** Empty glossary is perfectly fine. Only add terms when real naming conflicts or domain complexity emerges during development.

**Format:**
- **[Term]** — [What it means specifically in your product context]
  *UI example: "[Where/how users see it]"*

]

<!-- Start empty. Fill only when domain terminology actually appears and needs consistency -->

---

## Text Patterns

[How we write specific UI elements - keep examples SHORT]

### Buttons
**Style:** [e.g., "Action verb + object: 'Save changes', 'Create account'" / "Single verb: 'Save', 'Cancel'"]

**Examples:**
- Primary actions: [e.g., "Save changes", "Create workspace"]
- Secondary actions: [e.g., "Cancel", "Go back"]
- Destructive actions: [e.g., "Delete account", "Remove workspace"]

### Error Messages
**Format:** [e.g., "Problem + what to do: 'Invalid email. Please check and try again.'" / "Just state the problem: 'Invalid email address'"]

**Examples:**
- Validation: [e.g., "Email is required"]
- Auth errors: [e.g., "Incorrect password. Try again or reset password."]
- System errors: [e.g., "Something went wrong. Please try again."]

### Success Messages
**Format:** [e.g., "Confirmation + next step" / "Just confirmation"]

**Examples:**
- [e.g., "Account created! Check your email to verify."]
- [e.g., "Changes saved successfully."]

### Loading States
**Style:** [e.g., "Present continuous: 'Loading...', 'Saving changes...'" / "Please wait: 'Please wait...'"]

**Examples:**
- [e.g., "Loading workspace..."]
- [e.g., "Saving..."]

---

## Copy Reference

[If you have a separate file with all UI texts, link it here]

**Location:** [e.g., "See `/src/copy/ui-messages.ts` for all user-facing text" / "All text in `/locales/en.json`"]

<!-- If no separate file, write: "N/A - UI copy defined inline in components" -->

---

## Design System

[Visual design specifications - only if custom design exists]

**Design files:** [e.g., "Figma: [link]" / "No design files - using default [framework] components"]

**Color palette:**
- Primary: [e.g., "#0066FF" / "Default Material Blue"]
- Secondary: [e.g., "#FF6B00" / "N/A"]
- Error/Warning/Success: [e.g., "#FF0000, #FFA500, #00CC00" / "Standard"]

**Key components:**
- [e.g., "Custom Button with rounded corners + shadow"]
- [e.g., "Modal with blur backdrop"]
- [e.g., "Using standard [Chakra UI / Material UI / Ant Design] components"]

<!-- Only include if there are custom visual elements. If using standard framework components, write: "Standard [framework name] components with default theme" -->

---

## Accessibility

[Only include if there are specific requirements beyond standard practices]

**Requirements:**
- [e.g., "All buttons must have aria-label if icon-only"]
- [e.g., "Forms must have explicit <label> elements, no placeholder-only"]
- [e.g., "Color contrast ratio minimum 4.5:1"]

<!-- If following standard a11y practices with no special requirements, write: "Follow standard WCAG 2.1 AA guidelines" -->
