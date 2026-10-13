# Mental Models: Class Loading

## 1. The library with three desks

Bootstrap, platform, and app are reference desks in one line. Every
request starts at the app desk, which forwards up before checking its
own shelves. The top desk holds the unreplaceable core collection —
no request for `java.*` ever comes back down. The extension desk
closed in 2017 (JEP 220); its stock moved to the platform desk.

## 2. Load, link, initialize as build phases

Loading is delivery (bytes arrive). Linking is inspection (verify the
cargo, clear shelf space with zeroes, file cross-references without
opening boxes). Initialization is opening day (`<clinit>` runs the
shop's setup script). `loadClass` pays for delivery + inspection;
`forName` additionally cuts the ribbon. Constants are flyers printed
at the sender — they never wait for opening day.

## 3. Identity as passport, not face

Two people can share a name and photo (identical bytes) yet hold
different passports (defining loaders). Border control (the
verifier's cast check) compares passports, not faces — `w2.cast(o1)`
fails because the issuing authorities differ. "Same name" is a
coincidence; "same passport" is identity.

## 4. Delegation as a one-way mirror

Parents cannot see children: the platform desk has no window onto
app shelves. Framework code upstairs that needs a book from
downstairs cannot use the request line (it only goes up) — it must
use the back staircase, the thread-context loader. Forgetting the
staircase is every "works in main, fails in the container" story.

## 5. <clinit> as a once-only fuse

Each (name, loader) pair holds one fuse. The first active use lights
it under lock; every later use finds it spent. Touching two fuses in
a circle (A's setup needs B, B's setup needs A) jams the mechanism —
deadlock or half-lit defaults. Constants bypass the fuse box
entirely: their current was wired at the factory.

## 6. Custom loaders as private couriers

A `DirLoader` is a courier serving one street: it asks the main line
first (delegation preserved), delivers only its own addresses via
`findClass` + `defineClass`. Overriding `loadClass` fires the main
line and runs a rival postal service — faster for one neighborhood,
incompatible addresses everywhere else.
