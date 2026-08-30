// 06_tags_as_commands.ink
// Reference story for Lesson 06 (Tags as Commands).
// Deterministic (no shuffle / RANDOM) so it earns a golden transcript.
// Every tagged line carries a COMMAND for the engine to dispatch:
//   # speaker: NAME  -> set the name label above the text
//   # sound: NAME    -> play a sound effect
//   # hidden         -> run the line's side effects but do not show its text
// The engine reads these tags; the story never mentions Godot.

-> well

=== well ===
The old well sits in the village square. # speaker: Narrator
Alfoz the tinker leans against its stones. # speaker: Narrator
"Fancy a look at my wares, traveler?" # speaker: Alfoz # sound: cart_creak
+ [Show me] -> wares
+ [Not today] -> leave

=== wares ===
Alfoz spreads a cloth of trinkets. # speaker: Alfoz # sound: cloth_unfurl
A brass compass catches the light. # speaker: Alfoz
The needle always points home, he claims. # hidden
"Five coins and it's yours." # speaker: Alfoz
+ [Buy the compass] -> buy
+ [Walk away] -> leave

=== buy ===
Coins change hands. # speaker: Narrator # sound: coin_drop
"Safe travels," Alfoz says. # speaker: Alfoz
-> END

=== leave ===
You nod and step back into the crowd. # speaker: Narrator
-> END
