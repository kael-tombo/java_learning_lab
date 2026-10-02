# Lab 04: REST Data Sources — API Integration, File Upload/Download, ORDS

## Overview
Build APEX applications that consume external REST APIs, handle file uploads/downloads, expose ORDS REST services, and implement bulk CSV processing with resilience patterns.

## Learning Objectives
By the end of this lab, you will be able to:
- Create Web Credentials and Web Source Modules for external API authentication
- Build pages that call REST APIs and parse JSON responses
- Implement file upload with validation (MIME type, size) and download with inline preview
- Expose ORDS RESTful services with proper pagination and JSON formatting
- Process bulk CSV uploads using APEX_DATA_PARSER with batched API calls
- Implement retry logic and error handling for external API calls

## Prerequisites
- APEX 23.2+ workspace with ORDS enabled
- Oracle Database 19c+
- Network access to external APIs (or mock endpoints)
- Completed Labs 01-03

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Complete shipment tracking integration walkthrough |
| `THEORY.md` | REST integration architecture, Web Sources, ORDS, file handling |
| `CODE_DEEP_DIVE.md` | APEX_WEB_SERVICE, APEX_DATA_PARSER, APEX_FILE_MANAGER, ORDS internals |
| `EXERCISES.md` | 8 hands-on exercises |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference flashcards |
| `WORKED_EXAMPLE.sql` | Complete worked SQL/PLSQL |
| `MINI_PROJECT/` | Weather dashboard with multiple API integrations |
| `REAL_WORLD_PROJECT/` | Logistics portal with document management |

## Time Estimate
- Core lab: 120 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts Covered
1. **Web Credentials** — Secure API key storage in APEX vault
2. **Web Source Modules** — Declarative REST client definitions
3. **APEX_WEB_SERVICE** — Low-level PL/SQL API for REST calls
4. **File Upload/Download** — APEX_FILE_MANAGER, BLOB handling, inline preview
5. **ORDS REST Services** — DEFINE_MODULE, TEMPLATE, HANDLER for exposing data
6. **Bulk CSV Processing** — APEX_DATA_PARSER, batched API calls, MERGE upserts
7. **Resilience Patterns** — Retry with exponential backoff, circuit breaker, audit logging