# Changelog

All notable changes to this project will be documented in this file.

## 0.1.1 - 2026-09-26

### Added

- Typed `check`, `uncheck`, `drag_and_drop`, `reload`, `select`, and `do_nothing` action helpers.
- Click modes through `actions.click(selector, click_type)`, including `single`, `double`, and `right`.
- The Task-level `translation` contract for opt-in rendered-page translation in Agent and headful runs.

### Fixed

- Corrected the Task download Cabinet field to `downloadCabinetId`, retaining `cabinetId` as a compatibility alias.
- Corrected Cabinet item statuses to `unuploaded` and `uploaded`, and added source Task/run metadata.

## 0.1.0 - 2026-09-26

### Added

- Initial synchronous and asynchronous Python clients.
- Complete resource coverage matching `@figranium/sdk` 0.2.0, including tasks, executions, schedules, captures, cabinets, credentials, browser sessions, settings, direct execution, authentication, and health.
- Bearer and `x-api-key` authentication, persistent sessions, custom `httpx` clients, request timeouts, structured errors, and SSE streams.
- Typed task/action payloads and helpers for action IDs and variable templates.
- API documentation, examples, and automated tests.
