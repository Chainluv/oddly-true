"""Script for the 8-minute long-form "Nikola Tesla: The Man vs. the Brand" (16:9).
(id, section, spoken text for TTS, display text for subtitles). Sentences must match 1:1 between versions.
Fact-check notes (Nov 2026):
- Edison $50,000 bonus: from Tesla's own account; some historians doubt it -> attributed and hedged.
- 1897: Tesla gave up royalties for a lump sum (~$216,000, per Westinghouse's 1897 annual report via Cheney).
  The "tore up a billion-dollar contract" scene is legend -> treated as a myth.
- Wardenclyffe: $150,000 from J.P. Morgan; property lost to creditors; tower demolished for scrap in 1917.
- Death: Jan 7, 1943, Room 3327, Hotel New Yorker, age 86; belongings taken by the Office of Alien Property.
- 1943 Supreme Court (Marconi v. US) invalidated key Marconi claims citing prior work (Stone, Lodge, Tesla);
  it did not name Tesla the inventor of radio -> myth.
- Tesla Motors: incorporated July 1, 2003 by Eberhard & Tarpenning; Eberhard credited with the name; Musk led
  the Feb 2004 Series A ($6.5M of $7.5M) and became chairman; 2009 settlement allows five co-founders.
- tesla.com held by Stu Grossman since 1992, acquired Feb 2016; Musk said in 2018 it cost $11M and took 10+ years.
- Renamed Tesla, Inc. on Feb 1, 2017. Original Roadster used an AC induction motor.
"""

SECTIONS = ["cold", "title", "man", "motor", "war", "fall", "myths", "name", "outro"]

P = [
    # ---------------- cold open
    ("c1", "cold", "The most famous name in electric cars belongs to a man who died broke.",
     "The most famous name in electric cars belongs to a man who died broke."),
    ("c2", "cold", "January seventh, nineteen forty-three. New York City. In room thirty-three twenty-seven of the Hotel New Yorker, an eighty-six-year-old inventor dies alone, deep in debt.",
     "January 7th, 1943. New York City. In room 3327 of the Hotel New Yorker, an 86-year-old inventor dies alone, deep in debt."),
    ("c3", "cold", "Sixty years later, a startup in California puts his name on a car company. Today, it's one of the most valuable car companies on Earth.",
     "Sixty years later, a startup in California puts his name on a car company. Today, it's one of the most valuable car companies on Earth."),
    ("c5", "cold", "And the strangest part? For years, the company named after him didn't even own its own name online. We'll get to that.",
     "And the strangest part? For years, the company named after him didn't even own its own name online. We'll get to that."),
    ("c4", "cold", "This is the story of Nikola Tesla. The man, the myths, and the brand.",
     "This is the story of Nikola Tesla. The man, the myths, and the brand."),
    # ---------------- the immigrant
    ("m1", "man", "Nikola Tesla was born in eighteen fifty-six, in a small village in what is now Croatia, to a Serbian family. His father was a priest. His mother, he said, invented gadgets for the household.",
     "Nikola Tesla was born in 1856, in a small village in what is now Croatia, to a Serbian family. His father was a priest. His mother, he said, invented gadgets for the household."),
    ("m2", "man", "He studied engineering, worked for telephone and electric companies in Europe, and in eighteen eighty-four, he sailed to New York, with almost nothing in his pockets.",
     "He studied engineering, worked for telephone and electric companies in Europe, and in 1884, he sailed to New York, with almost nothing in his pockets."),
    ("m7", "man", "He had a remarkable memory. He claimed he could picture entire machines in his head, and test them there, before building anything.",
     "He had a remarkable memory. He claimed he could picture entire machines in his head, and test them there, before building anything."),
    ("m3", "man", "He landed a job working for Thomas Edison.", "He landed a job working for Thomas Edison."),
    ("m4", "man", "And this is where the first famous story comes in. According to Tesla, Edison promised him fifty thousand dollars to improve his generators. When Tesla delivered, Edison supposedly laughed, and told him he didn't understand American humor.",
     "And this is where the first famous story comes in. According to Tesla, Edison promised him $50,000 to improve his generators. When Tesla delivered, Edison supposedly laughed, and told him he didn't understand American humor."),
    ("m5", "man", "That story comes from Tesla himself, and some historians doubt the details. But either way, he quit within the year.",
     "That story comes from Tesla himself, and some historians doubt the details. But either way, he quit within the year."),
    ("m6", "man", "His first company of his own pushed him out. By his own account, he ended up digging ditches for a living.",
     "His first company of his own pushed him out. By his own account, he ended up digging ditches for a living."),
    # ---------------- the motor
    ("o1", "motor", "But Tesla had an idea he'd carried since his student days: a motor that ran on alternating current, with no brushes and no sparking contacts, almost nothing to wear out.",
     "But Tesla had an idea he'd carried since his student days: a motor that ran on alternating current, with no brushes and no sparking contacts, almost nothing to wear out."),
    ("o2", "motor", "The trick was something called a rotating magnetic field. Feed alternating currents into coils around a ring, slightly out of step with each other, and the magnetic field itself spins. Put a metal rotor in the middle, and the field drags it around.",
     "The trick was something called a rotating magnetic field. Feed alternating currents into coils around a ring, slightly out of step with each other, and the magnetic field itself spins. Put a metal rotor in the middle, and the field drags it around."),
    ("o3", "motor", "In eighteen eighty-eight, he patented his A C induction motor, and presented it to the country's top electrical engineers.",
     "In 1888, he patented his AC induction motor, and presented it to the country's top electrical engineers."),
    ("o4", "motor", "One man was paying very close attention: George Westinghouse. He licensed Tesla's patents, and hired him. Remember this motor. It's coming back, more than a century later.",
     "One man was paying very close attention: George Westinghouse. He licensed Tesla's patents, and hired him. Remember this motor. It's coming back, more than a century later."),
    # ---------------- the war of the currents
    ("x1", "war", "There was just one problem. Edison had bet everything on direct current, and he wasn't giving up without a fight.",
     "There was just one problem. Edison had bet everything on direct current, and he wasn't giving up without a fight."),
    ("x2", "war", "It became known as the War of the Currents. Edison's camp warned that alternating current was deadly, and pointed to its use in the first electric chair.",
     "It became known as the War of the Currents. Edison's camp warned that alternating current was deadly, and pointed to its use in the first electric chair."),
    ("x8", "war", "An engineer allied with Edison's side even electrocuted animals in public demonstrations, to show how dangerous A C could be.",
     "An engineer allied with Edison's side even electrocuted animals in public demonstrations, to show how dangerous AC could be."),
    ("x9", "war", "Tesla fought back with showmanship. In his lectures, he let high-frequency current pass through his own body, lighting up lamps in his hands.",
     "Tesla fought back with showmanship. In his lectures, he let high-frequency current pass through his own body, lighting up lamps in his hands."),
    ("x3", "war", "But A C had a huge advantage. It could be sent long distances efficiently. Direct current, back then, couldn't.",
     "But AC had a huge advantage. It could be sent long distances efficiently. Direct current, back then, couldn't."),
    ("x4", "war", "In eighteen ninety-three, Westinghouse lit up the Chicago World's Fair. Millions of visitors saw a glowing white city running on alternating current.",
     "In 1893, Westinghouse lit up the Chicago World's Fair. Millions of visitors saw a glowing white city running on alternating current."),
    ("x5", "war", "Then came Niagara Falls. In eighteen ninety-six, power generated at the falls, using Tesla's system, reached the city of Buffalo, more than twenty miles away.",
     "Then came Niagara Falls. In 1896, power generated at the falls, using Tesla's system, reached the city of Buffalo, more than 20 miles away."),
    ("x6", "war", "Alternating current won. It's the kind of power coming out of your wall right now.",
     "Alternating current won. It's the kind of power coming out of your wall right now."),
    ("x7", "war", "So Tesla should have been rich, right?", "So Tesla should have been rich, right?"),
    # ---------------- the fall
    ("f1", "fall", "Here's where it goes wrong. Westinghouse's company ran into serious money trouble. Tesla agreed to give up his royalties, and in eighteen ninety-seven, he took a lump sum of about two hundred sixteen thousand dollars for his patents.",
     "Here's where it goes wrong. Westinghouse's company ran into serious money trouble. Tesla agreed to give up his royalties, and in 1897, he took a lump sum of about $216,000 for his patents."),
    ("f2", "fall", "That was a lot of money in eighteen ninety-seven. But it was a tiny slice of what those royalties could have become.",
     "That was a lot of money in 1897. But it was a tiny slice of what those royalties could have become."),
    ("f7", "fall", "And in eighteen ninety-five, a fire tore through his New York laboratory, destroying years of equipment and notes.",
     "And in 1895, a fire tore through his New York laboratory, destroying years of equipment and notes."),
    ("f3", "fall", "Then Tesla went all in on his biggest dream: wireless power. On Long Island, he built a giant tower called Wardenclyffe, funded with a hundred and fifty thousand dollars from the banker J. P. Morgan.",
     "Then Tesla went all in on his biggest dream: wireless power. On Long Island, he built a giant tower called Wardenclyffe, funded with $150,000 from the banker J. P. Morgan."),
    ("f4", "fall", "The plan was to send messages, and eventually power, through the air and the earth itself. But the money ran out, and Morgan wouldn't invest more.",
     "The plan was to send messages, and eventually power, through the air and the earth itself. But the money ran out, and Morgan wouldn't invest more."),
    ("f5", "fall", "The tower never did what he hoped. Tesla lost the property to his creditors, and in nineteen seventeen, the tower was demolished for scrap.",
     "The tower never did what he hoped. Tesla lost the property to his creditors, and in 1917, the tower was demolished for scrap."),
    ("f6", "fall", "For the rest of his life, Tesla moved from hotel to hotel, often behind on the bills, feeding pigeons, and announcing inventions that never appeared.",
     "For the rest of his life, Tesla moved from hotel to hotel, often behind on the bills, feeding pigeons, and announcing inventions that never appeared."),
    ("f8", "fall", "He even told his biographer that he loved one white pigeon, the way a man loves a woman.",
     "He even told his biographer that he loved one white pigeon, the way a man loves a woman."),
    # ---------------- myth vs fact
    ("y1", "myths", "And that's where the myths start piling up. Let's sort out a few.", "And that's where the myths start piling up. Let's sort out a few."),
    ("y2", "myths", "Myth number one: Tesla tore up a contract worth billions, to save his friend Westinghouse. What we can document is the buyout: a lump sum instead of royalties. The dramatic tearing moment is much harder to prove.",
     "Myth number one: Tesla tore up a contract worth billions, to save his friend Westinghouse. What we can document is the buyout: a lump sum instead of royalties. The dramatic tearing moment is much harder to prove."),
    ("y3", "myths", "Myth number two: he built a death ray. In the nineteen thirties, he told reporters he'd designed a beam that could stop armies from far away. There's no evidence he ever built one.",
     "Myth number two: he built a death ray. In the 1930s, he told reporters he'd designed a beam that could stop armies from far away. There's no evidence he ever built one."),
    ("y4", "myths", "Myth number three: the Supreme Court declared Tesla the inventor of radio. In nineteen forty-three, the court did knock out key parts of Marconi's radio patent, citing earlier work by Tesla and others. But it never named Tesla the inventor of radio.",
     "Myth number three: the Supreme Court declared Tesla the inventor of radio. In 1943, the court did knock out key parts of Marconi's radio patent, citing earlier work by Tesla and others. But it never named Tesla the inventor of radio."),
    ("y5", "myths", "And the big one: Tesla invented everything. He didn't. But he did help build the electric world we live in. There's even a scientific unit of magnetism called the tesla.",
     "And the big one: Tesla invented everything. He didn't. But he did help build the electric world we live in. There's even a scientific unit of magnetism called the tesla."),
    ("y6", "myths", "He died in nineteen forty-three, in that hotel room. Afterward, the government took his belongings and papers.",
     "He died in 1943, in that hotel room. Afterward, the government took his belongings and papers."),
    # ---------------- the name returns
    ("n1", "name", "Now fast forward sixty years. July first, two thousand three. Two engineers in California, Martin Eberhard and Marc Tarpenning, start an electric car company.",
     "Now fast forward sixty years. July 1st, 2003. Two engineers in California, Martin Eberhard and Marc Tarpenning, start an electric car company."),
    ("n2", "name", "Eberhard is credited with choosing the name: Tesla Motors. A tribute to the inventor. But also a perfect fit, because their first car, the Roadster, would run on an A C induction motor. The same kind of motor Tesla patented in eighteen eighty-eight.",
     "Eberhard is credited with choosing the name: Tesla Motors. A tribute to the inventor. But also a perfect fit, because their first car, the Roadster, would run on an AC induction motor. The same kind of motor Tesla patented in 1888."),
    ("n3", "name", "Elon Musk joined in two thousand four. He led the first big funding round, with six and a half million dollars of his own money, and became chairman. Later, he became the CEO.",
     "Elon Musk joined in 2004. He led the first big funding round, with $6.5 million of his own money, and became chairman. Later, he became the CEO."),
    ("n7", "name", "The Roadster finally hit the road in two thousand eight. Only about twenty-five hundred were ever built.",
     "The Roadster finally hit the road in 2008. Only about 2,500 were ever built."),
    ("n8", "name", "It was built on a modified Lotus sports car chassis, packed with thousands of small, laptop-style battery cells.",
     "It was built on a modified Lotus sports car chassis, packed with thousands of small, laptop-style battery cells."),
    ("n4", "name", "And then it got messy. Eberhard sued. The settlement, in two thousand nine, allowed five people to call themselves co-founders, Musk included.",
     "And then it got messy. Eberhard sued. The settlement, in 2009, allowed five people to call themselves co-founders, Musk included."),
    ("n5", "name", "Here's the part that sounds made up. For years, the company didn't even own tesla dot com. That address had belonged to a man named Stu Grossman since nineteen ninety-two. Tesla finally got it in two thousand sixteen. Musk later said it cost eleven million dollars, and took more than a decade.",
     "Here's the part that sounds made up. For years, the company didn't even own tesla.com. That address had belonged to a man named Stu Grossman since 1992. Tesla finally got it in 2016. Musk later said it cost $11 million, and took more than a decade."),
    ("n6", "name", "In two thousand seventeen, the company dropped Motors from its name. Today, it's simply Tesla.",
     "In 2017, the company dropped \"Motors\" from its name. Today, it's simply Tesla."),
    # ---------------- outro
    ("q1", "outro", "So here's the full circle. A man who died broke, in debt, alone in a hotel room.",
     "So here's the full circle. A man who died broke, in debt, alone in a hotel room."),
    ("q2", "outro", "And more than a century after he patented his motor, his name became one of the most famous brands in the world.",
     "And more than a century after he patented his motor, his name became one of the most famous brands in the world."),
    ("q3", "outro", "No way.", "No way."),
    ("q4", "outro", "If you want more true stories that sound made up, subscribe. And if you liked this one, watch another one next, because they're just as wild.",
     "If you want more true stories that sound made up, subscribe. And if you liked this one, watch another one next, because they're just as wild."),
]

SPEED = 0.88           # natural storytelling pace (same as molasses-long v2)
PAUSE_DEFAULT = 0.7
PAUSE_SECTION = 1.0
PAUSE_AFTER = {"c4": 0.8, "m3": 0.7, "o4": 1.2, "x7": 2.4, "f8": 1.2, "y6": 1.4, "n6": 1.0, "q2": 1.0, "q3": 1.2}
TITLE_CARD = 2.6        # after the cold open
CHAPTER_CARD = 1.6      # chapter title card at the start of each later section
CHAPTERS = {"man": "THE IMMIGRANT", "motor": "THE MOTOR", "war": "THE WAR OF THE CURRENTS", "fall": "THE FALL",
            "myths": "MYTH VS. FACT", "name": "THE NAME RETURNS"}
START_PAD = 0.6
END_PAD = 15.0          # end-screen hold (YouTube end screens run up to 20s)
