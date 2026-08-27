// 03_variables_and_conditionals.ink
// Reference story for Lesson 03: Variables & Conditionals
// Demonstrates: read counts, conditional text, alternatives (sequences/cycles/shuffles),
//               VAR, arithmetic, printing, if/else blocks, conditional choices

VAR gold = 15
VAR has_compass = false
VAR has_map = false
VAR shop_visits = 0

-> shop

=== shop ===
~ shop_visits = shop_visits + 1

// --- Conditional greeting: changes on repeat visits (via a counter) ---
{
- shop_visits == 1:
    The old merchant looks up as you enter. "A new face! Welcome to my humble shop."
- shop_visits == 2:
    "Back again?" The merchant smiles. "I knew you'd return."
- else:
    The merchant nods without looking up. "The usual browse?"
}

// --- Cycle: ambient description varies each visit ---
{&The shelves are dusty but well-organized.|A cat sleeps on the counter.|Wind rattles the shuttered window.|The candle flickers, casting long shadows.}

You have {gold} gold coins.

// --- Conditional choices: gated on state ---
+ {not has_compass} [Buy the compass - 5 gold]
    {gold >= 5:
        ~ gold = gold - 5
        ~ has_compass = true
        "A fine instrument," the merchant says, wrapping it in cloth.
    - else:
        "You'll need more coin for that, friend." You put it back.
    }
    -> shop

+ {not has_map} [Buy the map - 8 gold]
    {gold >= 8:
        ~ gold = gold - 8
        ~ has_map = true
        "The northern pass," he says, tapping the parchment. "Dangerous but fast."
    - else:
        "Maps don't come cheap," he shrugs. You leave it on the shelf.
    }
    -> shop

+ {has_compass || has_map} [Ask about the journey north]
    -> journey_advice

+ [Leave the shop]
    -> crossroads

=== journey_advice ===
"Heading north, are you?" The merchant leans in.
{
- has_compass && has_map:
    "With a compass AND a map? You're better prepared than most. Take the high pass — the landmarks will guide you."
- has_map:
    "The map will show you the way, but without a compass you'll struggle in fog. Stick to clear days."
- has_compass:
    "A compass keeps you on course, but without a map you won't know the landmarks. Follow the river — it leads north eventually."
}
-> shop

=== crossroads ===

// --- Shuffle: different traveler each time (random) ---
{~A merchant caravan rattles past.|A lone rider gallops by without a glance.|Two children chase a dog across the road.|An old woman sells wildflowers by the path.}

The road forks here.

* {has_map} [Follow the map north]
    The map shows a clear route through the pass. You set off with confidence.
    -> ending

* {has_compass} [Use the compass to navigate]
    The needle points true north. You follow it into the hills.
    -> ending

* [Head north without aid]
    You pick a direction and hope for the best.
    -> ending

=== ending ===
{
- has_compass && has_map:
    The journey is swift. Your map marks every turn; your compass confirms the heading. By nightfall you've cleared the pass.
- has_compass || has_map:
    The path is uncertain at times, but your {has_compass:compass|map} keeps you from losing your way entirely. You arrive tired but safe.
- else:
    You wander for two days before finding the northern road. Exhausted, hungry, but alive.
}

// --- Print remaining gold ---
{
- gold > 0:
    You still have {gold} gold coins jingling in your pocket.
- else:
    Your pockets are empty — every coin spent on preparation.
}

-> END
