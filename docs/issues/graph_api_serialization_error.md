# Bug: /api/graph/extract returns 500 due to non-serializable dataclasses

## Summary
Calling the medical graph extraction endpoint fails with a 500 response. The
route tries to jsonify the raw output of `MedicalEntityExtractor.process_user_message`,
which includes dataclass instances. Flask's JSON encoder cannot serialise these
objects and raises `TypeError: Object of type ExtractedEntity is not JSON serializable`.

## Steps to Reproduce
1. Start the Memory-X API.
2. POST `/api/graph/extract` with body `{ "text": "患者有高血压并服用氨氯地平" }`.
3. Observe a 500 response and the stack trace mentioning the non-serializable dataclass.

## Expected Result
The endpoint should return a JSON object describing the extracted entities and
relations.

## Actual Result
The server returns HTTP 500 with the serialization error described above.

## Environment
- main branch @ HEAD prior to fix
- Flask 2.x

## Additional Notes
Serialising the dataclasses (e.g. via `dataclasses.asdict`) before returning the
response resolves the issue.
