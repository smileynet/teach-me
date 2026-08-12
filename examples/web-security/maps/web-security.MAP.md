---
domain: web-application-security
description: "Understand how web applications are attacked and how to build them so they resist those attacks"
generated: 2026-08-11
depth: 0
parent: null
leads_to:
  - penetration-testing
  - cloud-security
  - devsecops
  - secure-architecture
---

# Web Application Security

## Orientation

Every web app you ship is exposed to the entire internet the moment it goes live — bots probe it within hours. This domain teaches you to think like an attacker so you can build like a defender: understanding how authentication breaks, how input becomes an attack vector, and how the browser's security model either saves you or gets bypassed. You'll finish able to read an OWASP report and know exactly what to fix.

## Topics

### injection-and-input-validation
- **title:** Injection Attacks & Input Validation
- **why:** Untrusted input flowing into interpreters (SQL, OS, LDAP) is the oldest and most exploited class of web vulnerability
- **scope:** substantial
- **prereqs:** []
- **status:** complete

### authentication-and-session-management
- **title:** Authentication & Session Management
- **why:** If attackers can impersonate a legitimate user, nothing else you build matters
- **scope:** substantial
- **prereqs:** []
- **status:** in-progress

### authorization-and-access-control
- **title:** Authorization & Access Control
- **why:** Broken access control is the #1 risk in OWASP Top 10 2021 — most apps check "are you logged in?" but fail at "should YOU see THIS?"
- **scope:** substantial
- **prereqs:** [authentication-and-session-management]
- **status:** not-started

### cross-site-attacks
- **title:** Cross-Site Attacks (XSS & CSRF)
- **why:** These exploit the trust relationship between browser, user, and server — the unique attack surface of the web platform
- **scope:** substantial
- **prereqs:** [injection-and-input-validation]
- **status:** not-started

### cryptography-for-web-developers
- **title:** Cryptography for Web Developers
- **why:** You don't need to implement crypto, but you need to know when you're using it wrong — bad key management and weak hashing cause silent data exposure
- **scope:** substantial
- **prereqs:** []
- **status:** not-started

### security-headers-and-transport
- **title:** Security Headers & Transport Security
- **why:** The browser has a powerful security policy engine (CSP, CORS, HSTS) that most developers misconfigure or ignore entirely
- **scope:** substantial
- **prereqs:** [cross-site-attacks, cryptography-for-web-developers]
- **status:** not-started

### api-security
- **title:** API Security
- **why:** Modern apps are API-first — every endpoint is an attack surface, and APIs lack the browser protections that traditional web pages get for free
- **scope:** substantial
- **prereqs:** [authentication-and-session-management, authorization-and-access-control]
- **status:** not-started

### dependency-and-supply-chain-security
- **title:** Dependency & Supply Chain Security
- **why:** Your app is mostly other people's code — vulnerable dependencies and compromised packages are now a top attack vector
- **scope:** lightweight
- **prereqs:** []
- **status:** not-started

### security-monitoring-and-incident-response
- **title:** Security Monitoring & Incident Response
- **why:** You will be breached or probed — what you log and how fast you detect determines whether it's a near-miss or a disaster
- **scope:** lightweight
- **prereqs:** [authentication-and-session-management, injection-and-input-validation]
- **status:** not-started
