// 07_state_bridge.ink
// Reference story for Lesson 07 (State Bridge).
// Deterministic (no shuffle / RANDOM) so it earns a golden transcript.
//
// Three bridges between ink and the game engine:
//   EXTERNAL discount_for(rep)  -> ink calls OUT to game logic for a number
//   VAR gold                    -> the game OBSERVES this and mirrors it to a HUD
//   (state)                     -> get_state()/set_state() persist the whole story
//
// The story never mentions Godot. It declares what it needs (EXTERNAL) and
// exposes what it changes (VAR gold); the engine binds and observes.

VAR gold = 10
VAR reputation = 2

// The engine supplies this. Given the player's reputation, how many coins off?
// Declared here, bound in GDScript with bind_external_function(...). There is no
// ink fallback: this story's output correctness is validated in the real Godot
// runtime (mise run ink:validate-gd), which binds discount_for. bink (the golden-
// transcript runtime) has no binding API, so this story is excluded from
// transcript capture — the same way shuffle/RANDOM stories are.
EXTERNAL discount_for(rep)

-> market

=== market ===
The market stall is stacked with lanterns. # speaker: Merchant
"A fine lantern is twelve coins," the merchant says. # speaker: Merchant
// Ask the ENGINE to compute a discount from our reputation.
~ temp off = discount_for(reputation)
~ temp price = 12 - off
{off > 0:
    "But for a friend of the guild — {price} coins." # speaker: Merchant
}
+ {gold >= price} [Buy the lantern ({price} coins)] -> buy(price)
+ [Leave it] -> leave

=== buy(cost) ===
// Mutate a story variable. The engine's observer fires on this change.
~ gold = gold - cost
Coins change hands. You lift the lantern. # speaker: Narrator
"Light the way home," the merchant says. # speaker: Merchant
-> ending

=== leave ===
You nod and step back into the crowd. # speaker: Narrator
-> ending

=== ending ===
The square empties as dusk settles. # speaker: Narrator
-> END
