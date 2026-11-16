"""Script for the 8-minute long-form Great Molasses Flood episode (16:9).
Each paragraph: (id, section, spoken text for TTS, display text for subtitles). Sentences must match 1:1 between the
spoken and display versions (they are split on . ? !) so subtitle timing can follow the voice.
Fact edits vs. the draft: the unsourced ladder anecdote is replaced with the documented Engine 31 firehouse rescue;
"some victims weren't found for months" becomes the documented single case (Cesare Nicolo, ~4 months)."""

SECTIONS = ["cold", "title", "tank", "storm", "wave", "midroll", "trap", "cleanup", "blame", "legacy", "outro"]

P = [
    # ---------------- cold open
    ("c1", "cold", "January fifteenth, nineteen nineteen. Boston. It's lunchtime, it's unusually warm for winter, and people are out enjoying it.",
     "January 15th, 1919. Boston. It's lunchtime, it's unusually warm for winter, and people are out enjoying it."),
    ("c2", "cold", "Then they hear a sound like a machine gun. The ground shakes. And a wall of something dark and thick, taller than a two-story house, comes rolling down the street at thirty-five miles an hour.",
     "Then they hear a sound like a machine gun. The ground shakes. And a wall of something dark and thick, taller than a two-story house, comes rolling down the street at 35 miles an hour."),
    ("c3", "cold", "It isn't water. It's molasses. And before the day is over, it will kill twenty-one people.",
     "It isn't water. It's molasses. And before the day is over, it will kill 21 people."),
    # ---------------- the tank
    ("t1", "tank", "In nineteen nineteen the North End was a crowded, working-class neighborhood, mostly Italian and Irish immigrant families packed into tenements near the harbor.",
     "In 1919 the North End was a crowded, working-class neighborhood, mostly Italian and Irish immigrant families packed into tenements near the harbor."),
    ("t2", "tank", "Right in the middle of it, on Commercial Street, stood a giant steel tank: fifty feet tall and ninety feet across. It belonged to the Purity Distilling Company, part of a bigger corporation called United States Industrial Alcohol.",
     "Right in the middle of it, on Commercial Street, stood a giant steel tank: 50 feet tall and 90 feet across. It belonged to the Purity Distilling Company, part of a bigger corporation called United States Industrial Alcohol."),
    ("t3", "tank", "Inside was molasses. And not for baking. Molasses could be fermented into industrial alcohol, which was used to make munitions during World War One. That made it very profitable.",
     "Inside was molasses. And not for baking. Molasses could be fermented into industrial alcohol, which was used to make munitions during World War I. That made it very profitable."),
    ("t4", "tank", "The tank went up in nineteen fifteen, and it was rushed. The man in charge of building it was a company treasurer with no engineering background. He couldn't even read a blueprint. By most accounts, the tank was never properly tested by filling it with water before the molasses went in.",
     "The tank went up in 1915, and it was rushed. The man in charge of building it was a company treasurer with no engineering background. He couldn't even read a blueprint. By most accounts, the tank was never properly tested by filling it with water before the molasses went in."),
    ("t5", "tank", "And from the start, it leaked.", "And from the start, it leaked."),
    ("t6", "tank", "Molasses seeped through the seams so badly that local families brought buckets to collect it for free. Neighbors said the tank groaned and rumbled. And the company's fix? They painted the tank brown, so the leaks would be harder to see.",
     "Molasses seeped through the seams so badly that local families brought buckets to collect it for free. Neighbors said the tank groaned and rumbled. And the company's fix? They painted the tank brown, so the leaks would be harder to see."),
    # ---------------- the perfect storm
    ("s1", "storm", "Now here's the twist. By January nineteen nineteen, the war was over, but the alcohol business was facing a bigger threat: Prohibition. The amendment banning alcohol was about to be ratified, and producers wanted to make as much as they could while they still had time.",
     "Now here's the twist. By January 1919, the war was over, but the alcohol business was facing a bigger threat: Prohibition. The amendment banning alcohol was about to be ratified, and producers wanted to make as much as they could while they still had time."),
    ("s2", "storm", "So the tank was close to full, holding about two point three million gallons.",
     "So the tank was close to full, holding about 2.3 million gallons."),
    ("s3", "storm", "Then the weather got weird. Just a day or two earlier, Boston had been bitterly cold, close to zero degrees. On the morning of the fifteenth, the temperature shot up past forty. A fresh shipment of warmer molasses had recently been pumped in on top of the cold stuff already inside.",
     "Then the weather got weird. Just a day or two earlier, Boston had been bitterly cold, close to zero degrees. On the morning of the 15th, the temperature shot up past 40. A fresh shipment of warmer molasses had recently been pumped in on top of the cold stuff already inside."),
    ("s4", "storm", "Warm molasses expands. It ferments. It builds pressure. And all of that was pushing against steel that was already too thin, held together by rivets that were already failing.",
     "Warm molasses expands. It ferments. It builds pressure. And all of that was pushing against steel that was already too thin, held together by rivets that were already failing."),
    # ---------------- the wave
    ("w1", "wave", "Around twelve thirty in the afternoon, the tank gave way.", "Around 12:30 in the afternoon, the tank gave way."),
    ("w2", "wave", "Witnesses heard a deep rumble, then a rapid popping as rivets shot out of the steel like bullets. The walls split open, and roughly thirteen thousand tons of molasses came out all at once.",
     "Witnesses heard a deep rumble, then a rapid popping as rivets shot out of the steel like bullets. The walls split open, and roughly 13,000 tons of molasses came out all at once."),
    ("w3", "wave", "Molasses is about forty percent heavier than water. So this wasn't a spill. It was a wave. Estimates vary, but many accounts put it around twenty-five feet high at first, moving at about thirty-five miles an hour.",
     "Molasses is about 40 percent heavier than water. So this wasn't a spill. It was a wave. Estimates vary, but many accounts put it around 25 feet high at first, moving at about 35 miles an hour."),
    ("w4", "wave", "It flattened buildings. It ripped part of the elevated railway off its supports. It knocked a firehouse off its foundation. Wagons, horses and people were swept away or buried. At the crushed firehouse, rescuers spent hours cutting through the floorboards to reach the men trapped beneath.",
     "It flattened buildings. It ripped part of the elevated railway off its supports. It knocked a firehouse off its foundation. Wagons, horses and people were swept away or buried. At the crushed firehouse, rescuers spent hours cutting through the floorboards to reach the men trapped beneath."),
    ("w5", "wave", "And that was just the first few seconds.", "And that was just the first few seconds."),
    ("w6", "wave", "Because the molasses was about to do something even worse.", "Because the molasses was about to do something even worse."),
    # ---------------- the trap
    ("r1", "trap", "When molasses flows fast, it acts almost like a liquid. But once that wave spread out and hit the cold January air, it started to cool. And cold molasses thickens.",
     "When molasses flows fast, it acts almost like a liquid. But once that wave spread out and hit the cold January air, it started to cool. And cold molasses thickens."),
    ("r2", "trap", "People who survived the impact were now stuck in it, like flies on flypaper. The more they struggled, the more tired they got. Rescuers wading in got stuck too.",
     "People who survived the impact were now stuck in it, like flies on flypaper. The more they struggled, the more tired they got. Rescuers wading in got stuck too."),
    ("r3", "trap", "Sailors from a nearby training ship were among the first to rush in, along with police, firefighters and the Red Cross. They pulled people out of a brown, sticky mess that was waist-deep in places. Rescue work went on for days.",
     "Sailors from a nearby training ship were among the first to rush in, along with police, firefighters and the Red Cross. They pulled people out of a brown, sticky mess that was waist-deep in places. Rescue work went on for days."),
    ("r4", "trap", "Twenty-one people died, some of them children. Around a hundred and fifty were injured. One victim wasn't found for nearly four months.",
     "21 people died, some of them children. Around 150 were injured. One victim wasn't found for nearly four months."),
    # ---------------- the cleanup
    ("k1", "cleanup", "Cleaning it up was a nightmare. Crews eventually used salt water from the harbor to break the molasses down, because fresh water barely touched it.",
     "Cleaning it up was a nightmare. Crews eventually used salt water from the harbor to break the molasses down, because fresh water barely touched it."),
    ("k2", "cleanup", "The mess got tracked everywhere: onto streetcars, into homes, across the city. Boston Harbor reportedly ran brown for months.",
     "The mess got tracked everywhere: onto streetcars, into homes, across the city. Boston Harbor reportedly ran brown for months."),
    ("k3", "cleanup", "And people who lived in the North End for decades afterward swore that on hot summer days, you could still smell molasses.",
     "And people who lived in the North End for decades afterward swore that on hot summer days, you could still smell molasses."),
    # ---------------- the blame game
    ("b1", "blame", "So who was responsible?", "So who was responsible?"),
    ("b2", "blame", "The company had an answer ready: anarchists. They claimed someone had bombed the tank. And in nineteen nineteen, during a wave of real anarchist bombings, that wasn't an impossible story to sell.",
     "The company had an answer ready: anarchists. They claimed someone had bombed the tank. And in 1919, during a wave of real anarchist bombings, that wasn't an impossible story to sell."),
    ("b3", "blame", "But the victims weren't buying it. One hundred nineteen plaintiffs, including families of the dead, banded together and sued United States Industrial Alcohol. It became one of the first major class-action-style lawsuits against a big American corporation.",
     "But the victims weren't buying it. 119 plaintiffs, including families of the dead, banded together and sued United States Industrial Alcohol. It became one of the first major class-action-style lawsuits against a big American corporation."),
    ("b4", "blame", "The case dragged on for years. A court-appointed auditor heard testimony from thousands of witnesses and a long list of experts, including engineers and scientists arguing over metal, pressure and rivets.",
     "The case dragged on for years. A court-appointed auditor heard testimony from thousands of witnesses and a long list of experts, including engineers and scientists arguing over metal, pressure and rivets."),
    ("b5", "blame", "In the end, the ruling was clear: there was no bomb. The tank was simply too weak for what it held, and the company had cut corners.",
     "In the end, the ruling was clear: there was no bomb. The tank was simply too weak for what it held, and the company had cut corners."),
    ("b6", "blame", "The company was ordered to pay about six hundred twenty-eight thousand dollars in damages, which is millions in today's money.",
     "The company was ordered to pay about $628,000 in damages, which is millions in today's money."),
    # ---------------- the legacy
    ("l1", "legacy", "Here's why this story still matters, and why you probably benefit from it without knowing.",
     "Here's why this story still matters, and why you probably benefit from it without knowing."),
    ("l2", "legacy", "After the flood, Massachusetts and then other states began requiring that engineers and architects check their calculations, sign off on their plans, and have projects inspected. Rules we now take for granted in construction trace back, in part, to a tank of syrup that burst in Boston.",
     "After the flood, Massachusetts and then other states began requiring that engineers and architects check their calculations, sign off on their plans, and have projects inspected. Rules we now take for granted in construction trace back, in part, to a tank of syrup that burst in Boston."),
    ("l3", "legacy", "Today the spot where the tank stood is a park with ball fields. The only sign of what happened is a small plaque that most people walk right past.",
     "Today the spot where the tank stood is a park with ball fields. The only sign of what happened is a small plaque that most people walk right past."),
    # ---------------- outro
    ("o1", "outro", "Twenty-one lives lost, all because a company painted over its warning signs instead of fixing them.",
     "21 lives lost, all because a company painted over its warning signs instead of fixing them."),
    ("o2", "outro", "A wave of molasses. A cover-up story about bombers. And a lawsuit that helped make the buildings around you safer.",
     "A wave of molasses. A cover-up story about bombers. And a lawsuit that helped make the buildings around you safer."),
    ("o3", "outro", "No way.", "No way."),
    ("o4", "outro", "If you want more true stories that sound made up, subscribe. And if you liked this one, watch another one next, because they're just as wild.",
     "If you want more true stories that sound made up, subscribe. And if you liked this one, watch another one next, because they're just as wild."),
]

# pauses (seconds) after a paragraph: longer at section ends, a held beat for the cliffhanger / mid-roll
SPEED = 0.78           # storytelling pace
PAUSE_DEFAULT = 0.9
PAUSE_SECTION = 2.2
PAUSE_AFTER = {"c3": 0.8, "t5": 1.2, "w6": 3.0, "r4": 2.6, "b1": 1.2, "o2": 1.4, "o3": 1.6}
TITLE_CARD = 3.0        # after the cold open
CHAPTER_CARD = 2.6      # chapter title card at the start of each later section
CHAPTERS = {"tank": "THE TANK", "storm": "THE PERFECT STORM", "wave": "THE WAVE", "trap": "THE TRAP",
            "cleanup": "THE CLEANUP", "blame": "THE BLAME GAME", "legacy": "THE LEGACY"}
START_PAD = 0.6
END_PAD = 4.0           # end card hold after the last line
