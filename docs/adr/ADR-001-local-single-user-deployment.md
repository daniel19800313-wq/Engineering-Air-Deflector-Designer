# ADR-001: Local single-user deployment

## Context
V1 needs fast delivery and local engineering data without multi-user collaboration requirements.

## Decision
Run a React client with one FastAPI modular monolith and SQLite for a single local user. Bind to loopback by default. Use a configurable per-user data directory and documented application-controlled backup/restore. Do not add authentication unless remote access is introduced.

## Alternatives considered
Hosted multi-user SaaS; desktop-native shell; local service with cosmetic authentication.

## Consequences
Deployment and consistency stay simple. Concurrent remote access, centralized administration, and collaboration are excluded. External binding requires a new security decision.

## Reversibility
Moderate. API and repository boundaries allow hosted deployment and PostgreSQL later.

## Status
Accepted in conditional Sprint 1 review.
