#!/usr/bin/env python3
"""Generate personalized chicago/ and miami/ index pages from berlin shell."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# lima currently holds a berlin-pattern shell (CSS/JS); berlin/index.html may be absent in this env
shell = (ROOT / "lima/index.html").read_text()
css = shell[shell.index("    <style>") : shell.index("        </style>") + len("        </style>")]
js_template = shell[
    shell.index('    <script src="https://unpkg.com/leaflet') : shell.rindex("</script>") + len("</script>")
]


def make_js(city, photo_ids, places, google_all):
    js = js_template
    old_set = "const photoIds = new Set(['frames', 'bean', 'riverwalk', 'architecture-tour', 'deep-dish', 'lincoln-park']);"
    new_set = "const photoIds = new Set([" + ", ".join(repr(x) for x in photo_ids) + "]);"
    if old_set not in js:
        raise SystemExit("photoIds set not found")
    js = js.replace(old_set, new_set)

    places_start = js.index("        const places = [")
    places_end = js.index("        ];", places_start) + len("        ];")
    lines = ["        const places = ["]
    for i, p in enumerate(places):
        comma = "," if i < len(places) - 1 else ""
        lines.append(
            "            {{ id: '{id}', name: '{name}', n: '{n}', lat: {lat}, lng: {lng}, query: '{query}' }}{c}".format(
                c=comma, **p
            )
        )
    lines.append("        ];")
    js = js[:places_start] + "\n".join(lines) + js[places_end:]
    js = js.replace(
        "document.getElementById('lima-map-link')", f"document.getElementById('{city}-map-link')"
    )
    js = js.replace("L.map('lima-map'", f"L.map('{city}-map'")
    import re

    js, n = re.subn(r"const googleAll = '[^']+';", f"const googleAll = '{google_all}';", js, count=1)
    if n != 1:
        raise SystemExit("googleAll not found")
    return js


def head(slug, title, desc, og_title, og_desc, og_alt, city_name, country):
    city_css = css.replace("#lima-map", f"#{slug}-map")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="https://globetrotwithveda.com/{slug}/">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="Veda">
    <meta property="og:locale" content="en_US">
    <meta property="og:title" content="{og_title}">
    <meta property="og:description" content="{og_desc}">
    <meta property="og:url" content="https://globetrotwithveda.com/{slug}/">
    <meta property="og:image" content="https://globetrotwithveda.com/{slug}-image.jpg">
    <meta property="og:image:alt" content="{og_alt}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{og_title}">
    <meta name="twitter:description" content="{og_desc}">
    <meta name="twitter:image" content="https://globetrotwithveda.com/{slug}-image.jpg">
    <link rel="icon" type="image/png" href="../favicon.png">
    <link rel="shortcut icon" type="image/png" href="../favicon.png">
    <link rel="apple-touch-icon" href="../favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Syne:wght@500;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">

    <script async src="https://www.googletagmanager.com/gtag/js?id=G-DYCWL3V5TW"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', 'G-DYCWL3V5TW');
    </script>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@graph": [
            {{
                "@type": "WebSite",
                "@id": "https://globetrotwithveda.com/#site",
                "name": "Veda",
                "url": "https://globetrotwithveda.com/"
            }},
            {{
                "@type": "WebPage",
                "@id": "https://globetrotwithveda.com/{slug}/",
                "url": "https://globetrotwithveda.com/{slug}/",
                "name": "{og_title}",
                "description": "{desc}",
                "isPartOf": {{ "@id": "https://globetrotwithveda.com/#site" }},
                "about": {{
                    "@type": "City",
                    "name": "{city_name}",
                    "containedInPlace": {{ "@type": "Country", "name": "{country}" }}
                }},
                "author": {{ "@type": "Person", "name": "Veda" }}
            }},
            {{
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {{ "@type": "ListItem", "position": 1, "name": "Atlas", "item": "https://globetrotwithveda.com/" }},
                    {{ "@type": "ListItem", "position": 2, "name": "{city_name}", "item": "https://globetrotwithveda.com/{slug}/" }}
                ]
            }}
        ]
    }}
    </script>

{city_css}
</head>
"""


def visa_block(city_name):
    return f"""<div class="panel visa-stack" id="visa" role="tabpanel" aria-labelledby="tab-visa" hidden>
            <p class="choice-label">Select your citizenship</p>
            <div class="choice" role="group" aria-label="Citizenship">
                <button type="button" class="citizenship-btn" data-citizenship="indian" aria-pressed="true"><span class="emo" aria-hidden="true">🇮🇳</span> Indian citizen</button>
                <button type="button" class="citizenship-btn" data-citizenship="us" aria-pressed="false"><span class="emo" aria-hidden="true">🇺🇸</span> US citizen</button>
            </div>

            <div class="visa-block" id="visa-indian">
                <div class="visa-alert">
                    <strong>US entry first.</strong> Indian citizens need a valid US visa (usually B1/B2) to enter the United States. Once you are in the US, {city_name} is domestic travel.
                </div>

                <p class="choice-label">Where are you currently residing?</p>
                <div class="choice" role="group" aria-label="Residency">
                    <button type="button" class="residency-btn" data-residency="india" aria-pressed="true"><span class="emo" aria-hidden="true">🏠</span> Living in India</button>
                    <button type="button" class="residency-btn" data-residency="usa" aria-pressed="false"><span class="emo" aria-hidden="true">✈️</span> Living in USA (H1B/H4/OPT)</button>
                </div>

                <div class="visa-block" id="indian-india">
                    <div class="visa-grid">
                        <div class="card">
                            <h3><span class="emo" aria-hidden="true">📅</span> B1/B2 tourist / business</h3>
                            <div class="detail"><strong>What</strong><span>Visitor visa to enter the US; then fly domestically to {city_name}</span></div>
                            <div class="detail"><strong>Validity</strong><span>Often multi-year / multiple-entry (consulate decides)</span></div>
                            <div class="detail"><strong>Stay</strong><span>Usually up to 6 months per entry (CBP decides at the border)</span></div>
                            <div class="detail"><strong>Fee</strong><span>MRV fee (check travel.state.gov for current amount)</span></div>
                        </div>
                        <div class="card">
                            <h3><span class="emo" aria-hidden="true">📄</span> Required documents</h3>
                            <ul>
                                <li>Valid Indian passport</li>
                                <li>DS-160 confirmation page</li>
                                <li>Visa interview appointment confirmation</li>
                                <li>MRV fee payment receipt</li>
                                <li>Photo meeting US visa specs</li>
                                <li>Travel itinerary / hotel bookings (helpful)</li>
                                <li>Proof of ties to India (job, property, family)</li>
                                <li>Bank statements / financial proof</li>
                            </ul>
                        </div>
                        <div class="card">
                            <h3><span class="emo" aria-hidden="true">📍</span> How to apply</h3>
                            <div class="detail"><strong>Form</strong><span>DS-160 online</span></div>
                            <div class="detail"><strong>Interview</strong><span>US Embassy/Consulate in India (Delhi, Mumbai, Chennai, Hyderabad, Kolkata)</span></div>
                            <div class="detail"><strong>Appointments</strong><span>Book via the official US visa scheduling site</span></div>
                            <div class="detail"><strong>After visa</strong><span>Fly into any US port of entry, then a domestic flight to {city_name}</span></div>
                        </div>
                        <div class="card">
                            <h3><span class="emo" aria-hidden="true">💡</span> Pro tips</h3>
                            <ul>
                                <li>Apply well before travel — interview wait times vary by city</li>
                                <li>B1/B2 is for temporary visits; do not overstay your I-94</li>
                                <li>Domestic US flights need REAL ID-compliant ID or a passport</li>
                                <li>Keep hotel and return plans handy for CBP</li>
                                <li>ESTA is not for Indian passports — you need a visa stamp</li>
                            </ul>
                        </div>
                    </div>
                    <div class="note" style="margin-top:14px"><strong>Important:</strong> Guidance only. Check travel.state.gov and the US Embassy/Consulate for current fees, wait times, and rules.</div>
                </div>

                <div class="visa-block" id="indian-usa" hidden>
                    <div class="visa-alert ok">
                        <strong>Domestic trip.</strong> If you already hold valid US status (H1B/H4/OPT and a valid I-94), {city_name} is a domestic flight — no new visa for this city.
                    </div>
                    <div class="visa-grid">
                        <div class="card">
                            <h3><span class="emo" aria-hidden="true">✈️</span> What you need</h3>
                            <div class="detail"><strong>Status</strong><span>Valid H1B/H4/OPT (or other) with unexpired I-94</span></div>
                            <div class="detail"><strong>ID for flying</strong><span>Passport or REAL ID-compliant driver's license</span></div>
                            <div class="detail"><strong>Extra visa</strong><span>None for domestic US travel</span></div>
                            <div class="detail"><strong>Re-entry</strong><span>Only matters if you leave the US and come back</span></div>
                        </div>
                        <div class="card">
                            <h3><span class="emo" aria-hidden="true">📄</span> Carry anyway</h3>
                            <ul>
                                <li>Passport with visa stamp (if you have one)</li>
                                <li>I-797 (H1B/H4) or EAD (OPT/H4 EAD)</li>
                                <li>Recent pay stub or employment letter (optional but useful)</li>
                                <li>Government photo ID for TSA</li>
                            </ul>
                        </div>
                        <div class="card">
                            <h3><span class="emo" aria-hidden="true">💡</span> Tips for H1B/H4/OPT</h3>
                            <ul>
                                <li>No embassy appointment for a domestic US city once your status is valid</li>
                                <li>Watch your I-94 end date; domestic travel does not extend status</li>
                                <li>If your visa stamp is expired but I-94 is valid, you can stay/travel inside the US; leaving requires a new stamp to return</li>
                                <li>Carry passport or REAL ID for TSA at the airport</li>
                            </ul>
                        </div>
                        <div class="card">
                            <h3><span class="emo" aria-hidden="true">⚠️</span> Important</h3>
                            <div class="detail"><strong>Leaving the US</strong><span>A side trip abroad may still need a valid visa stamp to re-enter — check before you book</span></div>
                            <div class="detail"><strong>TSA</strong><span>REAL ID rules apply for domestic boarding</span></div>
                        </div>
                    </div>
                    <div class="note" style="margin-top:14px"><strong>Important:</strong> Status rules change. Confirm I-94 at i94.cbp.dhs.gov and TSA ID rules before you fly.</div>
                </div>
            </div>

            <div class="visa-block" id="visa-us" hidden>
                <div class="visa-alert ok">
                    <strong>Domestic travel.</strong> US citizens do not need a visa for {city_name}.
                </div>
                <div class="visa-grid">
                    <div class="card">
                        <h3><span class="emo" aria-hidden="true">✈️</span> Flying domestically</h3>
                        <div class="detail"><strong>ID</strong><span>REAL ID-compliant license or US passport</span></div>
                        <div class="detail"><strong>Visa</strong><span>Not required</span></div>
                        <div class="detail"><strong>Duration</strong><span>No immigration limit inside the US</span></div>
                    </div>
                    <div class="card">
                        <h3><span class="emo" aria-hidden="true">💡</span> Travel tips</h3>
                        <ul>
                            <li>Carry a government photo ID that TSA accepts</li>
                            <li>Book hotels early around big weekends and festivals</li>
                            <li>Domestic flight delays are common — leave buffer for timed tickets</li>
                        </ul>
                    </div>
                </div>
                <div class="note"><strong>Note:</strong> This page is about visiting {city_name} inside the United States. International trips still follow the destination country's rules.</div>
            </div>
        </div>"""


def write_chicago():
    places = [
        {
            "id": "millennium",
            "name": "Millennium Park",
            "n": "01",
            "lat": 41.8826,
            "lng": -87.6226,
            "query": "Millennium Park, Chicago, IL",
        },
        {
            "id": "artinstitute",
            "name": "Art Institute",
            "n": "02",
            "lat": 41.8796,
            "lng": -87.6237,
            "query": "Art Institute of Chicago, Chicago, IL",
        },
        {
            "id": "navypier",
            "name": "Navy Pier",
            "n": "03",
            "lat": 41.8917,
            "lng": -87.6086,
            "query": "Navy Pier, Chicago, IL",
        },
        {
            "id": "river",
            "name": "River architecture",
            "n": "04",
            "lat": 41.8892,
            "lng": -87.6242,
            "query": "Chicago Riverwalk architecture tour, Chicago, IL",
        },
    ]
    google_all = (
        "https://www.google.com/maps/dir/?api=1&origin=Millennium%20Park%2C%20Chicago"
        "&destination=Navy%20Pier%2C%20Chicago"
        "&waypoints=Art%20Institute%20of%20Chicago%7CChicago%20Riverwalk"
        "&travelmode=walking"
    )
    photo_ids = ["frames", "bean", "riverwalk", "deepdish", "lincolnpark", "cruise"]
    body = f"""<body>
    <a class="skip" href="#notes">Skip to notes</a>
    <div class="progress" id="progress"></div>

    <header class="nav">
        <a class="wordmark" href="../index.html">Veda</a>
        <div class="nav-meta">
            <span class="coords">41.8781° N · 87.6298° W</span>
            <a href="../index.html">Atlas</a>
        </div>
    </header>

    <section class="hero" id="chicago" aria-label="Chicago">
        <div class="hero-media">
            <img src="../chicago-image.jpg" alt="Veda on the Chicago Riverwalk with the skyline behind her">
        </div>
        <div class="hero-copy">
            <p class="kicker">United States · Field notes</p>
            <h1>CHICAGO<span>Steel, lake wind, and a bean that steals every photo.</span></h1>
            <p class="hero-lead">Four days of the Loop on foot, Cloud Gate, deep dish at Giordano’s, a river architecture cruise at dusk, and the CTA L stitching it together.</p>
            <div class="hero-stats">
                <div><strong>4</strong><span>Days</span></div>
                <div><strong>Loop</strong><span>Walked hard</span></div>
                <div><strong>5</strong><span>Places that stuck</span></div>
            </div>
        </div>
    </section>

    <nav class="rail" aria-label="On this page">
        <a href="#map">Map</a>
        <a href="#intel">Intel</a>
        <a href="#frames">Photos</a>
        <a href="#unfinished">Still</a>
        <a href="#day-tours">Trips</a>
        <a href="#visa">Visa</a>
    </nav>

    <section class="intro" id="notes">
        <h2>The skyline is the postcard.<br>The river is the tour.</h2>
        <p>Chicago got me with Midwestern warmth under a serious skyline. Millennium Park for the Bean, the Art Institute for a half-day, Navy Pier when I wanted lake air, and a river cruise that makes the architecture make sense. Deep dish is a commitment. Blues clubs still earn the night.</p>
    </section>

    <section class="atlas-map" id="map">
        <h2>Where I actually walked.</h2>
        <p>Every tagged stop is on the map. <strong>All pins</strong> shows them together — tap a name to zoom in. Each popup opens the same place in Google Maps.</p>
        <div class="map-pins" role="group" aria-label="Chicago locations">
            <button type="button" aria-pressed="true" data-place="all">All pins</button>
            <button type="button" aria-pressed="false" data-place="millennium">Millennium</button>
            <button type="button" aria-pressed="false" data-place="artinstitute">Art Institute</button>
            <button type="button" aria-pressed="false" data-place="navypier">Navy Pier</button>
            <button type="button" aria-pressed="false" data-place="river">River</button>
        </div>
        <div class="map-frame">
            <div id="chicago-map" role="region" aria-label="Map of Chicago with tagged locations"></div>
        </div>
        <a class="map-open" id="chicago-map-link" href="https://www.google.com/maps/search/?api=1&query=Chicago" target="_blank" rel="noopener noreferrer">Open a walking route in Google Maps ↗</a>
    </section>

    <section class="intel" id="intel">
        <h2>Intel</h2>
        <p class="intel-lead">The useful layer — museum tickets, a river cruise slot, CTA without overbuying, and where to sit for deep dish.</p>
        <div class="tabs" role="tablist" aria-label="Chicago practical notes">
            <button type="button" role="tab" id="tab-see" aria-controls="panel-see" aria-selected="true" data-tab="see"><span class="emo" aria-hidden="true">👀</span> See</button>
            <button type="button" role="tab" id="tab-book" aria-controls="panel-book" aria-selected="false" data-tab="book"><span class="emo" aria-hidden="true">🎟️</span> Book</button>
            <button type="button" role="tab" id="tab-eat" aria-controls="panel-eat" aria-selected="false" data-tab="eat"><span class="emo" aria-hidden="true">🥐</span> Eat</button>
            <button type="button" role="tab" id="tab-stay" aria-controls="panel-stay" aria-selected="false" data-tab="stay"><span class="emo" aria-hidden="true">🛏️</span> Stay</button>
            <button type="button" role="tab" id="tab-when" aria-controls="panel-when" aria-selected="false" data-tab="when"><span class="emo" aria-hidden="true">📅</span> When</button>
            <button type="button" role="tab" id="tab-move" aria-controls="panel-move" aria-selected="false" data-tab="move"><span class="emo" aria-hidden="true">🚶</span> Move</button>
            <button type="button" role="tab" id="tab-visa" aria-controls="visa" aria-selected="false" data-tab="visa"><span class="emo" aria-hidden="true">🛂</span> Visa</button>
        </div>

        <div class="panel is-on grid-3" id="panel-see" role="tabpanel" aria-labelledby="tab-see">
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🪞</span> Millennium Park / Cloud Gate</h3>
                <p>The Bean. Mirror steel, skyline upside down, a plaza that never empties. Go early if you want a frame without a hundred phones.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🎨</span> Art Institute</h3>
                <p>Impressionists, lions out front, a half-day that still feels short. Timed tickets. Wear shoes you can stand in.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🎡</span> Navy Pier</h3>
                <p>Lake Michigan, the Centennial Wheel, tourist on purpose. Sunset from the pier is the soft version of the skyline.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚢</span> Architecture river cruise</h3>
                <p>The city from water level. Guides who know their steel. Book dusk if you can — lights on glass beat noon glare.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🍕</span> Deep dish</h3>
                <p>Not a slice you fold. A pie you schedule. Giordano’s was my stop; Lou Malnati’s is the other religion.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🎵</span> Blues</h3>
                <p>Chicago’s soundtrack is still live. South Side clubs and downtown rooms — pick a night and stay for a set.</p>
            </div>
        </div>

        <div class="panel grid-3" id="panel-book" role="tabpanel" aria-labelledby="tab-book" hidden>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🎨</span> Art Institute tickets</h3>
                <p>Buy timed entry online. Weekends sell. Members skip some of the wait; I paid and planned a half day.</p>
                <span class="price">Timed ticket</span>
                <a class="book-link" href="https://www.artic.edu/visit" target="_blank" rel="noopener noreferrer">Art Institute ↗</a>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚢</span> Architecture cruise</h3>
                <p>Chicago Architecture Center or similar. Sunset slots go first. Rain jackets still worth it on the river.</p>
                <span class="price">Book ahead</span>
                <a class="book-link" href="https://www.architecture.org/tours" target="_blank" rel="noopener noreferrer">CAC tours ↗</a>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚇</span> CTA Ventra</h3>
                <p>L trains and buses. Ventra card or contactless. Day passes exist — do the math for your hops.</p>
                <span class="price">App / tap</span>
                <a class="book-link" href="https://www.transitchicago.com/" target="_blank" rel="noopener noreferrer">CTA ↗</a>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🎡</span> Navy Pier wheel</h3>
                <p>Optional. The pier is free to walk. The wheel is the postcard upgrade.</p>
                <span class="price">Timed ticket</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🤍</span> No reservation</h3>
                <p>Millennium Park, the Riverwalk, most of the Loop exterior. Show up. The Bean at 8am is a different city.</p>
                <span class="price">Walk up</span>
            </div>
        </div>

        <div class="panel grid-3" id="panel-eat" role="tabpanel" aria-labelledby="tab-eat" hidden>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🍕</span> Deep-dish pizza</h3>
                <p>Giordano’s for the stuffed pie I actually ate. Share. Order, then walk the Riverwalk while it bakes.</p>
                <span class="price">$18–30</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🌭</span> Chicago hot dog</h3>
                <p>Garden on a bun. No ketchup if you want the local rule. Portillo’s or a corner stand.</p>
                <span class="price">$5–8</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🇮🇹</span> Italian beef</h3>
                <p>Dipped, spicy giardiniera, napkins you will need. A lunch that is also a workout.</p>
                <span class="price">$10–14</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🍿</span> Garrett popcorn</h3>
                <p>Cheese and caramel mixed. Sticky fingers on Michigan Avenue. Tourist and correct.</p>
                <span class="price">$10–15</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🥩</span> Steakhouse night</h3>
                <p>If deep dish already won lunch, spend one evening on a classic Chicago chop.</p>
                <span class="price">$$$</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🍩</span> Doughnut / bakery</h3>
                <p>Neighborhood bakeries beat hotel breakfast. Fuel before the Art Institute.</p>
                <span class="price">$3–6</span>
            </div>
        </div>

        <div class="panel" id="panel-stay" role="tabpanel" aria-labelledby="tab-stay" hidden>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">📅</span> When to book</h3>
                <p>Summer festivals and marathon weekend need a head start. Fall is kinder. A few weeks usually covers spring.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">📍</span> Where</h3>
                <p><strong>Loop / River North</strong> — walk to the Bean and the river. <strong>Near North / Mag Mile</strong> — shopping and hotels. <strong>West Loop</strong> — dinner, still a short rideshare downtown.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">💵</span> Spend less</h3>
                <p>You do not need a lake-view room. The L is the view. Stay on a train line and walk the rest.</p>
            </div>
        </div>

        <div class="panel grid-2" id="panel-when" role="tabpanel" aria-labelledby="tab-when" hidden>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🌸</span> Spring (Apr–May)</h3>
                <p>8–20°C. City waking up, patios opening, fewer crowds than summer. Fine walking weather.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">☀️</span> Summer (Jun–Aug)</h3>
                <p>20–30°C. Festivals, lake beaches, long light — and hot. Book early. Hide at noon if you melt.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🍂</span> Fall (Sep–Oct)</h3>
                <p>10–22°C. Best overall for me — architecture tours, foliage, marathon energy without July humidity.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">❄️</span> Winter (Nov–Mar)</h3>
                <p>−10–5°C. Brutal wind off the lake. Museums, theaters, holiday lights. Budget rates if you pack layers.</p>
            </div>
        </div>

        <div class="panel grid-3" id="panel-move" role="tabpanel" aria-labelledby="tab-move" hidden>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚶</span> Walk the Loop</h3>
                <p>Millennium Park to the Riverwalk is a pedestrian day. Shoes. Then the L when the next pin is a neighborhood away.</p>
                <span class="price">Free</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚇</span> CTA L</h3>
                <p>Elevated trains that define the Loop. Ventra or contactless. Inspectors exist — tap honestly.</p>
                <span class="price">Ventra</span>
                <a class="book-link" href="https://www.transitchicago.com/" target="_blank" rel="noopener noreferrer">CTA ↗</a>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚕</span> Rideshare</h3>
                <p>For late blues clubs, luggage, or when the L map confuses you at midnight.</p>
                <span class="price">App</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚲</span> Divvy bikes</h3>
                <p>Blue bikes along the river. Fine for short hops if wind allows.</p>
                <span class="price">From a few $/ride</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">✈️</span> Airports</h3>
                <p>ORD or MDW. Blue Line from O’Hare is the adult choice. Rideshare if you land late with bags.</p>
                <span class="price">Train / car</span>
            </div>
        </div>

{visa_block("Chicago")}
    </section>

    <section class="frames" id="frames">
        <h2>What stayed on the roll.</h2>
        <p class="frames-lead">Five frames from the river, the Bean, a pizza stand, and Lincoln Park. Not a complete Chicago — just what I kept.</p>
    </section>

    <article class="chapter" id="bean">
        <div class="film" data-film>
            <img class="is-on" src="chicago-image-4.jpg" alt="Cloud Gate at Millennium Park">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 01</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">01 / 05</p>
            <h2>The Bean</h2>
            <p>Cloud Gate does not pretend to be subtle. Skyline bent into steel, plaza full of phones, a sculpture that still works when you stand under it. Millennium Park is the correct first stop.</p>
        </div>
    </article>
    <article class="chapter is-flip" id="riverwalk">
        <div class="film" data-film>
            <img class="is-on" src="chicago-image-1.jpg" alt="On the Chicago Riverwalk with the skyline">
            <img src="chicago-image-5.jpg" alt="Riverwalk walkway and towers" loading="lazy">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 02</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">02 / 05</p>
            <h2>Riverwalk, daylight</h2>
            <p>Concrete path, glass towers, Marina City’s corn cobs in the distance. The lower level is where the city feels walkable. I kept circling the same stretch because the light kept changing.</p>
        </div>
    </article>
    <article class="chapter" id="deepdish">
        <div class="film" data-film>
            <img class="is-on" src="chicago-image-3.jpg" alt="Deep-dish pizza at Giordano's">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 01</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">03 / 05</p>
            <h2>Deep dish, Giordano’s</h2>
            <p>A pie on a stand, olives, a crust you schedule around. This is not foldable street pizza. Share it. Then walk it off on the river.</p>
        </div>
    </article>
    <article class="chapter is-flip" id="lincolnpark">
        <div class="film" data-film>
            <img class="is-on" src="chicago-image-2.jpg" alt="Lincoln Park afternoon">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 01</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">04 / 05</p>
            <h2>Lincoln Park pause</h2>
            <p>Grass, trees, a free zoo if you want animals. After the Loop’s steel, this is the green lung. Temporary tattoos optional. The breeze is not.</p>
        </div>
    </article>
    <article class="chapter" id="cruise">
        <div class="film" data-film>
            <img class="is-on" src="chicago-image-6.jpg" alt="Chicago Riverwalk at night">
            <img src="chicago-image-7.jpg" alt="Architecture river cruise at dusk" loading="lazy">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 02</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">05 / 05</p>
            <h2>Lights on the river</h2>
            <p>Wrigley Building lit, a boat sliding under the bridges, the skyline doing its night job. The architecture cruise is how the map finally clicks.</p>
        </div>
    </article>

    <section class="unfinished" id="unfinished">
        <h2>Still on the list.</h2>
        <p class="unfinished-lead">Four days is a first draft. These are the rooms I didn’t finish — worth a return ticket.</p>
        <div class="grid-3">
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🏢</span> Willis Tower skydeck</h3>
                <p>The glass box over the Loop. I stayed at river level. Next time I go up.</p>
                <span class="price">Ticket</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🎸</span> Longer blues night</h3>
                <p>One set is not enough. I owe Chicago a late last train.</p>
                <span class="price">Night</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🏘️</span> Pilsen murals</h3>
                <p>Neighborhood color beyond downtown. On the list for a slower trip.</p>
                <span class="price">Walk</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">⚾</span> Cubs at Wrigley</h3>
                <p>If the season lines up. Ivy, a crowd, a different Chicago afternoon.</p>
                <span class="price">Seasonal</span>
            </div>
        </div>
    </section>

    <section class="day-tours" id="day-tours">
        <h2>If you have a fifth day.</h2>
        <p class="day-tours-lead">Oak Park for Wright, a longer lakefront ride, or a museum you skipped downtown.</p>
        <div class="grid-3">
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🏠</span> Oak Park</h3>
                <p>Frank Lloyd Wright homes on a Green Line / bus combo. Architecture without the riverboat.</p>
                <span class="price">Day · transit</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🔬</span> Museum Campus</h3>
                <p>Shedd, Field, Adler — pick one. Do not try all three unless you enjoy lines.</p>
                <span class="price">Half day</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🌊</span> Lakefront trail</h3>
                <p>Bike or walk along Michigan. Soft day after deep dish and museums.</p>
                <span class="price">Half day</span>
            </div>
        </div>
    </section>

    <div class="next">
        <a href="../index.html">← Back to the atlas</a>
        <a href="../miami/">Miami is next →</a>
    </div>

    <footer>
        <span>Chicago · United States</span>
        <span>globetrotwithveda.com</span>
    </footer>

{make_js("chicago", photo_ids, places, google_all)}
</body>
</html>
"""
    html = head(
        "chicago",
        "Chicago itinerary: 4 days, food, map, and visa notes | Veda",
        "A 4-day Chicago itinerary with a walking map, what to eat, when to go, and US domestic visa notes for Indian and US passports — written by Veda, who actually went.",
        "Chicago itinerary: 4 days, food, map, and visa notes",
        "Places to walk, what to eat, when to go, and visa notes for Indian and US passports — in one Chicago page.",
        "Veda on the Chicago Riverwalk with the skyline behind her",
        "Chicago",
        "United States",
    ) + body
    out = ROOT / "chicago/index.html"
    out.write_text(html)
    print("wrote", out, "bytes", out.stat().st_size)


def write_miami():
    places = [
        {
            "id": "bayside",
            "name": "Bayside Marketplace",
            "n": "01",
            "lat": 25.7781,
            "lng": -80.1867,
            "query": "Bayside Marketplace, Miami, FL",
        },
        {
            "id": "southbeach",
            "name": "South Beach",
            "n": "02",
            "lat": 25.7826,
            "lng": -80.1341,
            "query": "South Beach, Miami Beach, FL",
        },
        {
            "id": "everglades",
            "name": "Everglades",
            "n": "03",
            "lat": 25.7459,
            "lng": -80.5544,
            "query": "Everglades National Park, Florida",
        },
        {
            "id": "keywest",
            "name": "Key West southernmost",
            "n": "04",
            "lat": 24.5465,
            "lng": -81.7975,
            "query": "Southernmost Point Buoy, Key West, FL",
        },
    ]
    google_all = (
        "https://www.google.com/maps/dir/?api=1&origin=Bayside%20Marketplace%2C%20Miami"
        "&destination=Southernmost%20Point%20Buoy%2C%20Key%20West"
        "&waypoints=South%20Beach%2C%20Miami%20Beach%7CEverglades%20National%20Park"
        "&travelmode=driving"
    )
    photo_ids = ["frames", "snorkel", "bayside", "speedboat", "macaws", "everglades", "nightlife", "keywest"]
    js = make_js("miami", photo_ids, places, google_all).replace(
        "Open a walking route in Google Maps ↗",
        "Open a driving route in Google Maps ↗",
    )
    body = f"""<body>
    <a class="skip" href="#notes">Skip to notes</a>
    <div class="progress" id="progress"></div>

    <header class="nav">
        <a class="wordmark" href="../index.html">Veda</a>
        <div class="nav-meta">
            <span class="coords">25.7617° N · 80.1918° W</span>
            <a href="../index.html">Atlas</a>
        </div>
    </header>

    <section class="hero" id="miami" aria-label="Miami">
        <div class="hero-media">
            <img src="../miami-image.jpg" alt="Miami waterfront and tropical sky">
        </div>
        <div class="hero-copy">
            <p class="kicker">United States · Field notes</p>
            <h1>MIAMI<span>Salt air, neon nights, and a day that ends in Key West.</span></h1>
            <p class="hero-lead">Snorkel mornings, speedboats on the Atlantic, Bayside docks, Everglades airboats, cafecito, and the southernmost buoy when the Keys call.</p>
            <div class="hero-stats">
                <div><strong>4+</strong><span>Days</span></div>
                <div><strong>Atlantic</strong><span>In the water</span></div>
                <div><strong>8</strong><span>Frames kept</span></div>
            </div>
        </div>
    </section>

    <nav class="rail" aria-label="On this page">
        <a href="#map">Map</a>
        <a href="#intel">Intel</a>
        <a href="#frames">Photos</a>
        <a href="#unfinished">Still</a>
        <a href="#day-tours">Trips</a>
        <a href="#visa">Visa</a>
    </nav>

    <section class="intro" id="notes">
        <h2>Paradise is not only the beach.<br>It is the mix.</h2>
        <p>Miami hit me as Art Deco plus humidity plus Cuban coffee. One day in the Atlantic, one on an airboat in the River of Grass, one racing a speedboat past the skyline, and a Key West marker that feels like the edge of the map. Nightlife is not optional here — it is the city’s second shift.</p>
    </section>

    <section class="atlas-map" id="map">
        <h2>Where I actually went.</h2>
        <p>Tagged stops on the map. <strong>All pins</strong> shows them together — tap a name to zoom. Popups open Google Maps. Key West is a drive or tour day, not a walk from South Beach.</p>
        <div class="map-pins" role="group" aria-label="Miami locations">
            <button type="button" aria-pressed="true" data-place="all">All pins</button>
            <button type="button" aria-pressed="false" data-place="bayside">Bayside</button>
            <button type="button" aria-pressed="false" data-place="southbeach">South Beach</button>
            <button type="button" aria-pressed="false" data-place="everglades">Everglades</button>
            <button type="button" aria-pressed="false" data-place="keywest">Key West</button>
        </div>
        <div class="map-frame">
            <div id="miami-map" role="region" aria-label="Map of Miami-area stops with tagged locations"></div>
        </div>
        <a class="map-open" id="miami-map-link" href="https://www.google.com/maps/search/?api=1&query=Miami" target="_blank" rel="noopener noreferrer">Open a route in Google Maps ↗</a>
    </section>

    <section class="intel" id="intel">
        <h2>Intel</h2>
        <p class="intel-lead">Boat slots, hurricane season honesty, Cuban sandwiches, and how to move without living in traffic.</p>
        <div class="tabs" role="tablist" aria-label="Miami practical notes">
            <button type="button" role="tab" id="tab-see" aria-controls="panel-see" aria-selected="true" data-tab="see"><span class="emo" aria-hidden="true">👀</span> See</button>
            <button type="button" role="tab" id="tab-book" aria-controls="panel-book" aria-selected="false" data-tab="book"><span class="emo" aria-hidden="true">🎟️</span> Book</button>
            <button type="button" role="tab" id="tab-eat" aria-controls="panel-eat" aria-selected="false" data-tab="eat"><span class="emo" aria-hidden="true">🥐</span> Eat</button>
            <button type="button" role="tab" id="tab-stay" aria-controls="panel-stay" aria-selected="false" data-tab="stay"><span class="emo" aria-hidden="true">🛏️</span> Stay</button>
            <button type="button" role="tab" id="tab-when" aria-controls="panel-when" aria-selected="false" data-tab="when"><span class="emo" aria-hidden="true">📅</span> When</button>
            <button type="button" role="tab" id="tab-move" aria-controls="panel-move" aria-selected="false" data-tab="move"><span class="emo" aria-hidden="true">🚶</span> Move</button>
            <button type="button" role="tab" id="tab-visa" aria-controls="visa" aria-selected="false" data-tab="visa"><span class="emo" aria-hidden="true">🛂</span> Visa</button>
        </div>

        <div class="panel is-on grid-3" id="panel-see" role="tabpanel" aria-labelledby="tab-see">
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🤿</span> Snorkel the Atlantic</h3>
                <p>Warm water, reef time, salt in your hair. Book a boat that actually puts you in the water, not just past it.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🛥️</span> Bayside &amp; bay boats</h3>
                <p>Yachts and fishing boats sharing a dock. Star Island tours leave from here. Sunset is the soft sell.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚤</span> Speedboat</h3>
                <p>Spray, skyline, open Atlantic. Loud and worth it once. Hold the rail.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🦜</span> Macaws &amp; color</h3>
                <p>Tropical birds that look Photoshopped until they aren’t. Miami’s palette is not subtle.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🐊</span> Everglades</h3>
                <p>Airboat, sawgrass, alligators that ignore your schedule. A different Florida than Ocean Drive.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🌴</span> Key West day</h3>
                <p>Southernmost Point buoy, 90 miles from Cuba on the sign. Long day from Miami — leave early or overnight.</p>
            </div>
        </div>

        <div class="panel grid-3" id="panel-book" role="tabpanel" aria-labelledby="tab-book" hidden>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚤</span> Speedboat / snorkel</h3>
                <p>Morning slots are kinder. Confirm gear and reef stops. Seasick tablets if you are that person.</p>
                <span class="price">Book ahead</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🐊</span> Everglades airboat</h3>
                <p>Operators west of the city. Bring ear protection and something that can get wet.</p>
                <span class="price">Half day</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚌</span> Key West tour or drive</h3>
                <p>Overseas Highway is the point. Day tours exist; overnight is saner if you want Duval after dark.</p>
                <span class="price">Day · long</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🏛️</span> Vizcaya</h3>
                <p>Villa and gardens on the bay. Timed tickets help on weekends.</p>
                <span class="price">Ticket</span>
                <a class="book-link" href="https://vizcaya.org/" target="_blank" rel="noopener noreferrer">Vizcaya ↗</a>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🤍</span> Walk-up</h3>
                <p>South Beach, Wynwood Walls exterior, Little Havana sidewalks. Show up. Bring sunscreen that means it.</p>
                <span class="price">Free</span>
            </div>
        </div>

        <div class="panel grid-3" id="panel-eat" role="tabpanel" aria-labelledby="tab-eat" hidden>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🥪</span> Cuban sandwich</h3>
                <p>Ham, roast pork, Swiss, pickles, mustard, pressed. Versailles or a serious ventanita line.</p>
                <span class="price">$8–12</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🦞</span> Stone crab</h3>
                <p>In season roughly Oct–May. Cold claws, mustard sauce. Joe’s if you accept the wait.</p>
                <span class="price">$40–60</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🍋</span> Ceviche</h3>
                <p>Citrus, cilantro, ocean-fresh fish. Beach lunch energy without the sand in your teeth.</p>
                <span class="price">$15–25</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">☕</span> Cafecito</h3>
                <p>Sweet, strong, window service. Colada if you are sharing. Morning ritual, not a latte.</p>
                <span class="price">$1–2</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🥧</span> Key lime pie</h3>
                <p>Tart, graham crust, the Keys on a plate. Save room even after seafood.</p>
                <span class="price">$8–12</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🍹</span> Mojitos</h3>
                <p>Mint, lime, beach-bar logic. One after the boat. Hydrate either way.</p>
                <span class="price">$12–18</span>
            </div>
        </div>

        <div class="panel" id="panel-stay" role="tabpanel" aria-labelledby="tab-stay" hidden>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">📅</span> When to book</h3>
                <p>Winter peak and Art Basel week need lead time. Summer is cheaper and stormier. Shoulder spring is the value play.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">📍</span> Where</h3>
                <p><strong>South Beach</strong> — walk to sand and Art Deco. <strong>Brickell / downtown</strong> — bay and Bayside access. <strong>Wynwood</strong> — murals and evenings that are not Ocean Drive.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">💵</span> Spend less</h3>
                <p>Oceanfront premiums are real. One neighborhood inland plus rideshare still gets you the water.</p>
            </div>
        </div>

        <div class="panel grid-2" id="panel-when" role="tabpanel" aria-labelledby="tab-when" hidden>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">☀️</span> Winter (Dec–Mar)</h3>
                <p>18–26°C. Best overall — beach weather, lower humidity, peak prices and crowds. Book early.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🌺</span> Spring (Apr–May)</h3>
                <p>22–29°C. Still excellent, fewer crowds, better rates after spring break.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🌧️</span> Summer (Jun–Sep)</h3>
                <p>26–33°C. Hurricane season. Hot, humid, afternoon storms, lowest rates. Watch forecasts.</p>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🍂</span> Fall (Oct–Nov)</h3>
                <p>23–29°C. Risk easing, still warm, deals before winter rush. November is a sweet spot.</p>
            </div>
        </div>

        <div class="panel grid-3" id="panel-move" role="tabpanel" aria-labelledby="tab-move" hidden>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚶</span> Walk pockets</h3>
                <p>South Beach, Wynwood, Little Havana work on foot. Cross-town is not a stroll.</p>
                <span class="price">Free</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚕</span> Rideshare</h3>
                <p>Default between neighborhoods. Traffic is the tax. Budget time, not just money.</p>
                <span class="price">App</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚇</span> Metromover / Metrorail</h3>
                <p>Downtown Metromover is free. Useful near Brickell and Bayside — not a full city network.</p>
                <span class="price">Free / cheap</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🚗</span> Car for Keys / Glades</h3>
                <p>Rent if Everglades or Key West are on the plan. Parking in South Beach is its own adventure.</p>
                <span class="price">Day rate</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">✈️</span> MIA / FLL</h3>
                <p>Either airport works. Rideshare or rental after landing. Domestic connections are normal.</p>
                <span class="price">Airport</span>
            </div>
        </div>

{visa_block("Miami")}
    </section>

    <section class="frames" id="frames">
        <h2>What stayed on the roll.</h2>
        <p class="frames-lead">Eight frames from water, birds, neon, and the Keys. Not a complete Miami — just what I kept.</p>
    </section>

    <article class="chapter" id="snorkel">
        <div class="film" data-film>
            <img class="is-on" src="miami-image-1.jpg" alt="Snorkeling in the Atlantic">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 01</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">01 / 07</p>
            <h2>Under the Atlantic</h2>
            <p>Mask on, reef below, Miami sun above the surface. Snorkeling here is the quiet hour before the speedboats start arguing with the horizon.</p>
        </div>
    </article>
    <article class="chapter is-flip" id="bayside">
        <div class="film" data-film>
            <img class="is-on" src="miami-image-2.jpg" alt="Miami Bayside waterfront">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 01</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">02 / 07</p>
            <h2>Bayside docks</h2>
            <p>Luxury hulls next to working boats. The waterfront where tours leave and people watch. Glamour and bait shops sharing a zip code.</p>
        </div>
    </article>
    <article class="chapter" id="speedboat">
        <div class="film" data-film>
            <img class="is-on" src="miami-image-3.jpg" alt="Speed boat ride in the Atlantic">
            <img src="miami-image-8.jpg" alt="Speed boat on the Atlantic, another run" loading="lazy">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 02</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">03 / 07</p>
            <h2>Throttle up</h2>
            <p>Skyline as backdrop, spray in your face, a boat that does not do subtle. I went twice on the roll — same adrenaline, different light.</p>
        </div>
    </article>
    <article class="chapter is-flip" id="macaws">
        <div class="film" data-film>
            <img class="is-on" src="miami-image-4.jpg" alt="Blue-and-yellow macaws">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 01</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">04 / 07</p>
            <h2>Blue and yellow</h2>
            <p>Macaws that look like the city’s color wheel came alive. Tropical on purpose. A reminder Miami is not only concrete and neon.</p>
        </div>
    </article>
    <article class="chapter" id="everglades">
        <div class="film" data-film>
            <img class="is-on" src="miami-image-5.jpg" alt="Everglades wetlands">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 01</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">05 / 07</p>
            <h2>River of Grass</h2>
            <p>Airboat noise, then sudden quiet over sawgrass. Alligators that do not care about your itinerary. The wild Florida next to the Magic City.</p>
        </div>
    </article>
    <article class="chapter is-flip" id="nightlife">
        <div class="film" data-film>
            <img class="is-on" src="miami-image-6.jpg" alt="Nightlife in Miami">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 01</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">06 / 07</p>
            <h2>Second shift</h2>
            <p>When the sun drops, Miami clocks in again. Neon, bass, a sidewalk that does not empty. Sleep is optional; cafecito is not.</p>
        </div>
    </article>
    <article class="chapter" id="keywest">
        <div class="film" data-film>
            <img class="is-on" src="miami-image-7.jpg" alt="Key West Southernmost Point of the U.S.">
            <div class="film-ui">
                <button type="button" data-dir="-1" aria-label="Previous photo">←</button>
                <span class="count">01 / 01</span>
                <button type="button" data-dir="1" aria-label="Next photo">→</button>
            </div>
        </div>
        <div>
            <p class="index">07 / 07</p>
            <h2>Southernmost</h2>
            <p>The buoy, the queue, the sign that says Cuba is ninety miles. Standing at the continental edge after a Keys highway day still feels like a dare you already won.</p>
        </div>
    </article>

    <section class="unfinished" id="unfinished">
        <h2>Still on the list.</h2>
        <p class="unfinished-lead">I covered water and neon. These are the next tickets.</p>
        <div class="grid-3">
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🎨</span> Longer Wynwood night</h3>
                <p>Murals by day, galleries and bars after. I skimmed. Next time I stay.</p>
                <span class="price">Evening</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🎺</span> Little Havana deeper</h3>
                <p>Calle Ocho, domino park, a longer cafecito crawl. Cultural heartbeat worth more than a drive-by.</p>
                <span class="price">Half day</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🏝️</span> Key Biscayne slow day</h3>
                <p>Quieter sand than South Beach. Lighthouse, bikes, fewer poses.</p>
                <span class="price">Day</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🏛️</span> Full Vizcaya morning</h3>
                <p>Gardens without rushing. I owe the villa a quieter hour.</p>
                <span class="price">Ticket</span>
            </div>
        </div>
    </section>

    <section class="day-tours" id="day-tours">
        <h2>If you stretch the trip.</h2>
        <p class="day-tours-lead">Keys overnight, a second Everglades angle, or just more boat days.</p>
        <div class="grid-3">
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🌴</span> Key West overnight</h3>
                <p>Duval after dark beats a same-day turnaround. Southernmost at sunrise if you hate the midday line.</p>
                <span class="price">1–2 nights</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">🐊</span> Everglades longer</h3>
                <p>National Park trails beyond the airboat loop. Bring water and respect for wildlife.</p>
                <span class="price">Full day</span>
            </div>
            <div class="card">
                <h3><span class="emo" aria-hidden="true">⛵</span> Biscayne boat day</h3>
                <p>Islands, sandbars, another excuse to be on the water. Book when seas look kind.</p>
                <span class="price">Day</span>
            </div>
        </div>
    </section>

    <div class="next">
        <a href="../index.html">← Back to the atlas</a>
        <a href="../nassau/">Nassau is next →</a>
    </div>

    <footer>
        <span>Miami · United States</span>
        <span>globetrotwithveda.com</span>
    </footer>

{js}
</body>
</html>
"""
    html = head(
        "miami",
        "Miami itinerary: food, map, Everglades, Keys, and visa notes | Veda",
        "A Miami itinerary with snorkeling, Bayside, Everglades, Key West, food, and US domestic visa notes for Indian and US passports — written by Veda, who actually went.",
        "Miami itinerary: food, map, Everglades, Keys, and visa notes",
        "Places to go, what to eat, when to visit, and visa notes for Indian and US passports — in one Miami page.",
        "Miami waterfront and tropical sky",
        "Miami",
        "United States",
    ) + body
    out = ROOT / "miami/index.html"
    out.write_text(html)
    print("wrote", out, "bytes", out.stat().st_size)


if __name__ == "__main__":
    write_chicago()
    write_miami()
