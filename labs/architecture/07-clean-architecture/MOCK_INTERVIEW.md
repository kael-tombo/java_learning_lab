# Mock Interview Prep: Clean Architecture for an Invoicing Run

> Personal prep notes, first-person throughout, going before a staff hiring panel. AutoLedger produces customer invoices; month-end batch jobs move real money.

---

## The Case I Walk In With

I frame the layers as risk containment, not aesthetics. Entities carry the rules an auditor rereads: `Invoice.finalize()` refuses lines without a tax code and refuses an empty invoice. Use cases orchestrate: `MonthEndInvoiceRun` fetches orders due, builds invoices, tracks per-customer progress, and reports failures at the end. Adapters translate — a scheduler trigger and a manual admin endpoint both feed the same use case, and a presenter shapes the response object. Storage, mail, and the calendar enter through interfaces the outer ring implements.

---

## Questions I Expect, With Replies

1. "Why not put `finalize()` inside a service?"
   Because a service imports everything the day does — persistence, queues, whatever — and the rule drowns. The entity keeps the rule plain: constructible, assertable, runnable in a unit test with no container.

2. "What does framework independence actually buy?"
   A demonstrated swap: replacing the relational store touched adapter classes only. Interactors and entities never noticed, because neither had ever referenced the store.

3. "Five DTO layers seems heavy."
   Agreed if translations happen everywhere. I confine mapping to the ring boundaries — request to command, result to view object — while internal calls pass domain objects untouched. Mapping cost should concentrate, not spread.

4. "Where does authorization get checked?"
   At the driving adapter, and once more coarsely inside the use case as a guard. The inner check protects the rule from a forgotten controller; the outer check keeps user context from creeping inward.

5. "What erodes this architecture fastest?"
   Persistence annotations creeping onto entities as a shortcut. One annotation drags lazy-loading policy into the enterprise rules, and suddenly the store dictates the business. Module walls that forbid the core from seeing framework packages are the enforcement.

6. "Presenters seem like ceremony. Drop them?"
   For a raw status reply, a presenter is a passthrough and I skip it. Anything that formats, orders, or hides fields needs one tested place to live, and ad-hoc formatting in controllers is exactly where it starts to rot.

7. "Interactors calling other interactors?"
   Permitted rarely, suspected always: nested use cases signal a missing rule boundary. Pull the shared rule down into the entity instead, and the nesting disappears on its own.

8. "What about the audit log?"
   An output port: the use case emits facts about itself, and whichever adapter wants to persist or forward them, persists or forwards them. Auditing stays a decision of the outer ring, not of the rules.

---

## The Trap

A candidate who builds the rings but returns persistence rows as views "to save a mapping step". Inversion theatre: if inner layers hand outer layers storage shapes, the dependency rule turns decorative.

## One More Answer I Keep Ready

Asked why this and not ports-and-adapters vocabulary: the mechanics overlap heavily, but stakeholders hear "use case" faster than "port", and month-end invoicing is a use-case-shaped problem — communicate the structure in words the room already owns.

Asked how entity names age: they keep the business word even as storage shifts beneath them. The store may reorganize freely; the language of the rules does not, and that asymmetry is the protection working.

Asked about the batch window: the run receives its period and its sense of "now" through interfaces, so a test can freeze the month-end, and no rule ever consults a system clock directly.
