# Mission

## Why I'm learning this

I'm building a Rust web service that needs user authentication. I want to integrate with an identity provider (Google, Keycloak, Auth0) using OpenID Connect — not roll my own auth. I need to understand the protocol well enough to implement it correctly and debug token validation failures at 2 AM.

## What success looks like

I can implement OIDC authentication in a Rust/axum web app from scratch. I understand the authorization code flow well enough to draw it on a whiteboard. When a token validation fails, I know which of the 8 validation steps broke and why. I can explain to a colleague why we use PKCE and what it prevents.

## Context

- Comfortable with Rust — async, traits, error handling are familiar
- Building on axum (but patterns apply to actix-web too)
- Using an external IdP (not building an auth server)
- Needs both: web app login flow AND API token validation for resource endpoints
- Security-conscious — wants to understand the "why" behind each step, not just copy-paste
