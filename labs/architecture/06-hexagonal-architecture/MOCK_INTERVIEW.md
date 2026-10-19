# Mock Interview: Ports and Adapters at a Toll Road Operator

> Clean Q&A format. TollPass lets drivers open accounts, tag vehicles, and get billed monthly for road trips. Leadership has switched payment processors twice in three years, and each switch rewrote the module end to end.

---

## Questions and Answers

1. "Sketch the ports that solve the switching problem."
   Driving side: `VehicleAccountManager`, the interface the web app talks to. Driven side: `PaymentProcessorPort` with a charge operation and a `LedgerPort` that records toll rows. Swapping providers later touches one adapter class plus a wiring choice — never the rules about unpaid balances blocking new trips.

2. "Provider #3 replaces #2 next quarter. What changes in the codebase?"
   A new adapter implements the existing port; the old adapter is deleted; configuration selects the bean. Domain rules — an account in arrears refuses new trips — remain byte-identical. That isolation is precisely the point of the exercise.

3. "How do you test trip billing without a real bank?"
   Fakes: an in-memory ledger and a scripted processor that declines on the fourth call. Business tests run in milliseconds with no network, and the bank adapter itself earns one thin contract test against its sandbox.

4. "Where do framework annotations live?"
   In the adapters, nowhere else. The core declares interfaces; it never imports a persistence or HTTP symbol. The day the core pulls in a framework type, the dependency rule has been breached whether or not the tests notice.

5. "Is this overkill for a smaller module?"
   For plain CRUD, yes — an honest service over a repository is the right answer there. Ports pay for themselves where an external dependency is likely to move: payment providers, legacy stores, message brokers, anything with a roadmap you do not control.

6. "Ports sound rigid when providers vary wildly."
   Variation lives outward: one adapter per partner, each translating its quirks into the core's vocabulary. If supporting a second provider makes the port look absurd, the port — not the pattern — was modelled wrong, and that is visible pressure to fix it.

7. "One port-hygiene rule you enforce in review?"
   Ports carry intent in their names; adapters carry the technology. The moment either drifts — a port named for a wire protocol, an adapter sneaking in a rule — the review flags it on sight.

8. "Refund boundaries — where do those live?"
   The core decides whether a refund is owed and how much; the adapter maps that decision onto whatever operation the provider supports. A provider that cannot express it reports a capability gap — the rule never bends to the tooling.

---

## Probes That Follow

- "Your driving port returns domain objects. REST wants JSON. Contention?" — the adapter owns translation at the edge; the core never learns a status code. Mapping cost is the tax adapters pay, deliberately, so the rules stay portable.
- "Two adapters both need the shared auth helper — where does it go?" — outside the core, as infrastructure both adapters import; anything the domain cannot express stays out of the domain.
- "A port with a single adapter and a single fake, forever?" — a consolidation candidate: abstraction with no second implementation and no prospect of one is ceremony, and ceremony is billed as onboarding time.
- "The core needs today's date — port that too?" — yes. A controllable calendar is what lets the arrears rule be tested deterministically, so time enters through a one-line interface like anything else.
- "Testing matrix across several adapters?" — shared test suites keyed to the port itself run against every adapter, so provider quirks surface as adapter failures rather than core surprises.

---

## Red Flag

Praising hexagonal layout while putting business rules inside an adapter "because that's where the scheduler can see them". The entire pattern exists to prevent exactly that transfer.
