# Model Serving - Mental Models

## Restaurant kitchen
- Online serving is cooking to order; batch is catering trays; streaming is a conveyor sushi bar.
- Pick the kitchen that matches the diner's patience, not the chef's preference.
- Mixed workloads need mixed kitchens, with explicit routing between them.

## Tail wags the experience
- Means describe the crowd; tails describe the unlucky diner.
- Interactive budgets are written for the unlucky one, which is why p99 sizes timeouts.
- One slow garnish station stalls the whole plate: find it with version-tagged histograms.

## Batching as carpooling
- Fuller cars move more people per trip but each rider waits longer and arrives later.
- The latency cap is the latest acceptable arrival; it sets the maximum car size.
- Empty cars at night still depart on time: that is the bounded batch-wait.

## Rollouts as dimmer switches
- Shadow watches, canary glows dimly, blue-green flips rooms.
- Brightness rises only while the meters stay green; any red returns the switch.
- The switch itself must be tested, or darkness arrives during the real outage.

## Schemas as contracts
- A menu with fixed dishes and portion sizes, reprinted by version.
- Substitutions need a new printing, not a whisper to the kitchen.
- Old menus stay valid until their holders upgrade: that is backward compatibility.

## Warmup as dress rehearsal
- The curtain never rises on an empty stage: sample scores run before traffic.
- Cold actors forget lines (page faults, empty caches); rehearsal absorbs it.
- Only the stage manager's readiness call opens the doors, never the clock.

## Version tags as name badges
- Every prediction wears the model version that produced it.
- Incident triage reads badges first: which version answered, when, how slowly.
- Badgeless logs are an anonymous crowd: present but unidentifiable.

## Queue depth as waiting room
- Requests queue when arrivals outpace scoring; the room fills before timeouts fire.
- A filling room warns earlier than any latency chart: watch it per version.
- Headroom is spare seating; saturation means standing room only, then the door.

## Cache keys as coat checks
- Tickets must name the exact coat: request plus model and schema versions.
- A new collection (promotion) voids old tickets; stale claims return wrong coats.
- Unversioned tickets hand any coat to any claim: fast, wrong, and confident.
