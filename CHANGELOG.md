# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to Axiom Station will be documented in this file.

## [1.0.1] - 2026-10-29

### Fixed
- Fixed duplicate claim extraction in document parser: lines matching multiple claim-extraction conditions (factual pattern, number+keyword, frequency keyword) were generating duplicate claims, leading to duplicate contradiction reports. Each line now produces at most one claim.

### Added
- Frontend test suite (`frontend/src/components/Analyzer.test.tsx`) with 4 tests:
  - Form rendering verification
  - Default sample content check
  - Analyze submission mock testing
  - Error handling display
- Vitest configuration with jsdom environment and @testing-library/jest-dom matchers
- Test setup file for shared test configuration

### Updated
- README.md status checkboxes to reflect actual implementation state (all features except Keycloak OIDC complete)
- Frontend TypeScript config to exclude test files from build and include vitest globals
- STATUS.md with current test results and outstanding items

### Test Results
- Backend: 12 passed
- Frontend: 4 passed

## [1.0.0] - 2026-10-22

### Added
- FastAPI backend with document analysis API
- Markdown document parser with section classification (hook, body, table, exercise, learning objectives, problem, concept, ship-it)
- Contradiction detection engine for:
  - Numeric contradictions (parameter counts, dataset sizes, GPU hours, etc.)
  - Count contradictions (e.g., "three tasks" vs "four tasks")
  - Frequency contradictions (e.g., "annual" vs "per quarter")
  - Semantic contradictions between sections
- REST API endpoints:
  - POST /api/v1/documents/analyze - Analyze markdown content
  - POST /api/v1/documents/analyze/file - Upload and analyze markdown file
  - GET /api/v1/contradictions/ - List contradictions with filters
  - GET /api/v1/contradictions/stats - Get statistics
- React + TypeScript + Vite frontend with:
  - Document input form with phase/lesson metadata
  - File upload support
  - Analysis summary with severity breakdown
  - Contradiction table with filtering by phase, severity, section
  - Responsive professional UI
- Docker support with docker-compose.yml including:
  - Backend service (FastAPI + SQLite)
  - Frontend service (Nginx serving React build)
  - Keycloak service for OIDC authentication
- CI/CD pipeline with GitHub Actions:
  - Backend tests (pytest)
  - Frontend typecheck, tests, build
  - Docker image builds
- 12 backend tests covering document parsing, contradiction detection, and API endpoints
- MIT license

### Security
- Non-root Docker users
- HttpOnly SameSite cookie configuration ready
- CSRF protection structure in place
- No hardcoded secrets
- Environment variable configuration
