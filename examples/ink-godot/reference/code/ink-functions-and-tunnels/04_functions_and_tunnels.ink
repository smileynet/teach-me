// 04_functions_and_tunnels.ink
// Reference story for Lesson 04: Functions & Tunnels
// Demonstrates: temp variables, knot parameters, functions (with/without return),
//               tunnels (->knot->), ->->, INCLUDE concept, "when to use what"

VAR player_health = 100
VAR gold = 20

-> forest_path

// ─── FUNCTIONS ──────────────────────────────────────────────

=== function roll_dice(sides) ===
    ~ return RANDOM(1, sides)

=== function calculate_damage(base, armor) ===
    ~ temp result = base - armor
    {
    - result < 0:
        ~ return 0
    - else:
        ~ return result
    }

=== function describe_condition(hp) ===
    {
    - hp > 75:
        ~ return "strong"
    - hp > 40:
        ~ return "battered"
    - hp > 10:
        ~ return "barely standing"
    - else:
        ~ return "near death"
    }

=== function gold_text() ===
    {
    - gold > 15:
        Your purse is heavy with coin.
    - gold > 5:
        You have a modest amount of gold.
    - else:
        Your pockets are nearly empty.
    }

// ─── TUNNELS ────────────────────────────────────────────────

=== camp ===
// A reusable rest scene — called as a tunnel from multiple locations
The fire crackles. You rest your legs and eat dried provisions.
~ player_health = player_health + 20
{player_health > 100:
    ~ player_health = 100
}
You feel {describe_condition(player_health)}.
* [Stare into the flames]
    The embers shift. Tomorrow will be harder.
* [Sleep immediately]
    You're unconscious before your head hits the bedroll.
- Dawn breaks. Time to move.
->->

=== battle(enemy, enemy_attack, enemy_armor) ===
// A reusable combat encounter — tunnel with parameters
The {enemy} lunges at you!

~ temp enemy_roll = roll_dice(6) + enemy_attack
~ temp your_roll = roll_dice(6) + 3
~ temp damage_taken = calculate_damage(enemy_roll, 2)
~ temp damage_dealt = calculate_damage(your_roll, enemy_armor)

{
- your_roll > enemy_roll:
    You strike true! The {enemy} takes {damage_dealt} damage.
- your_roll == enemy_roll:
    Blades clash — neither lands a blow.
- else:
    The {enemy} hits you for {damage_taken} damage!
    ~ player_health = player_health - damage_taken
}

You feel {describe_condition(player_health)}.

{player_health <= 0:
    You fall. The {enemy} stands over you.
    -> defeat
}

* [Press the attack] -> battle(enemy, enemy_attack, enemy_armor)
* [Disengage and flee]
    You break away, gasping.
-
->->

// ─── MAIN STORY ─────────────────────────────────────────────

=== forest_path ===
The forest road is quiet. You are {describe_condition(player_health)}.
{gold_text()}

* [Enter the dark grove]
    A wolf emerges from the shadows.
    -> battle("wolf", 2, 1) ->
    The wolf limps away. You find 5 gold on a nearby corpse.
    ~ gold = gold + 5
    -> forest_path

* [Make camp for the night]
    -> camp ->
    -> forest_path

* [Continue to the cave]
    -> cave_entrance

=== cave_entrance ===
The cave mouth yawns before you. Cold air seeps out.
{gold_text()}

* [Enter the cave]
    A goblin shrieks and charges!
    -> battle("goblin", 3, 2) ->
    The goblin collapses. A glint of gold catches your eye.
    ~ gold = gold + 8
    -> cave_entrance

* [Rest outside the cave]
    -> camp ->
    -> cave_entrance

* {gold >= 15} [Pay the troll toll (15 gold)]
    ~ gold = gold - 15
    The troll steps aside with a grunt.
    -> victory

* [Turn back to the forest]
    -> forest_path

=== victory ===
Beyond the troll, the pass opens into sunlit meadows.
You made it through — {describe_condition(player_health)} but alive.
{gold_text()}
-> END

=== defeat ===
Your journey ends here, in the dark.
-> END
