# Generated API client

`schema.ts` is generated from `services/backend` OpenAPI. `client.ts` wraps it with
`openapi-fetch`, so application code gets typed paths, inputs, and responses without maintaining
duplicate frontend DTOs. Run `make generate-api` after changing public FastAPI schemas.
