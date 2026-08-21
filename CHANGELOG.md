# Changelog

All notable changes to this project are documented in this file.

## [1.1.0](https://github.com/SendLayer/sendlayer-python/compare/v1.0.0...v1.1.0) (2026-08-21)

### Bug Fixes

* `Emails.send()` no longer discards the plain-text body when both `text` and
  `html` are supplied. The payload used a single computed dict key, which could
  only ever emit one of the two fields. Both `PlainContent` and `HTMLContent`
  are now sent, and `ContentType` is reported as `HTML` whenever an HTML body is
  present.
* API error messages are no longer discarded. The client read
  `response.json().get("Error", ...)`, but SendLayer returns errors as
  `{"Errors": [{"Code": ..., "Message": ...}]}`, so every error surfaced a
  hardcoded default instead of the API's own text. The 401 branch did not read
  the response body at all.
* `requests` exceptions no longer escape the SDK. `response.json()` was called
  unguarded on the 400/404/422/429/500 branches and on the success path, so a
  non-JSON error body (such as an HTML page from a proxy) or an empty success
  body raised `requests.exceptions.JSONDecodeError` — which is not a
  `SendLayerError`, so callers catching `SendLayerError` missed it. Empty
  success bodies now decode to `{}`, and undecodable bodies raise
  `SendLayerError`.
* Requests now time out. `self._session.timeout` was a silent no-op, because
  `requests.Session.request()` reads only the per-request keyword, and none was
  passed — so a hung server blocked forever and the documented
  `requests: {timeout: N}` option did nothing. Requests now default to 30
  seconds, matching the PHP SDK.
* `Webhooks.delete()` was annotated `-> None` while returning the response.
* Replaced a bare `except:` that swallowed `KeyboardInterrupt` and `SystemExit`.

### Features

* Every exception now carries `message`, `status_code`, `response` and `errors`,
  along with a `codes` helper for branching on SendLayer's numeric error codes.
  These previously existed only on `SendLayerAPIError`, so reading them after
  catching `SendLayerError` raised `AttributeError` for every other type.
* `SendLayer(api_key, config)` now forwards configuration to the underlying
  client. `__init__` accepted only `api_key`, so `timeout`,
  `attachmentURLTimeout` and the `requests` options were unreachable from the
  public entry point.
* All seven exception types are exported from the `sendlayer` package. Only
  `SendLayerError` and `SendLayerAPIError` were, so catching a validation or
  rate-limit error required importing from `sendlayer.exceptions`.

### Documentation

* Documented the exception attributes, the full list of exception types, and the
  `SendLayerAPIError` message prefix. The previous example had two identical
  `except SendLayerError` clauses, the second unreachable, and read attributes
  that did not exist on the type it caught.
* Added a Configuration section and an explicit HTML-with-plain-text-fallback
  example.

### Breaking Changes

* Requests now time out after 30 seconds by default. Callers relying on
  unbounded waits will see `SendLayerError` and should set an explicit `timeout`
  in config.

## 1.0.0

* Initial public release.
