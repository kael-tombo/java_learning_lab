# Reflection: JVM Tuning

## Your box's numbers

Without looking at anyone else's: what are your JVM's `InitialHeapSize`
and `MaxHeapSize`, and what RAM do they imply (x64, x4)? Run the query
inside your deployment, not your laptop — how far apart are the two
answers, and which one governs production?

## Geometry by hand

For your production `-Xmx`: compute young size (third), Eden and
survivor sizes (8/10ths, 1/10ths each), and the 50% survivor fill line in
megabytes. Which allocation in your system sits closest to a boundary the
geometry creates — and does it sit on the cheap side?

## The pooling question

Name one pool in your codebase for small short-lived objects. Against the
~8x TLAB gap, what does the pool win — allocation speed (unlikely),
lifecycle control, or nothing measurable? What would you need to measure
to delete it with confidence, and what stops you?

## Plane attribution drill

Take your last memory incident: which plane (heap, code cache, Metaspace)
did the evidence actually implicate, and which pool or log line proved
it? If the answer is "we raised `-Xmx`," restate what the plane check
would have prescribed instead.

## One experiment, fully specified

Write the next tuning trial as a lab sentence: objective metric, load
generator, mechanism hypothesis, exactly one flag changed (with
before/after values), and the predicted move in the log. If the sentence
needs two flags, split it into two trials — the discipline is the
deliverable, not the outcome.

## Compression-cliff check for your fleet

List your services' `-Xmx` values: does any sit just over 32 GB, paying
uncompressed layout for marginal capacity? For each, write the readout
you expect from `UseCompressedOops` today and the resized value (with
margin) you would trial. One number per service, cheapest memory win
available.
