# Frontend Tests TODO

## Current Status

The frontend test suite has been migrated from jsdom to happy-dom to fix ESM compatibility issues. The happy-dom environment works correctly, but there are some test failures that need to be addressed.

## Issues to Fix

### 1. API Tests (src/api/articles.test.ts)

**12 failed tests** - Import/mock issues:

- `articlesApi.getArticles is not a function`
- `apiClient.post is not a function`
- `articlesApi.getAllTopics is not a function`

**Root Cause**: Mocking setup may not be working correctly with the new test environment.

**Solution**: Review mocking strategy and ensure proper vi.mock() setup.

### 2. Component Tests (src/components/ArticleCard.test.tsx)

**7 failed tests** - Component import issue:

- `Element type is invalid: expected a string (for built-in components) or a class/function (for composite components) but got: undefined`

**Root Cause**: ArticleCard component is not being imported correctly or export/import mismatch.

**Solution**: Verify component exports and imports in test files.

### 3. Passing Tests

- ✅ `src/store/authStore.test.ts` (5 tests) - All passing
- ✅ Some API insight tests passing

## Test Environment Change

**Before**: jsdom
**After**: happy-dom

**Reason**: jsdom v27 has ESM compatibility issues with parse5 package. Happy-dom is a faster, more modern alternative that works with Vitest.

**Configuration**:
```typescript
// vitest.config.ts
test: {
  environment: 'happy-dom', // Changed from 'jsdom'
}
```

## Next Steps

1. Fix API test mocks - ensure vi.mock() is properly configured
2. Fix ArticleCard component imports - check export/import statements
3. Add more component tests once imports are fixed
4. Increase test coverage for:
   - Pages
   - Hooks
   - Utils
   - Store actions

## Testing Commands

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test -- src/api/articles.test.ts

# Run with coverage
npm test -- --coverage
```

## Dependencies Installed

- `happy-dom` - Modern DOM implementation for testing
- `@testing-library/react` - React testing utilities
- `@testing-library/jest-dom` - Custom Jest matchers
- `@testing-library/user-event` - User interaction simulation
- `vitest` - Test runner

## Known Working Tests

- Auth store tests (Zustand state management)
- Some API tests (insights, recommendations)

## Priority Fixes

1. **High**: Fix ArticleCard component imports (blocks all component tests)
2. **Medium**: Fix API client mocking (blocks API tests)
3. **Low**: Add test coverage for remaining components
