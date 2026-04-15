---
name: Everything must be strongly typed
description: Project-wide rule — no `object`, anonymous types, loose dicts, or JsonElement on API/service boundaries in C# code
type: feedback
originSessionId: 26a38dc0-0432-4437-91b9-5e7de4aa3fd3
---
Every API/service boundary in the C# codebase must use strongly-typed records, classes, or enums. No `object`, `dynamic`, anonymous types, `Dictionary<string, object>`, `Dictionary<string, JsonElement>`, or similar loose shapes where a record would do.

**Why:** The user caught `PostJson<object, BountyDto>(..., new { AcceptedBy = x })` in the ApiClient — anonymous type + `object` generic. They called it out immediately and asked that this be a project-wide requirement, not a one-time fix. Typed records are the default; if a dict/JsonElement shows up, there must be a justified reason.

**How to apply:**
- When writing new code: define a record/class DTO for every request/response body, config file, and service call. Never use `object` or `new { ... }` as a substitute.
- When editing existing code: if I'm touching a file that uses an untyped shape, promote it to a typed model rather than propagating the looseness.
- Acceptable exceptions: true free-form JSON at boundaries we don't control (rare), generic infrastructure code (e.g. `JsonSerializer.Deserialize<T>`), and trait dictionaries like `IDictionary<string, string>` for metadata bags. In those cases, type the immediate surface and only keep the dict internal.
- Check the whole edit before claiming done — grep for `object`, `Dictionary<string, object>`, `JsonElement`, `dynamic`, `new {` in the files I touched.
