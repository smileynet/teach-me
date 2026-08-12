# Resources

## Primary Sources

| Resource | Type | Trust | Notes |
|----------|------|-------|-------|
| [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html) | Specification | Authoritative | The standard itself. Dense but definitive for token validation rules. |
| [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html) | Specification | Authoritative | How `.well-known/openid-configuration` works. |
| [RFC 7636 — PKCE](https://datatracker.ietf.org/doc/html/rfc7636) | RFC | Authoritative | Proof Key for Code Exchange. Why native/CLI apps need it. |
| [openidconnect-rs](https://github.com/ramosbugs/openidconnect-rs) | Crate source | High | The canonical Rust OIDC crate. Passes OIDC Relying Party Certification. |
| [oauth2-rs](https://github.com/ramosbugs/oauth2-rs) | Crate source | High | Foundation crate for OAuth2 in Rust. openidconnect builds on this. |
| [Auth0 — Authorization Code Flow with PKCE](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-pkce) | Provider docs | High | Clearest visual explanation of the auth code + PKCE flow. |
| [Shuttle Blog: OAuth with Axum](https://www.shuttle.dev/blog/2023/08/30/using-oauth-with-axum) | Tutorial | High | Full working example: axum + oauth2 crate + session management. |

## Rust Crate Ecosystem

| Crate | Role | When to use |
|-------|------|-------------|
| `openidconnect` | Full OIDC client | Web app login flow — does discovery, PKCE, token exchange, ID token validation |
| `oauth2` | OAuth2 client | When you only need OAuth2 (no ID tokens) or want lower-level control |
| `jsonwebtoken` | JWT decode/validate | Resource servers validating incoming bearer tokens |
| `jwtk` | JWT + JWKS | Resource servers needing automatic JWKS fetching and caching |
| `axum-oidc-layer` | Axum middleware | Production API auth — multi-tier caching, pluggable backends |
| `axum-jwt-oidc` | Axum middleware | Lightweight JWT validation for simpler APIs |
| `reqwest` | HTTP client | Token endpoint calls, JWKS fetching |

## What the Protocol Actually Guarantees

| Claim | Evidence | Source |
|-------|----------|--------|
| ID tokens prove identity TO YOUR APP (not to APIs) | Spec: "The ID Token is a security token that contains Claims about Authentication" | OIDC Core 1.0 §2 |
| PKCE prevents authorization code interception | code_verifier never transits the browser; interceptor can't compute it | RFC 7636 §1 |
| Discovery auto-configures everything from one URL | `.well-known/openid-configuration` returns all endpoints + supported features | OIDC Discovery 1.0 |
| Token validation requires 8 specific checks | iss, sub, aud, exp, iat, nonce, signature, at_hash | OIDC Core 1.0 §3.1.3.7 |
| Refresh token rotation detects theft | Reuse triggers family revocation | OAuth 2.0 Security BCP |

## What This System CANNOT Teach

| Domain | Why | What to do instead |
|--------|-----|-------------------|
| IdP configuration | Each provider has unique admin UI and terminology | Follow your provider's getting-started guide (Google Cloud Console, Keycloak admin, Auth0 dashboard) |
| Production secrets management | Operational concern, not protocol knowledge | Use Vault, AWS Secrets Manager, or env-var injection in your deployment |
| Compliance (SOC2, HIPAA) | Legal/organizational, not technical | Consult your security team — protocol correctness ≠ compliance |
| Cryptographic implementation | You should never implement JWT signature verification yourself | Use the crates — they handle RSA/ECDSA correctly |
