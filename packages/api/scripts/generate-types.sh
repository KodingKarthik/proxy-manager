#!/bin/bash
# Generate TypeScript types from OpenAPI schema

cd "$(dirname "$0")/.."
npx openapi-typescript openapi.json -o src/types.ts

