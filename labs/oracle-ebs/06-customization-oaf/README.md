# Lab 06: Customization (OAF) — README

## Overview
Build an OAF (Oracle Application Framework) custom invoice approval page for a
healthcare client — extending APXINWKB to display the scanned invoice image
alongside EBS invoice data, with Approve/Reject actions, reason codes, custom
logging, and Oracle Approval Workflow integration on EBS 12.2.10.

## Learning Objectives
By the end of this lab you will be able to:
- Design an OAF page in JDeveloper using BC4J components
- Extend the standard APXINWKB invoice workbench
- Build a custom VO joining `AP_INVOICES_ALL` and `FND_ATTACHMENTS`
- Implement a controller with Approve/Reject action handlers
- Trigger Oracle Approval Workflow completion programmatically
- Register the page as a function in the Application Object Library
- Grant access via responsibility and function security

## Prerequisites
- Oracle EBS R12.2 fundamentals
- Java basics and JDeveloper familiarity
- OA Framework MVC concepts (VO, AM, Controller)
- BC4J architecture

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Full OAF page design and implementation |
| `THEORY.md` | OAF architecture, MVC, extension vs customization, workflow |
| `CODE_DEEP_DIVE.md` | VO, AM, Controller, workflow calls, registration |
| `EXERCISES.md` | 8 hands-on OAF exercises |
| `MATH_FOUNDATION.md` | Performance budgets, image sizing, interaction cost |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute OAF page exercise |
| `REAL_WORLD_PROJECT.md` | Healthcare invoice approval page |

## Time Estimate
- Core lab: 150 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **OAF MVC** — View Object, Application Module, Controller
2. **BC4J** — the Java layer between the page and the database
3. **Extensions vs customizations** — decision and cost
4. **VO design** — joins, bind variables, view object layering
5. **Controllers** — action handling, validation, security
6. **Approval workflow** — programmatic completion
7. **Registration** — AOL function, menu, responsibility
8. **Function security** — least privilege at the action level