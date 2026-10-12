# API error envelope

All public API errors use the following stable envelope:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found.",
    "retryable": false,
    "details": {},
    "trace_id": "opaque-request-id"
  }
}
```

The backend does not return stack traces or user-supplied payloads. Additional domain-specific
codes are added only with their phase-specific public contract.
