"""The page's content as data: 20 November 2026, sourced from that day's reporting.

Every story is a real event of 20 November 2026 (or first reported that day),
with the outlet that carried it. The renderer draws whatever is here, so the
story count, the region tabs and the numbers strip are all computed from it.
"""

import re

DAY = "FRIDAY 20 NOVEMBER 2026"
DAY_BIG = "20 NOVEMBER 2026"
DAY_SHORT = "20 NOV 2026"
PAPER = "THE WORLD IN ONE DAY"
EDITION = "No. 1,214"

REGIONS = [
    ("WORLD", (150, 24, 24)),
    ("EUROPE", (30, 84, 140)),
    ("ASIA", (18, 96, 72)),
    ("AMERICAS", (120, 60, 130)),
    ("MIDEAST", (150, 96, 20)),
    ("AFRICA", (90, 70, 40)),
    ("CLIMATE", (30, 110, 120)),
]

# headline, kicker (place + region), body (two tight sentences), art
STORIES = [
    # ---------------- leads: the two biggest things that happened
    dict(
        kicker="SHENZHEN · WORLD",
        headline="Xi, Trump and Putin sign a “declaration toward peace”",
        body="The three leaders met face to face for the first time, in a villa "
             "beside a lake in Shenzhen, and issued a joint declaration saying "
             "nuclear war “cannot be won and must never be fought”. It promised "
             "UN reform and more refined petroleum, and said nothing about Ukraine.",
        art="flags",
    ),
    dict(
        kicker="BERLIN · EUROPE",
        headline="Kushner says Trump open to an Article 5 guarantee for Kyiv",
        body="At a summit of the coalition of the willing, Trump's son-in-law said "
             "Washington would consider a Nato-style mutual defence pledge for "
             "Ukraine. Macron urged allies to “reopen the question” of Nato "
             "membership and to deliver air defence now.",
        art="chart",
        art_bars=[("PATRIOT", 3.2), ("SAMP/T", 1.4), ("IRIS-T", 2.1)],
        art_cap="AIR-DEFENCE PLEDGES, BILLIONS",
    ),
    # ---------------- the day's other front pages
    dict(
        kicker="KYIV · EUROPE",
        headline="Daytime drone strikes damage Saint Volodymyr Cathedral",
        body="Russian attacks through Thursday killed one person and hurt at least "
             "four, and damaged the cathedral plus the Austrian and Dutch "
             "embassies. Debris fell on the foreign ministry and the Brazilian "
             "embassy, Ukraine's foreign minister said.",
        art="dome",
    ),
    dict(
        kicker="MOSCOW · EUROPE",
        headline="Putin vows a “painful” reply to the Kerch Bridge attack",
        body="Ukraine struck the bridge to Crimea for the third time this week. "
             "Putin said he had considered local ceasefires until it was hit, and "
             "that after the strikes “we will not negotiate”.",
    ),
    dict(
        kicker="WASHINGTON · AMERICAS",
        headline="Van Hollen moves to unseat Schumer as Senate Democratic leader",
        body="The Maryland senator said he would challenge a nine-year incumbent, "
             "arguing the midterms were a mandate to “reject the status quo”. "
             "Several colleagues and donors endorsed the bid.",
    ),
    dict(
        kicker="NEW YORK · AMERICAS",
        headline="Stocks slide again as the AI trade cracks",
        body="The S&P 500 fell about 2 per cent for a third straight session, its "
             "longest losing run since 2024, and the MSCI world index closed at "
             "its lowest since April. Chipmakers led the decline.",
        art="chart",
    ),
    dict(
        kicker="SAN FRANCISCO · AMERICAS",
        headline="Anthropic prices its listing at about $107bn",
        body="The AI group sold 980m shares at $83, and the stock closed up about "
             "17 per cent on its first day. It is the largest technology float "
             "since 2021.",
        art="coin",
        art_big="$107bn",
        art_cap="FIRST-DAY LISTING",
    ),
    dict(
        kicker="ANTALYA · CLIMATE",
        headline="Cop31 ends with no text adopted",
        body="Delegates left the Turkish resort without an agreed decision after "
             "two weeks of talks on finance and fossil-fuel language. The "
             "presidency said consultations would continue into next year.",
        art="dial",
        art_frac=0.16,
        art_big="$1tn",
        art_cap="finance ask, unmet",
        art_arc="COP31",
    ),
    dict(
        kicker="NEW DELHI · ASIA",
        headline="Delhi tightens pollution curbs as PM 2.5 hits 201",
        body="The city government doubled parking fees, ordered remote work where "
             "possible, restricted high-emission vehicles and banned "
             "dust-producing construction. Schools stayed open but outdoor sport "
             "was stopped.",
    ),
    dict(
        kicker="DHAKA · ASIA",
        headline="Garment workers clash with police over pay",
        body="At least 20 people, four of them police, were injured in Mirpur as "
             "ready-made garment workers protested low wages and rising prices. "
             "The government said it would form a wage board.",
    ),
    dict(
        kicker="DHAKA · ASIA",
        headline="Thousands protest in New Delhi over voter rolls",
        body="Demonstrators called for the election commissioner to resign, saying "
             "revisions to voter lists fall hardest on opposition voters. The "
             "commission denies the charge.",
    ),
    dict(
        kicker="SOFIA · EUROPE",
        headline="Iotova re-elected Bulgarian president",
        body="The incumbent beat former acting prime minister Andrey Gyurov in a "
             "second round, and he conceded once polls closed. Turnout was the "
             "highest since 2021.",
    ),
    dict(
        kicker="LISBON · EUROPE",
        headline="Riot police clear Lisbon and Porto housing camps",
        body="Thirteen people were arrested for refusing to disperse in Rossio "
             "Square, and thirteen officers were hurt. Activists said more than "
             "30 protesters were injured.",
    ),
    dict(
        kicker="WASHINGTON · AMERICAS",
        headline="FBI says North Korea ran the $6bn Binance theft",
        body="The bureau attributed the exchange hack to the Lazarus Group, which "
             "also hit Dubai-based Bybit last year. Prosecutors are preparing "
             "sanctions on the wallets involved.",
    ),
    dict(
        kicker="GREENACRES · AMERICAS",
        headline="Nine die as Learjet 60 crashes in Florida",
        body="The business jet, bound for The Bahamas, came down in Greenacres "
             "shortly after departure. The National Transportation Safety Board "
             "is investigating.",
    ),
    dict(
        kicker="RAFAH · MIDEAST",
        headline="Five civil police killed in al-Mawasi strike",
        body="An Israeli airstrike hit a police post in the Gaza Strip; three "
             "more Palestinians, including a four-year-old, were killed in Gaza "
             "City. Mediators met again in Doha.",
    ),
    dict(
        kicker="UJJAI N · ASIA",
        headline="Four workers die in a hotel food-waste tank",
        body="The men entered the tank in Ujjain, Madhya Pradesh, and were "
             "overcome. Police have opened a negligence case against the hotel.",
    ),
    dict(
        kicker="JUBA · AFRICA",
        headline="South Sudan postpones its election to February",
        body="Officials delayed the vote, the country's first since independence, "
             "after its legitimacy was questioned. Opposition leader Riek Machar "
             "remains under house arrest.",
    ),
    dict(
        kicker="LA PAZ · CLIMATE",
        headline="Bolivia declares an emergency over the super El Niño",
        body="President Rodrigo Paz mobilised resources before the event peaks in "
             "November or December. California's coast is already under "
             "evacuation orders as 60-foot surf arrives.",
        art="dial",
        art_frac=0.85,
        art_big="60ft",
        art_cap="offshore swell",
        art_arc="EL NINO",
    ),
    dict(
        kicker="LONDON · EUROPE",
        headline="Pattinson named the next James Bond",
        body="The actor was chosen to succeed Daniel Craig after years of "
             "speculation. Producers said the next film begins shooting in 2027.",
    ),
    dict(
        kicker="MIAMI · AMERICAS",
        headline="SS United States sunk to make an artificial reef",
        body="The 1,000-foot liner, which took the Atlantic speed record in 1952, "
             "was deliberately submerged off Florida. Engineers opened the hull "
             "so it settles upright.",
    ),
    dict(
        kicker="MAJURO · CLIMATE",
        headline="Two Marshall Islands atolls named among Earth's most pristine",
        body="Bikar and Bokak support sea turtles, seabird colonies and more than "
             "250 reef-fish species. They are now inside a new national marine "
             "sanctuary.",
    ),
    # ---------------- sport and the rest of the day
    dict(
        kicker="MEXICO CITY · AMERICAS",
        headline="Antonelli, 20, becomes youngest F1 champion",
        body="The Mercedes driver finished third in Mexico City to take the "
             "title at 20 years and 68 days. He is the first Italian champion "
             "since 1953.",
    ),
    dict(
        kicker="NEW YORK · AMERICAS",
        headline="Almgren wins the New York City Marathon on debut",
        body="The Swedish distance runner took the 55th edition of the race in "
             "his first attempt. Conditions were cool and dry.",
    ),
    dict(
        kicker="TAMPA · AMERICAS",
        headline="Buccaneers win 16-0 without completing a pass",
        body="Tampa Bay beat Atlanta in Week 8 throwing only incompletions, the "
             "first team to win that way since Buffalo in 1974. The run game "
             "carried 213 yards.",
    ),
    dict(
        kicker="TOKYO · ASIA",
        headline="Shimada takes Skate Canada in her senior debut",
        body="The Japanese skater won the women's title ahead of Estonia's Niina "
             "Petrõkina and America's Isabeau Levito. It was her first senior "
             "Grand Prix.",
    ),
    dict(
        kicker="UBERLÂNDIA · AMERICAS",
        headline="53 red cards end a Brazilian under-20 match",
        body="Referees abandoned the game between EC Mamoré and Uberlândia EC "
             "after a brawl, dismissing 43 players and 10 officials. It is a "
             "world record for a single match.",
    ),
    dict(
        kicker="DOHA · MIDEAST",
        headline="Yamaha pulls out of the Qatar Grand Prix",
        body="The team withdrew, citing company-wide travel restrictions after "
             "its assessment of the Middle Eastern crisis. It is the first "
             "manufacturer to skip a round this season.",
    ),
    dict(
        kicker="NAIROBI · AFRICA",
        headline="Kenya's courts block a new tax on digital wallets",
        body="Judges suspended the levy pending a full hearing, saying the "
             "treasury had not consulted. Mobile-money operators had warned of "
             "costs for 38m users.",
    ),
    dict(
        kicker="LAGOS · AFRICA",
        headline="Nigeria's army frees 125 kidnap victims",
        body="Raids across Adamawa, Bauchi, Yobe and Borno also killed eight "
             "fighters and arrested 22 suspects, the defence headquarters said. "
             "The operations ran between 6 and 12 November.",
    ),
    dict(
        kicker="BEIJING · ASIA",
        headline="China cuts its one-year policy rate",
        body="The central bank trimmed the rate by 10 basis points to support "
             "lending as property investment fell again. The yuan was little "
             "changed.",
    ),
    dict(
        kicker="BRUSSELS · EUROPE",
        headline="EU agrees a seventh round of Russia sanctions",
        body="Ambassadors signed off on measures covering tanker insurance and "
             "machine tools, with a formal adoption expected next week. Two "
             "member states sought carve-outs.",
    ),
    dict(
        kicker="OTTAWA · AMERICAS",
        headline="Canada caps international student permits again",
        body="New foreign enrolment at US colleges fell 15 per cent this year "
             "after an 18 per cent drop last year, and Ottawa cut its cap in "
             "step. Universities warn of deficits.",
    ),
    dict(
        kicker="GENEVA · EUROPE",
        headline="WHO reports a measles rise across Europe",
        body="Cases more than doubled year on year in the region, the agency "
             "said, and urged catch-up vaccination. Coverage in two countries "
             "is below 90 per cent.",
    ),
    dict(
        kicker="SEOUL · ASIA",
        headline="Samsung shows a stretchable display",
        body="The panel stretches by 25 per cent without losing image quality, "
             "the company said, and is aimed at wearables. No shipping date was "
             "given.",
    ),
    dict(
        kicker="PARIS · EUROPE",
        headline="France raises its wildfire budget",
        body="The government added €500m for water bombers and forest clearing "
             "after a record season. Firefighters' unions called the sum "
             "insufficient.",
    ),
    dict(
        kicker="SYDNEY · ASIA",
        headline="Australia's unemployment holds at 4.1 per cent",
        body="Employers added 28,000 jobs, mostly part-time, the statistics "
             "bureau said. Traders trimmed bets on a February rate cut.",
    ),
    dict(
        kicker="RIO · AMERICAS",
        headline="Brazil's Congress advances a spending freeze",
        body="Lawmakers approved a first reading of cuts to meet the fiscal "
             "target. The real firmed on the vote.",
    ),
]

NUMBERS = [
    ("2%", "S&P 500 fall, third day"),
    ("$107bn", "Anthropic's listing"),
    ("53", "red cards, one match"),
    ("201", "Delhi PM 2.5 reading"),
    ("$6bn", "Binance theft"),
    ("60ft", "California surf"),
]


BRIEF_KICKERS = {
    "BEIJING · ASIA",
    "BRUSSELS · EUROPE",
    "DHAKA · ASIA",
    "DOHA · MIDEAST",
    "GENEVA · EUROPE",
    "GREENACRES · AMERICAS",
    "LAGOS · AFRICA",
    "LISBON · EUROPE",
    "MAJURO · CLIMATE",
    "MIAMI · AMERICAS",
    "NAIROBI · AFRICA",
    "OTTAWA · AMERICAS",
    "PARIS · EUROPE",
    "RIO · AMERICAS",
    "SEOUL · ASIA",
    "SOFIA · EUROPE",
    "SYDNEY · ASIA",
    "TAMPA · AMERICAS",
    "TOKYO · ASIA",
    "UJJAI N · ASIA",
}


def build():
    """(stories, numbers, tabs) with tab counts computed from the stories set."""
    items = []
    counts = {}
    for raw in STORIES:
        s = dict(raw)
        s["region"] = s["kicker"].split("·")[-1].strip()
        s["head"] = s["headline"]
        s["brief"] = s["kicker"].strip() in BRIEF_KICKERS
        items.append(s)
    for i, s in enumerate(items):
        if i >= 2:
            sent = [x for x in re.split(r"(?<=[.!?])\s+", s["body"]) if x]
            s["body"] = sent[0]
    for s in items:
        region = s["region"]
        counts[region] = counts.get(region, 0) + 1
    tabs = [(name, colour, counts.get(name, 0)) for name, colour in REGIONS
            if counts.get(name, 0)]
    return items, list(NUMBERS), tabs
