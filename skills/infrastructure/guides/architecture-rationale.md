# Architecture Rationale: Separation of Concerns

## Why Separate Config, Prompts, and Messages?

Traditional approach mixes everything:
```javascript
// ❌ Bad: Everything mixed in business logic
async function generateStory(userId) {
  const apiKey = 'sk-abc123';  // Config hardcoded
  const prompt = 'Write a story about...';  // Prompt hardcoded
  const errorMsg = 'Failed to generate story';  // Message hardcoded

  const response = await openai.chat({
    apiKey,
    messages: [{ role: 'user', content: prompt }]
  });

  if (!response) throw new Error(errorMsg);
  return response;
}
```

**Problems:**
- Can't change API key without code change
- Can't A/B test prompts
- Can't translate error messages
- Can't test logic without calling API
- Hard to maintain

---

## Separation of Concerns Approach

```
src/
├── config/           # Configuration
│   └── openai.ts     # API keys, endpoints, settings
├── prompts/          # LLM prompts
│   └── story.ts      # Prompt templates
├── messages/         # User-facing text
│   └── errors.ts     # Error messages
└── services/         # Business logic
    └── story.ts      # Pure logic, no hardcoded strings
```

**Implementation:**

```typescript
// config/openai.ts
export const openaiConfig = {
  apiKey: process.env.OPENAI_API_KEY!,
  model: 'gpt-4',
  maxTokens: 2000
};

// prompts/story.ts
export const storyPrompts = {
  generate: (topic: string) => `Write a compelling story about ${topic}.
    The story should be engaging and approximately 500 words.`,

  improve: (story: string) => `Improve this story: ${story}
    Make it more vivid and add sensory details.`
};

// messages/errors.ts
export const errorMessages = {
  storyGeneration: 'Unable to generate story. Please try again.',
  apiLimit: 'API rate limit reached. Please try again in a few minutes.',
  invalidInput: 'Please provide a valid topic for the story.'
};

// services/story.ts
import { openaiConfig } from '../config/openai';
import { storyPrompts } from '../prompts/story';
import { errorMessages } from '../messages/errors';

export async function generateStory(topic: string) {
  if (!topic) {
    throw new Error(errorMessages.invalidInput);
  }

  const prompt = storyPrompts.generate(topic);

  try {
    const response = await openai.chat({
      ...openaiConfig,
      messages: [{ role: 'user', content: prompt }]
    });

    return response.content;
  } catch (error) {
    if (error.code === 'rate_limit_exceeded') {
      throw new Error(errorMessages.apiLimit);
    }
    throw new Error(errorMessages.storyGeneration);
  }
}
```

---

## Benefits

### 1. Easy Configuration Changes

```typescript
// Change API key without touching code
// .env
OPENAI_API_KEY=sk-new-key

// Change model for all calls
// config/openai.ts
model: 'gpt-4-turbo'  // One line change
```

### 2. Prompt Iteration Without Code Changes

```typescript
// Version 1
generate: (topic) => `Write a story about ${topic}.`

// Version 2 (more specific)
generate: (topic) => `Write a compelling story about ${topic}.
  Include vivid descriptions and dialogue.`

// Version 3 (with structure)
generate: (topic) => `Write a story about ${topic}.
  Structure: Hook → Rising action → Climax → Resolution.
  Length: ~500 words.`

// No code changes in services/story.ts needed!
```

### 3. A/B Testing Prompts

```typescript
// prompts/story.ts
export const storyPromptsV1 = {
  generate: (topic) => `Write a story about ${topic}...`
};

export const storyPromptsV2 = {
  generate: (topic) => `Create a narrative about ${topic}...`
};

// services/story.ts
const prompts = Math.random() < 0.5 ? storyPromptsV1 : storyPromptsV2;
// Now can measure which version performs better
```

### 4. Easy Translation

```typescript
// messages/en/errors.ts
export const errorMessages = {
  storyGeneration: 'Unable to generate story.',
  apiLimit: 'Rate limit reached.'
};

// messages/ru/errors.ts
export const errorMessages = {
  storyGeneration: 'Не удалось создать историю.',
  apiLimit: 'Достигнут лимит запросов.'
};

// services/story.ts
import { errorMessages } from `../messages/${locale}/errors`;
```

### 5. Testable Business Logic

```typescript
// ✅ Easy to test - no hardcoded values
import { generateStory } from './story';

jest.mock('../config/openai', () => ({
  openaiConfig: { apiKey: 'test-key', model: 'gpt-4' }
}));

jest.mock('openai', () => ({
  chat: jest.fn().mockResolvedValue({ content: 'Test story' })
}));

test('generates story with correct prompt', async () => {
  const story = await generateStory('dragons');
  expect(story).toBe('Test story');
});
```

---

## Folder Structure by Project Type

### Web Applications (Next.js, React)

```
src/
├── components/           # UI components
│   ├── StoryCard.tsx
│   └── StoryGenerator.tsx
├── services/             # Business logic
│   ├── story.ts
│   └── user.ts
├── lib/                  # Utilities, helpers
│   ├── db.ts
│   └── auth.ts
├── config/               # Configuration
│   ├── openai.ts
│   └── database.ts
├── prompts/              # LLM prompts
│   └── story.ts
├── messages/             # User-facing text
│   ├── en/
│   └── ru/
tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
└── e2e/                  # E2E tests
```

### APIs (Express, FastAPI)

```
src/
├── routes/               # API endpoints
│   └── stories.ts        # GET /stories, POST /stories
├── services/             # Business logic
│   └── story.ts
├── models/               # Data models
│   └── Story.ts
├── middleware/           # Express middleware
│   ├── auth.ts
│   └── errorHandler.ts
├── config/               # Configuration
│   ├── openai.ts
│   └── database.ts
├── prompts/              # LLM prompts
│   └── story.ts
tests/
├── unit/
└── integration/
```

### CLI Tools

```
src/
├── commands/             # CLI commands
│   ├── generate.ts       # generate story
│   └── improve.ts        # improve story
├── services/             # Business logic
│   └── story.ts
├── config/               # Configuration
│   └── openai.ts
├── prompts/              # LLM prompts
│   └── story.ts
├── messages/             # User-facing text
│   └── cli.ts            # "Generating story...", "Done!"
tests/
├── unit/
└── integration/
```

---

## Anti-Patterns to Avoid

### ❌ Config in Code

```javascript
// Bad
const API_KEY = 'sk-abc123';
const MODEL = 'gpt-4';
```

**Why:** Can't change without code deployment.

**Fix:** Use environment variables + config files.

### ❌ Prompts Inline

```javascript
// Bad
const response = await openai.chat({
  messages: [{ role: 'user', content: 'Write a story about ' + topic }]
});
```

**Why:** Can't iterate on prompts easily.

**Fix:** Extract to prompts/ directory.

### ❌ Mixed Concerns

```javascript
// Bad: Everything in one file
// routes/stories.ts (300 lines)
// - Route handlers
// - Business logic
// - Database queries
// - API calls
// - Error messages
```

**Why:** Hard to test, hard to maintain.

**Fix:** Separate into routes/, services/, models/.

### ❌ Hardcoded Messages

```javascript
// Bad
throw new Error('Failed to generate story');
```

**Why:** Can't translate, can't change without code.

**Fix:** Extract to messages/ directory.

---

## Migration Strategy for Existing Code

**Step 1: Extract config**
```bash
mkdir src/config
# Move API keys, settings to config/
```

**Step 2: Extract prompts**
```bash
mkdir src/prompts
# Move LLM prompts to prompts/
```

**Step 3: Extract messages**
```bash
mkdir src/messages
# Move user-facing strings to messages/
```

**Step 4: Refactor services**
```javascript
// Before
function doSomething() {
  const key = 'sk-abc';
  const prompt = 'Do something';
  // ...
}

// After
import { config } from './config/api';
import { prompts } from './prompts/main';

function doSomething() {
  const key = config.apiKey;
  const prompt = prompts.doSomething;
  // ...
}
```

**Step 5: Add tests**
```javascript
// Now easy to test with mocks
jest.mock('./config/api');
jest.mock('./prompts/main');
```

---

## Real-World Example: Finspoved Bot

**Before (mixed concerns):**
```javascript
async function processNewResponse(formData) {
  const prompt = `Создай историю из данных анкеты: ${JSON.stringify(formData)}`;
  const story = await openai.chat({ apiKey: 'sk-...', messages: [...] });
  await db.insert({ story, status: 'pending' });
  await telegram.send(chatId, 'История создана и ожидает модерацию');
}
```

**After (separated):**
```javascript
// prompts/story.ts
export const storyPrompts = {
  generate: (formData) => `Создай анонимную карьерную историю...`
};

// messages/telegram.ts
export const telegramMessages = {
  storyCreated: 'История создана и ожидает модерацию',
  storyApproved: 'История одобрена и опубликована'
};

// services/story.ts
export async function processNewResponse(formData) {
  const story = await generateStory(formData);
  await saveStory(story);
  await notifyModerator(story);
}
```

**Benefits achieved:**
- ✅ Prompt versioning without code changes
- ✅ A/B testing different prompt styles
- ✅ Easy message translation (Russian/English)
- ✅ Testable business logic
- ✅ Config changes without deployment

---

## Summary

**Separation of concerns provides:**
1. **Maintainability** - Easy to find and change things
2. **Testability** - Can test logic without external dependencies
3. **Flexibility** - Change config/prompts without code changes
4. **Scalability** - Easy to add new features
5. **Team collaboration** - Clear boundaries, less conflicts

**Always separate:**
- Configuration → `config/`
- LLM prompts → `prompts/`
- User-facing text → `messages/`
- Business logic → `services/`
- Data access → `models/` or `lib/db/`
