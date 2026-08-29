// 08_production_patterns.ink
// Reference story for Lesson 08 (Production Patterns) — the capstone.
// Deterministic (no shuffle / RANDOM) so it earns a golden transcript.
//
// Shows three patterns a shipped game (Esoteric Ebb, 286 stories) uses at scale,
// in miniature and in PURE ink:
//   * State-bus VARs  -- a few flags carry all cross-topic state (asked_name,
//                        helped_cook). One topic writes them; another reads them.
//   * Hub-and-spoke   -- the tavern is a hub; topics are re-enterable knots you
//                        can visit in any order until you pick Leave.
//   * Stateless shape -- the story tracks NO world state of its own beyond these
//                        flags; a real game keeps them in the engine and pushes
//                        them back in, so each dialog file starts fresh.

VAR asked_name = false
VAR helped_cook = false

-> tavern

// === THE HUB ===
// Re-enterable: every spoke diverts back here, so read counts advance on fresh
// entry (never a self-loop). Sticky (+) choices stay available; the gate on the
// cook's thanks reads a flag another topic set.
=== tavern ===
The tavern is warm and loud. The keeper wipes a glass. # speaker: Narrator
+ [Ask the keeper's name] -> ask_name
+ {asked_name} [Greet her by name] -> greet
+ [Help the cook with the barrels] -> help_cook
+ {helped_cook} [Collect the cook's thanks] -> thanks
+ [Leave] -> leave

// === SPOKE: writes a state-bus flag ===
=== ask_name ===
{asked_name:
    "You already know — I'm Mara," she says, amused. # speaker: Mara
- else:
    "Name's Mara," the keeper says. # speaker: Mara
    ~ asked_name = true
}
-> tavern

// === SPOKE: reads a flag set by another spoke ===
=== greet ===
"Evening, Mara." She nods, pleased you remembered. # speaker: You
-> tavern

// === SPOKE: writes another state-bus flag ===
=== help_cook ===
{helped_cook:
    The cook waves you off — the barrels are already stacked. # speaker: Narrator
- else:
    You haul the barrels to the cellar. The cook grins. # speaker: Cook
    ~ helped_cook = true
}
-> tavern

// === SPOKE: gated on the flag help_cook set ===
=== thanks ===
"For the barrels — here, on the house." # speaker: Cook
A mug of cider slides across the bar. # speaker: Narrator
-> tavern

=== leave ===
You step out into the cool night. # speaker: Narrator
-> END
