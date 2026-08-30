// 02_choices_and_weave.ink
// Reference story for Lesson 02: Choices, Stitches & Weave
// Demonstrates: once-only/sticky choices, bracket text suppression, stitches,
//               gathers, nested choices, fallback choices, chained weave

-> market_square

=== market_square ===
The market square bustles with traders and travelers. Three stalls catch your eye.

// --- Sticky choices: the player can browse multiple stalls ---
+ [Browse the weapon stall] -> market_square.weapons
+ [Browse the potion stall] -> market_square.potions
+ [Browse the map stall] -> market_square.maps
* {weapons || potions || maps} [Leave the market] -> tavern

// --- Stitches organize sub-locations within the knot ---
= weapons
The blacksmith grins. "Looking for steel, traveler?"

// --- Bracket syntax: text before [] shows in both; inside [] shows only in choice; after shows only in output ---
* "Show me your swords[."]," you say.
  He unsheathes a curved blade, its edge catching the light.
* "Just looking[."]," you mutter.
  He shrugs and turns to another customer.
+ ->
  You have nothing more to ask here.

// --- Gather: branches rejoin here ---
- You step back into the square.
-> market_square

= potions
Glass bottles line the stall, filled with luminous liquids.

* ["What's the blue one?"]
  "Restores stamina," the merchant says. "Five coins."
* ["What's the red one?"]
  "Heals wounds. Ten coins — worth every copper."
* ["I'll pass for now."]
  The merchant nods, unbothered.
+ ->
  The bottles glint, but you've seen enough.

- The colors swirl as you turn away.
-> market_square

= maps
An old cartographer peers at you over half-moon spectacles.

// --- Nested choices: ** is a sub-choice within a * branch ---
* "Do you have maps of the northern pass?"
  "Indeed!" He unfurls a parchment.
  * * [Buy the map for three coins]
      "A wise purchase." He rolls it up neatly for you.
  * * [It's too expensive]
      "Perhaps next time," he says, folding it away.
  -- You thank him for his time.
* "Any news from the road[?"]?" you ask.
  "Bandits near the bridge," he whispers. "Take the forest path."
+ ->
  The cartographer returns to his charts.

- You leave the stall with plenty to think about.
-> market_square

=== tavern ===
The tavern is warm and loud. A bard plays in the corner.

// --- Chained weave: multiple choice-gather pairs in sequence ---
* [Sit at the bar]
  You slide onto a stool, the wood worn smooth by years of use.
* [Find a quiet corner]
  You duck behind a pillar, away from the noise.
+ ->

- The barkeep catches your eye. "What'll it be?"

* "Ale[."]," you say.
  She pours a foaming mug and slides it across.
* "Water[."], please."
  "Smart traveler," she says, filling a clay cup.
* "Information[."]," you say quietly.
  She leans in. "That depends on the coin."
+ ->

- You drink in silence, watching the room.

// --- Once-only choices that build a conversation ---
* "Who's the bard?" you ask the barkeep.
  "Calls herself Wren. Been here a week."
  -> tavern
* "Any rooms available?"
  "Last one on the left, upstairs. Two coins a night."
  -> tavern
+ [Stop talking and decide] -> tavern_end

= tavern_end
The candle on your table gutters low. Time to decide.

* [Head upstairs to rest] -> rest
* [Slip out into the night] -> night_road

=== rest ===
You climb the narrow stairs and find your room. The bed is simple but clean.
Tomorrow, the northern pass awaits.
-> END

=== night_road ===
The cobblestones are slick with evening rain. The forest path the cartographer mentioned — it begins just past the bridge.
You pull your cloak tight and walk into the dark.
-> END
