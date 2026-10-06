# Lab 04: APEX Security — README

## Overview
Configure Oracle APEX to authenticate against Oracle Identity Cloud Service via
OAuth2/OIDC for corporate SSO: register the application, configure the
authentication scheme from IdP metadata, map claims, manage the client secret
securely, implement RP-initiated logout, and verify against the OWASP Top 10.

## Learning Objectives
By the end of this lab you will be able to:
- Explain APEX's four security layers and where each control belongs
- Compare authentication schemes (internal, LDAP, SAML, OIDC, custom) on
  stated criteria
- Register an APEX application as a confidential OIDC client
- Build an OIDC authentication scheme from IdP discovery metadata
- Map IdP claims to APEX user attributes safely
- Store the client secret outside application source
- Implement RP-initiated logout so sessions end at the IdP
- Walk the OWASP Top 10 with recorded evidence per item

## Prerequisites
- Oracle APEX 23.2 or later
- An Oracle Identity Cloud Service tenant (or equivalent OIDC provider)
- Basic OAuth2 and OpenID Connect concepts
- Lab 03: Security (RBAC + Custom Auth)

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | SSO integration walkthrough |
| `THEORY.md` | Four-layer model, scheme comparison, OIDC flow |
| `CODE_DEEP_DIVE.md` | Scheme config, claim mapping, logout, session state |
| `EXERCISES.md` | 8 hands-on security exercises |
| `MATH_FOUNDATION.md` | Token lifetime, attack surface, lockout math |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute SSO configuration exercise |
| `REAL_WORLD_PROJECT.md` | Corporate SSO for a financial services APEX app |

## Time Estimate
- Core lab: 180 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Four security layers** — authentication, authorisation, session, data
2. **Scheme comparison** — SSO, compliance, operational cost
3. **OIDC flow** — authorization code, tokens, and what each proves
4. **Claim mapping** — fail closed on an unmapped subject
5. **Credential storage** — secrets never in application source
6. **RP-initiated logout** — session termination at the IdP
7. **Session state** — minimal, no credentials, CSRF-protected
8. **OWASP** — verify each item, do not assume