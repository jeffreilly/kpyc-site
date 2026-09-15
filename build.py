#!/usr/bin/env python3
"""Build the KPYC interim site pages from shared templates.

Run `python3 build.py` from the repo root. index.html is hand-maintained
(notice, contacts, launch hours) and is not touched by this script except
for the shared navigation bar, which is inserted between the markers
<!-- nav:start --> and <!-- nav:end -->.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NAV = [
    ("index.html", "Home"),
    ("membership.html", "Membership"),
    ("new-members.html", "New Members"),
    ("launch.html", "Launch"),
    ("clubhouse.html", "Clubhouse"),
    ("docks-moorings.html", "Docks &amp; Moorings"),
    ("sailing-school.html", "Sailing School"),
    ("social-education.html", "Social &amp; Education"),
    ("documents.html", "Documents"),
]

NAV_CSS = """
    /* nav-css:start */
    .nav { position: sticky; top: 0; z-index: 30; width: calc(100% + 2.5rem); background: #0d3b6e; color: #fff; margin: 0 -1.25rem 1.5rem; padding: 0 1.25rem; box-shadow: 0 2px 10px rgba(0,0,0,.15); }
    .nav-inner { max-width: 860px; margin: 0 auto; display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; padding: 0.55rem 0; }
    .nav-brand { display: flex; align-items: center; gap: 0.5rem; font-weight: 700; font-size: 0.95rem; color: #fff; text-decoration: none; margin-right: 0.5rem; white-space: nowrap; }
    .nav-brand img { height: 22px; width: auto; }
    .nav-links { list-style: none; display: flex; flex-wrap: wrap; gap: 0.15rem 0.2rem; }
    .nav-links a { color: #dbe6f5; font-size: 0.84rem; font-weight: 600; text-decoration: none; padding: 0.3rem 0.55rem; border-radius: 6px; display: inline-block; }
    .nav-links a:hover { background: rgba(255,255,255,0.12); color: #fff; }
    .nav-links a.active { background: #fff; color: #0d3b6e; }
    .tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.8rem; margin: 0.4rem 0 0.6rem; }
    .tile { display: block; background: #f8f9fb; border: 1px solid #eceff3; border-radius: 10px; padding: 0.9rem 1rem; text-decoration: none; color: inherit; transition: box-shadow .15s, transform .15s; }
    .tile:hover { box-shadow: 0 4px 14px rgba(0,0,0,.1); transform: translateY(-1px); }
    .tile .t { font-weight: 700; color: #0d3b6e; font-size: 0.95rem; }
    .tile .d { font-size: 0.83rem; color: #666; margin-top: 0.2rem; }
    @media (max-width: 700px) {
      .nav-inner { flex-wrap: nowrap; gap: 0.5rem; padding: 0.45rem 0; }
      .nav-brand { margin-right: 0; }
      .nav-links { flex-wrap: nowrap; overflow-x: auto; -webkit-overflow-scrolling: touch; scrollbar-width: none; flex: 1; min-width: 0; mask-image: linear-gradient(to right, #000 92%, transparent); -webkit-mask-image: linear-gradient(to right, #000 92%, transparent); }
      .nav-links::-webkit-scrollbar { display: none; }
      .nav-links a { white-space: nowrap; font-size: 0.86rem; padding: 0.35rem 0.6rem; }
      .tiles { grid-template-columns: 1fr; }
      .nav.js .nav-toggle { display: inline-flex; flex-direction: column; justify-content: center; gap: 5px; margin-left: auto; background: none; border: 0; padding: 10px 8px; cursor: pointer; }
      .nav.js .nav-toggle span { display: block; width: 24px; height: 2.5px; background: #fff; border-radius: 2px; transition: transform .2s, opacity .2s; }
      .nav.js.open .nav-toggle span:nth-child(1) { transform: translateY(7.5px) rotate(45deg); }
      .nav.js.open .nav-toggle span:nth-child(2) { opacity: 0; }
      .nav.js.open .nav-toggle span:nth-child(3) { transform: translateY(-7.5px) rotate(-45deg); }
      .nav.js .nav-inner { flex-wrap: wrap; }
      .nav.js .nav-links { display: none; flex-direction: column; width: 100%; flex: none; overflow: visible; mask-image: none; -webkit-mask-image: none; padding: 0.25rem 0 0.6rem; gap: 0.1rem; }
      .nav.js.open .nav-links { display: flex; }
      .nav.js .nav-links a { display: block; font-size: 0.98rem; padding: 0.6rem 0.75rem; }
    }
    .nav-toggle { display: none; }
    /* nav-css:end */
"""

NAV_SCRIPT = """<script>document.addEventListener('DOMContentLoaded',function(){var n=document.querySelector('.nav'),t=n&&n.querySelector('.nav-toggle'),l=n&&n.querySelector('.nav-links');if(!n||!t||!l)return;n.classList.add('js');t.addEventListener('click',function(){var o=n.classList.toggle('open');t.setAttribute('aria-expanded',o?'true':'false');});l.addEventListener('click',function(e){if(e.target.tagName==='A'){n.classList.remove('open');t.setAttribute('aria-expanded','false');}});document.addEventListener('click',function(e){if(!n.contains(e.target)){n.classList.remove('open');t.setAttribute('aria-expanded','false');}});});</script>"""

CSS = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: #f4f6f9; color: #1a1a2e; line-height: 1.65; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 0 1.25rem 2rem; }
    .card { background: #fff; border-radius: 14px; box-shadow: 0 4px 24px rgba(0,0,0,.10); max-width: 860px; width: 100%; overflow: hidden; }
    .card + .card { margin-top: 1.5rem; }
    .card[id] { scroll-margin-top: 5rem; }
    .card-header { background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa8 100%); color: #fff; padding: 2rem 2rem 1.6rem; text-align: center; }
    .card-header h1 { font-size: clamp(1.3rem, 4vw, 1.8rem); font-weight: 700; letter-spacing: -0.01em; margin-bottom: 0.25rem; }
    .card-header .est { font-size: 0.85rem; opacity: 0.7; letter-spacing: 0.04em; }
    .card-header img.burgee { height: 54px; width: auto; margin-bottom: 0.6rem; }
    .card-body { padding: 1.75rem 2rem 2rem; }
    h2 { font-size: 1.15rem; font-weight: 700; color: #0d3b6e; margin: 1.4rem 0 0.5rem; }
    h2:first-child { margin-top: 0; }
    h3 { font-size: 0.98rem; font-weight: 700; color: #1a5fa8; margin: 1rem 0 0.35rem; }
    p { font-size: 0.97rem; color: #444; margin-bottom: 0.9rem; }
    ul, ol { margin: 0.2rem 0 0.9rem 1.4rem; color: #444; font-size: 0.95rem; }
    li { margin-bottom: 0.3rem; }
    a { color: #0d3b6e; }
    table { width: 100%; border-collapse: collapse; margin: 0.4rem 0 1rem; font-size: 0.92rem; }
    th, td { text-align: left; padding: 0.55rem 0.7rem; border-bottom: 1px solid #eceff3; vertical-align: top; }
    th { color: #0d3b6e; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em; }
    tr:last-child td { border-bottom: none; }
    @media (max-width: 600px) {
      table.stack, table.stack tbody, table.stack tr, table.stack td { display: block; width: 100%; }
      table.stack thead { display: none; }
      table.stack tr { border: 1px solid #eceff3; border-radius: 8px; padding: 0.5rem 0.75rem; margin-bottom: 0.6rem; background: #f8f9fb; }
      table.stack td { border: none; padding: 0.15rem 0; }
      table.stack td::before { content: attr(data-label); display: block; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; color: #0d3b6e; font-weight: 700; margin-top: 0.3rem; }
      table.stack td:first-child::before { margin-top: 0; }
      table.stack td:first-child { font-weight: 700; color: #0d3b6e; }
    }
    .rules-box { margin: 0.75rem 0 1.25rem; background: #fdf1f1; border: 1px solid #f3d4d4; border-radius: 10px; padding: 0.85rem 1rem; }
    .rules-label { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: #7a1f1f; margin-bottom: 0.45rem; }
    .rules-box ul, .rules-box ol { margin-bottom: 0; color: #7a1f1f; }
    .note { background: #fff8e1; border: 1px solid #f0d060; border-radius: 10px; padding: 0.75rem 1rem; font-size: 0.88rem; color: #6b5200; margin: 0.6rem 0 1.1rem; }
    .info { background: #eef4fb; border: 1px solid #cfdff2; border-radius: 10px; padding: 0.75rem 1rem; font-size: 0.9rem; color: #1e3a5f; margin: 0.6rem 0 1.1rem; }
    .btn { display: inline-block; background: #0d3b6e; color: #fff; text-decoration: none; font-weight: 600; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 8px; margin: 0.2rem 0.4rem 0.6rem 0; }
    .btn.secondary { background: #e9eef6; color: #0d3b6e; }
    .btn:hover { opacity: 0.92; }
    .photos { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.8rem; margin: 0.4rem 0 1rem; }
    .photos img { width: 100%; height: auto; border-radius: 8px; border: 1px solid #e3e6ea; }
    .photos .cap { font-size: 0.78rem; color: #777; margin-top: 0.2rem; }
    .toc { list-style: none; display: flex; flex-wrap: wrap; gap: 0.4rem 1.1rem; margin: 0 0 1rem; }
    .toc a { font-size: 0.88rem; font-weight: 600; text-decoration: none; }
    footer { text-align: center; font-size: 0.78rem; color: #aaa; margin-top: 2rem; }
    @media (max-width: 600px) { .card-body { padding: 1.25rem 1.1rem 1.5rem; } .nav-links a { font-size: 0.8rem; padding: 0.25rem 0.45rem; } }
"""

# Upcoming clubhouse dates, fall and winter 2026. kind: "club" (named) or "rental" (shown as reserved).
EVENTS = [
    ("Thu Oct 15", "rental", "Reserved: private member event"),
    ("Sat Oct 17", "club", "Docks Out work day, 8:00 AM to noon"),
    ("Thu Oct 22", "club", "October semiannual membership meeting: Director elections, trophies, sailing school vote"),
    ("Fri Oct 30", "rental", "Reserved: private event (pending)"),
    ("Sun Nov 8 or Mon Nov 9", "rental", "Reserved: private member event (date to be confirmed)"),
    ("Sat Nov 14", "club", "Club event, details to be announced"),
    ("Fri Nov 20", "rental", "Reserved: private member event"),
    ("Sun Nov 29", "rental", "Reserved: private member event"),
    ("Sat Dec 5", "club", "NEI (Dylan Kimmel), private event"),
    ("Sat Dec 12", "club", "KPYC Christmas Party"),
    ("Fri Jan 1", "club", "KPYC New Year's Day Bloody Mary Party"),
]


def events_table(kinds=("club", "rental")):
    rows = "".join(
        f"<tr><td>{d}</td><td>{'Club event' if k == 'club' else 'Reserved'}</td><td>{t}</td></tr>"
        for d, k, t in EVENTS if k in kinds
    )
    return f"<table><thead><tr><th>Date</th><th>Type</th><th>Details</th></tr></thead><tbody>{rows}</tbody></table>"


def nav_html(active):
    items = "".join(
        f'<li><a href="{href}"{" class=\"active\"" if href == active else ""}>{label}</a></li>'
        for href, label in NAV
    )
    return (
        '<nav class="nav"><div class="nav-inner">'
        '<a class="nav-brand" href="index.html"><img src="assets/KPYC_burgee_wave.png" alt="">KPYC</a>'
        '<button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>'
        f'<ul class="nav-links">{items}</ul></div></nav>'
    )


def stack_tables(html):
    """Give every table a mobile stacking class and data-label attributes from its header row."""
    def fix(m):
        table = m.group(0)
        heads = re.findall(r"<th[^>]*>(.*?)</th>", table, re.S)
        if not heads or "</thead>" not in table:
            return table
        labels = [re.sub(r"<[^>]+>", "", h).strip() for h in heads]
        head, body = table.split("</thead>", 1)
        def fix_row(rm):
            row = rm.group(0)
            i = [0]
            def fix_td(tm):
                lab = labels[i[0]] if i[0] < len(labels) else ""
                i[0] += 1
                return f'<td data-label="{lab}"' + tm.group(1)
            return re.sub(r"<td((?:\s[^>]*)?>)", fix_td, row)
        body = re.sub(r"<tr>.*?</tr>", fix_row, body, flags=re.S)
        return (head + "</thead>" + body).replace("<table>", '<table class="stack">', 1)
    return re.sub(r"<table>.*?</table>", fix, html, flags=re.S)


def page(filename, title, subtitle, body, toc=None):
    toc_html = ""
    if toc:
        toc_html = '<ul class="toc">' + "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in toc) + "</ul>"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | Kittery Point Yacht Club</title>
  <link rel="icon" href="assets/favicon.png">
  <style>{NAV_CSS}{CSS}</style>
</head>
<body>
  {nav_html(filename)}
  <div class="card">
    <div class="card-header">
      <img class="burgee" src="assets/KPYC_burgee_wave.png" alt="KPYC burgee">
      <h1>{title}</h1>
      <div class="est">{subtitle}</div>
    </div>
    <div class="card-body">
      {toc_html}
      {stack_tables(body)}
    </div>
  </div>
  {NAV_SCRIPT}
  <footer>Kittery Point Yacht Club &middot; 328 Portsmouth Ave., PO Box 373, New Castle, NH 03854<br>Interim website. Content is drawn from the club's printed Welcome booklet and earlier website and is being reviewed by the committees; please confirm fees and dates with the officer listed.</footer>
</body>
</html>
"""
    (ROOT / filename).write_text(html)
    print("wrote", filename)


# ---------------------------------------------------------------- pages

MEMBERSHIP = """
<h2 id="join">How to join</h2>
<p>Membership in the Kittery Point Yacht Club is open to individuals with an active interest in boating who want to be part of a volunteer-run club. The Club is at its By-Laws limit of 200 Regular Members, so approved applicants are placed on an ordered waiting list and move up as Regular Members resign, in the order their completed applications were received.</p>
<h3>Membership application procedures</h3>
<ol>
  <li>Complete the application and pay the non-refundable $250 application fee.</li>
  <li>You will receive a confirmation, and each of your two sponsors will be asked to submit a confidential recommendation. Sponsors must be Regular Members in good standing for six or more months and not from the same household as the applicant. It is the applicant's responsibility to make sure both recommendations are submitted promptly; the application is not complete until both are received, and the date of the second recommendation sets your place on the waiting list.</li>
  <li>Once both sponsor recommendations are received, the Membership Committee presents your complete application to the Board of Directors at the next monthly meeting for consideration, including review of any membership openings due to resignations. The Board vote (four affirmative votes required) determines approval onto the waiting list.</li>
  <li>If approved, you are added to the official waiting list in the order your completed application was received.</li>
  <li>When an opening occurs and you reach the top of the list, the Treasurer contacts you with payment instructions. You then become a Probationary Member for one month, with all the privileges of Regular Members except eligibility to serve on the Board, and are invoiced for annual dues prorated monthly from your activation month through December 31. Payment is due immediately to begin the probationary period.</li>
  <li>At the end of the one-month probationary period you purchase one Share of KPYC stock for $510, full payment required. On receipt of payment you become a full Regular Member.</li>
</ol>
<p><strong>KPYC is a 100 percent volunteer-run club.</strong> Our exceptionally low dues are possible only because every member contributes time and talent. We strongly encourage Probationary Members to use their first 30 days to review the By-Laws, meet the committee chairs, and choose at least one committee where they can actively volunteer. This is a core part of our culture and what makes KPYC special.</p>
<p>Spouses and children under 18 in the member's household are covered by the one Share, with one vote per Share.</p>

<h2 id="dues">Fees, dues and Share Value</h2>
<table>
  <thead><tr><th>Item</th><th>Amount (2026)</th></tr></thead>
  <tbody>
    <tr><td>Application fee (paid with the application; non-refundable, even if you later withdraw)</td><td>$250</td></tr>
    <tr><td>Annual dues (regular membership; prorated by month in your first year)</td><td>$500</td></tr>
    <tr><td>Share purchase at the then current price (one-time, after the probationary month; KPYC will purchase the Share back on resignation, at the then current price, once a new member takes your place)</td><td>$510</td></tr>
  </tbody>
</table>
<p>Dues notices for continuing members go out the first week of February; dues unpaid after March 30 are subject to a late fee. Payment of any KPYC fees by published electronic means is highly preferable. Checks are payable to Kittery Point Yacht Club and must include an additional $5 handling fee. <em>(Electronic payment preference and the check handling fee are pending Board approval.)</em></p>

<h2 id="application">Application form</h2>
<p>The application is a four-page PDF: the procedures, the application itself, and one Sponsor Recommendation page for each of your two sponsors.</p>
<a class="btn" href="docs/KPYC_Membership_Application_2026.pdf">Download the Membership Application (PDF)</a>
<h3>How to submit while the online form is offline</h3>
<ol>
  <li>Print and complete page 2, sign it, and send it with your $250 check (payable to Kittery Point Yacht Club) to the Membership Chair: Chris Snow, Kittery Point Yacht Club, PO Box 373, New Castle, NH 03854-0373. You may email a scan of the application to <a href="mailto:csnow@nhpta.com">csnow@nhpta.com</a> and mail the check separately.</li>
  <li>Give each of your two sponsors a copy of a Sponsor Recommendation page (pages 3 and 4). Each sponsor sends their completed page directly to the Membership Chair by mail or email, not back to you, so recommendations stay confidential.</li>
  <li>Your application is complete when all three items have arrived. The date the last item is received is your date of record for the waiting list, and the Membership Chair will confirm by email.</li>
</ol>
<div class="info">The online application and sponsor forms will return with the new club website. Questions: Chris Snow, 603-731-3348, or <a href="mailto:membership@kpyc.org">membership@kpyc.org</a>.</div>
<a class="btn secondary" href="docs/KPYC_ByLaws_January_2024.pdf">KPYC Constitution and By-Laws (PDF)</a>

<h2 id="faq">Frequently asked questions</h2>
<h3>How do I get a clubhouse key?</h3>
<p>You receive a key automatically once accepted as a member. For an extra key, contact the Treasurer.</p>
<h3>How do I get a burgee or club gear?</h3>
<p>Every new member receives their first burgee free when they join. Additional burgees, shirts and other club gear are available from the Quartermaster, Adam Shapiro (<a href="mailto:adamhshapiro@gmail.com">adamhshapiro@gmail.com</a>).</p>
<h3>How do I rent the clubhouse for a private event?</h3>
<p>See the <a href="clubhouse.html#rentals">Clubhouse Rentals</a> section. Rentals are for members only, in the off-season.</p>
<h3>When are the membership meetings?</h3>
<p>Two a year: one in October, when Directors are elected and trophies awarded, and one in January, when dues, the Share Value and any By-Law changes are set. This year's October meeting is Thursday, October 22, 2026.</p>
"""

NEW_MEMBERS = """
<a class="btn" href="docs/KPYC_Welcome_Booklet_2026.pdf">Download the New Member Welcome Booklet (PDF)</a>
<p style="font-size:0.85rem;color:#777;">The booklet given to new members: welcome letter, launch rules, this reference guide, clubhouse rules, Board policies, facilities, the social season, the sailing school, and 2026 club contacts.</p>
<p>Welcome to the Kittery Point Yacht Club. We want everyone to enjoy their association with the Club, so this guide will help you navigate your way around. Please also read the <a href="clubhouse.html#rules">Clubhouse Rules</a>, the <a href="documents.html#policies">Board of Directors' Established Policies</a>, and the <a href="docs/KPYC_ByLaws_January_2024.pdf">Constitution and By-Laws</a>. If you have a question these do not answer, contact any member of the Board of Directors.</p>

<h2 id="welcome">Welcome aboard</h2>
<p>On behalf of the members, officers, directors and staff, we are thrilled you have chosen to join our family. As a new member you will receive this reference guide, the Launch Rules and Etiquette, the Board of Directors' Policies, the Clubhouse Rules, the Constitution and By-Laws, a burgee, a clubhouse key, the season's social calendar, club contacts, and your Member Share Certificate.</p>
<p>Please let us know how we can best match your skills to the volunteer tasks and projects. Volunteerism is at the root of our success, so come join in the fun! The Board of Directors meets monthly; the date is posted on the clubhouse bulletin board. Feel free to stop by, and contact the Membership Chair, Chris Snow, with any questions.</p>

<h2 id="structure">How the club is organized</h2>
<p>The Club has a nine-member Board of Directors that meets monthly; members are welcome to attend and observe Board meetings, and the dates are posted on the clubhouse bulletin board. Three Directors are elected each year by the membership, for three-year terms, at the annual meeting in October, and a Director may serve no more than two consecutive three-year terms. The Board elects the Commodore, Vice Commodore, Rear Commodore, Fleet Captain, Secretary and Treasurer as Club Officers, and appoints a Quartermaster. Members volunteer to chair and serve on the standing committees: House, Race, Social, Junior Activities (Sailing School), Education, Membership, Auditing and Election, along with the Launch Services Committee. There is plenty of need for volunteers and we would welcome your involvement. Current officers and chairs are listed on the <a href="index.html#contacts">contacts page</a>.</p>

<h2 id="using">Using the clubhouse</h2>
<p>The clubhouse and deck are for everyone's use, so please clean up after yourself. You are welcome to use the clubhouse, deck, grill and kitchen for yourselves and your guests. As a member you may host an indoor gathering with guests without renting the club, but other members may be coming and going. To decorate the club or send out invitations for an event, you must reserve it as a rental (off-season only; see <a href="clubhouse.html#rentals">Clubhouse Rentals</a>).</p>

<h3>Front door</h3>
<p>To keep the front door unlocked during your stay: from the inside, find the pin hanging on the panic bar (older instructions refer to an Allen wrench stowed on the right-hand door casing). With the panic bar held down, insert the pin in the hole on top of the bar; the bar is now locked down. To undo this, pull the pin.</p>

<h3>Cleaning</h3>
<p>The club has a cleaning person for the larger tasks, but keeping the clubhouse neat is every member's responsibility. Brooms, dustpans and the vacuum are behind the kitchen door; the central vacuum outlet is low on the dart board wall; the wet mop and bucket are in the shower opposite the bathroom; trash bags and paper towels are under the kitchen sink; the dumpster is at the right rear of the property. Bag recyclable cans and leave them beside the dumpster.</p>

<h3>Parking</h3>
<p>Parking is at a premium in summer. On Tuesday and Thursday race nights, please carpool when possible and pack in to the right of the clubhouse. In summer the parking along the left-hand property line is reserved for sailing school students. See the parking plan posted in the clubhouse, and please respect the spaces for our upstairs tenants.</p>

<h3>Noise</h3>
<p>Out of respect for our apartment tenants upstairs and our residential neighbors to the right of the clubhouse, no activities are conducted outdoors on that side of the building and noise is kept to a minimum. Noise is restricted to conversational tones after 10:00 PM and there is to be no noise after 11:00 PM.</p>

<h3>Chairs and tables</h3>
<p>Chairs and tables are behind the roll-out cabinet in the kitchen. Note the labeled stacking order so everything fits back where it belongs. One long table stays out permanently in the rear right-hand corner.</p>

<h3>Ice and rubbish</h3>
<p>Bags of ice are in the freezer in the wooden box on the fixed pier, on the honor system. Rubbish from your boat goes in the dumpster in the parking lot.</p>

<h3>Lighting the parking lot</h3>
<p>In the evening, please light the parking lot after dark. On the kitchen wall to the right of the telephone are four switches labeled North, South, East and West floodlight zones: South lights the front parking area, East the right-hand side of the clubhouse, and North and West the exterior deck. If you are the last to leave, shut off all lights.</p>

<h3>Fireplace</h3>
<p>The fireplace has been converted to gas. Follow the lighting and shut-off instructions posted at the fireplace, and make sure it is fully off before you leave. Do not bring in or burn wood.</p>

<h3>Last to leave</h3>
<p>If you are the last member to leave, check that all doors and windows are locked, all stove burners and oven elements are off, all interior and exterior lights (including floodlights) are off, and the heat is turned down to 55 &deg;F.</p>

<h2 id="season">The club year</h2>
<p><strong>Work days.</strong> In spring and fall we hold "Docks In" and "Docks Out" work days from 8:00 AM to noon, with coffee and lunch provided. All members are asked to help; it is a great way to meet people and it keeps dues reasonable. Docks Out 2026 is Saturday, October 17.</p>
<p><strong>Membership meetings.</strong> Two a year: October (Director elections and trophies) and January (dues, Share Value, By-Law changes). One member per family Share is expected to attend. A quorum is required, so please plan to join us. The 2026 October meeting is Thursday, October 22.</p>
<p><strong>Social functions.</strong> The Social Committee runs events through the season; see <a href="social-education.html">Social &amp; Education</a>. Members may always bring guests. There is no dress code.</p>
<p><strong>Launch, docks and moorings.</strong> See the <a href="launch.html">Launch</a> and <a href="docks-moorings.html">Docks &amp; Moorings</a> pages.</p>
<p><strong>Sailing School.</strong> The club operates the KPYC Sailing School for kids and adults; see <a href="sailing-school.html">Sailing School</a>.</p>
<p><strong>Club gear.</strong> Your first burgee is free, with the compliments of the Club. Additional burgees, clothing and other items with the KPYC burgee are available from the Quartermaster, Adam Shapiro.</p>
"""

LAUNCH = """
<h2 id="hours">Hours</h2>
<p>The launch operates from late spring into fall and monitors <strong>VHF channel 68</strong> during operating hours. There is no per-ride fee; annual dues support the service. Tipping the driver is at your discretion.</p>
<table>
  <thead><tr><th>Day</th><th>Hours</th></tr></thead>
  <tbody>
    <tr><td>Tuesday and Thursday</td><td>2:00 PM to 9:00 PM</td></tr>
    <tr><td>Friday</td><td>11:00 AM to 8:00 PM</td></tr>
    <tr><td>Saturday and Sunday</td><td>9:00 AM to 8:00 PM</td></tr>
  </tbody>
</table>
<div class="note">Hours change with the season and driver availability; holiday hours are announced by email. Questions about launch service go to the Launch Services Committee chair, Brendan Cooney (<a href="mailto:br_cooney@mac.com">br_cooney@mac.com</a>), or the Vice Commodore, Kevin McCoole, for launch drivers.</div>
<p>Our launch makes over a thousand trips each summer, so please have all your crew present before venturing out to your boat.</p>

<h2 id="rules">Launch rules and etiquette</h2>
<div class="rules-box">
  <div class="rules-label">Strictly enforced</div>
  <ul>
    <li>Maximum capacity: six passengers</li>
    <li>No open containers at any time</li>
    <li>The driver's directions on seating, trim, boarding and safety are to be followed without exception</li>
  </ul>
</div>
<ol>
  <li>Those requesting and utilizing the KPYC launch service do so at their own risk and agree to hold harmless The Kittery Point Yacht Club, its Board of Directors, officers, employees and members from any and all damage, loss or injury resulting from said launch service.</li>
  <li>Launch capacity is limited to six (6) passengers.</li>
  <li>The "No Open Container" rule is in effect at all times.</li>
  <li>Directions of the launch driver with respect to seating positions, trim of the boat, embarking, debarking and any other safety related issues are to be followed without exception.</li>
  <li>In the interest of better service and efficiency, the launch driver may at his or her discretion, and not exceeding launch capacity, take aboard individuals or parties traveling to the same or nearby destination regardless of their position in the queue awaiting launch service.</li>
  <li>All members and guests will maintain decorum that is conducive to good order and is considerate of others.</li>
  <li>Unaccompanied non-members and guests will be afforded launch service to a member's boat provided that member is already on board his or her vessel.</li>
  <li>Please plan around the posted hours and make alternative transportation arrangements as needed.</li>
  <li>Comments, complaints, issues or suggestions on any aspect of Club operations should be directed to any Director, the House Committee Chair, or the Commodore. Contact information is on the <a href="index.html#contacts">contacts page</a> and the Club bulletin board.</li>
</ol>
"""

CLUBHOUSE = """
<h2 id="facilities">Facilities</h2>
<div class="photos">
  <div><img src="assets/clubhouse_front.jpg" alt="KPYC clubhouse"><div class="cap">The clubhouse at 328 Portsmouth Avenue, Goat Island</div></div>
  <div><img src="assets/deck_view_river.jpg" alt="Deck view of the Piscataqua"><div class="cap">The deck and the Piscataqua River</div></div>
</div>
<p>Kittery Point Yacht Club is located in New Castle, NH, on the southern shore of the Piscataqua River. Its clubhouse, on Goat Island, stands opposite Seavey Island, home of the historic Portsmouth Naval Shipyard. Ships from all over the world pass before it, vying with local lobster and fishing boats during the week and hundreds of pleasure boats on holidays and weekends. The clubhouse has a wrap-around deck, a kitchen and bar, and one shower. It is not wheelchair accessible; there are two broad steps up to the deck. Per the occupancy permit, the limit is 70 persons in the club at any one time.</p>
<p>A member of US Sailing, KPYC is well represented in local, regional and occasionally national events, with members racing and cruising a variety of boats. The club sponsors the KPYC Sailing School, the Seacoast's only public sailing school and youth racing program. Members are drawn mainly from New Hampshire and Maine, and most enjoy boating and organized social activities during the main season from May to October, with potluck dinners and casual gatherings through the year.</p>

<h2 id="rules">Clubhouse rules</h2>
<ol>
  <li>The Clubhouse is for the exclusive use of members and invited guests.</li>
  <li>There shall be no social activity conducted on club property east of the building.</li>
  <li>No pets allowed on the premises except going to and from a boat. All pets must be on a leash. Members must clean up after their animals.</li>
  <li>There shall be no borrowing or renting of Club property.</li>
  <li>No child under 18 may be allowed the use of the Clubhouse unless accompanied by a member or parent responsible for his or her supervision.</li>
  <li>Members shall be held responsible for any property damaged or lost by themselves or their guests.</li>
  <li>Guests, other than visiting yachtsmen, must be accompanied by a member and that member shall be held responsible for the conduct of the guest while on the premises. Guests of members may be taken to a member's boat by the launch only when the member is already on board.</li>
  <li>The last member to leave the Clubhouse is responsible for locking doors and windows, turning out lights, and turning down the heat.</li>
  <li>The Clubhouse is available for member use and shall be left "shipshape" after each use, especially the bar and galley.</li>
  <li>Application by a member for rental of the Club for a private event shall be made to the Social Committee on the form provided. The Club will not be rented from May 1 to October 15.</li>
  <li>The member holding a private party at the Club shall be present at all times and shall be responsible for proper conduct of guests and all damage or loss to the Club. Out of respect for our tenant, noise levels are restricted to conversational tones after 10:00 PM, with no noise after 11:00 PM. Clean-up following rentals must begin no earlier than 8:00 AM on the day following the event and be completed no later than 10:00 AM.</li>
  <li>Visiting yachtsmen from other yacht clubs may be allowed use of the club facilities during normal club hours (Steward or dock attendant on duty).</li>
  <li>Tie-up on the dock is limited to pick up, drop off, and provisioning only. In case of an emergency, or if there is a need to use the dock for an extended period, call the House Committee Chair.</li>
  <li>Only Club members and Sailing School students will be allowed to park on the premises on Tuesday nights. Guests are to park on the road or elsewhere. This policy is in effect from Docks In to Docks Out.</li>
  <li>The Club facility will be locked when no members are present and when the Steward is not on the premises.</li>
  <li>Sailing School students will be monitored by the instructors, who will enforce the house rules.</li>
  <li>Neither profanity nor other offensive behavior will be tolerated; a member's suspension or expulsion could result.</li>
  <li>There shall be no smoking in the Clubhouse.</li>
</ol>

<h2 id="rentals">Clubhouse rentals</h2>
<p>Club members may rent the Club for private functions on a first come, first served basis after October 15 and before May 1. No rentals are permitted from May 1 through October 15. Any member who rents the Club must be present at the event, and the rental and deposit checks must be written by the member, not by someone they are sponsoring. Members must reserve the Club if they want exclusive use of the Clubhouse or plan to decorate it; an event that involves decorating and inviting people is a "party" under Board policy and is subject to the rental policy. The Club may not be used for commercial purposes.</p>
<div class="note">The last published rental fee was $300 for members plus a refundable deposit check. Confirm the current fee, deposit and payment method with the House Chair, Dylan Kimmel (<a href="mailto:dkimmel@neintegration.com">dkimmel@neintegration.com</a>), or the Social Chair, Alison Magill, before booking. While the website is down, reservations are made by email to the House Chair rather than through the online form.</div>
<h3>Clubhouse calendar, fall and winter 2026</h3>
<p>The club will not have an online calendar until the new website launches. Dates already booked or scheduled are listed here and on the clubhouse bulletin board; check with the House Chair before requesting a date.</p>
""" + events_table() + """
<h3>How to reserve</h3>
<ol>
  <li>Check the calendar on the clubhouse wall for your date, then email the House Chair with your name, phone, requested date, start and end times, and expected number of guests.</li>
  <li>Sign the Release and Hold Harmless Agreement and agree to pay for any damage to the club.</li>
  <li>Pay the rental fee and provide the deposit check. Once confirmed, your reservation is posted on the clubhouse calendar.</li>
  <li>During the event, post a sign on the front door: "Private Member Event Underway". The club's beverage refrigerator is not available during rentals.</li>
  <li>To cancel, notify the House Chair immediately; payments are refunded and the date is released.</li>
</ol>
<h3>Rental rules</h3>
<p>Our cleaning person tries to schedule the weekly cleaning the day before your rental, but has no control over what happens between the cleaning and your arrival. Chairs and tables are behind the roll-out cabinet in the kitchen in a labeled stacking order; the one long table stays out in the rear right-hand corner. If your function runs into the evening, light the parking lot from the four floodlight switches on the kitchen wall. Noise is restricted to conversational tones after 10:00 PM and there is to be no noise after 11:00 PM.</p>
<p>It is your responsibility to leave the Clubhouse shipshape. All rentals must, at the end of the function:</p>
<ul>
  <li>Wet mop (warm water only) the kitchen, bathrooms and hardwood floors, and vacuum the carpets.</li>
  <li>Clean bathroom toilets and sinks.</li>
  <li>Wash, dry and put away any pots, pans, dishes or utensils used; wipe down the bar and kitchen counters.</li>
  <li>Take out all trash (kitchen and bathrooms) and replace with clean bags; bag recyclable cans beside the dumpster.</li>
  <li>Check that all doors and windows are locked, no burners or oven elements are on, lights are out including the floodlights, and the heat is turned down.</li>
</ul>
<p>If clean-up is deferred to the following day, it must start no earlier than 8:00 AM and finish by 10:00 AM. If additional cleaning is needed, the deposit may be used to pay for it.</p>
"""

DOCKS = """
<h2 id="tieup">Front float and dinghy docks</h2>
<p>The front tie-up float is approximately 75 feet long with 6 feet of depth. There is a shallow spot at the extreme east end. Currents in the Piscataqua are swift and there is heavy river traffic with resulting wakes; boats that tie up should use long spring lines and plenty of fenders. Tie-up is limited to pick up, drop off and provisioning; for an emergency or extended use, call the House Chair. Dinghy docks are inboard of the float. The typical tidal range is 9 to 11 feet, and the ramp to the float can be steep at low tide.</p>

<h2 id="dinghies">Dinghy, kayak and paddle board storage</h2>
<table>
  <thead><tr><th>Storage</th><th>Season fee (2026)</th><th>Notes</th></tr></thead>
  <tbody>
    <tr><td>Dinghy on the inside floats</td><td>$175</td><td>Sign up in the first quarter (January to March). Space is limited to about 40 dinghies. Maximum 12 feet LOA. Hard-sided dinghies are not permitted. Outboards must be left tilted down in the water or with the prop covered by a bucket. Spaces are first come, first served and not assigned.</td></tr>
    <tr><td>Kayak or paddle board on the racks at the club's new property</td><td>$150 each</td><td>Racks hold three per section. Nothing may be stored on top of the racks.</td></tr>
    <tr><td>Locker</td><td>$50</td><td>Subject to availability.</td></tr>
  </tbody>
</table>
<p>Every dinghy, kayak and paddle board must be clearly marked with the member's name and must display the current season's sticker. Stickers are issued by the Treasurer once the fee is paid. <strong>Craft without a current season sticker will be removed.</strong> Kayaks and paddle boards are cleared from the racks at the end of the season so the sailing school boats can be stored for the winter.</p>

<h2 id="moorings">Club moorings</h2>
<p>The Club rents moorings to members by the season, in the river in front of the clubhouse and in the Back Channel. There is a waiting list. Any member renting a Club mooring must show that they are on a state or town mooring list somewhere in the area; Club moorings are not a permanent mooring solution. Contact the Dock Master, Doug Pinciaro (<a href="mailto:dpinciaro@comcast.net">dpinciaro@comcast.net</a>, 603-475-2828). The launch monitors VHF channel 68 during operating hours.</p>
<table>
  <thead><tr><th>Mooring</th><th>Season fee (2026)</th></tr></thead>
  <tbody>
    <tr><td>River mooring, in front of the clubhouse</td><td>$1,500</td></tr>
    <tr><td>Back Channel mooring</td><td>$1,250</td></tr>
  </tbody>
</table>
<p>By Board policy (1989), a $10 per night guest fee applies when a Club mooring is used by a guest; it covers launch service and use of the club and goes to the Club. The Club asks the mooring's renter for permission before assigning it to a guest.</p>

<h2 id="shoals">Isles of Shoals moorings</h2>
<p>The Club maintains three moorings in Gosport Harbor at the Isles of Shoals for two-day use on a first come, first served basis. Visiting boats are welcome to use them if available; the launch and steward are not involved with these moorings. Please check the pennant and hardware before use and limit rafting numbers in challenging conditions. The moorings as last reported by the Dock Master: NH 4641 (2,000 lb block), NH 4006 (3,000 lb block) and ME 911 (4,000 lb block).</p>

<h2 id="workdays">Docks In and Docks Out</h2>
<p>The floats go in each spring and come out each fall on member work days from 8:00 AM to noon, with coffee and lunch provided. All members are asked to help and to remove their dinghies before Docks Out. Docks Out 2026 is Saturday, October 17.</p>
"""

SCHOOL = """
<div class="photos">
  <div><img src="assets/school_photo_2_optis.jpg" alt="Optimists racing"></div>
  <div><img src="assets/school_photo_3_fleet.jpg" alt="Sailing school fleet"></div>
</div>
<p>The Kittery Point Yacht Club Sailing School has been teaching students the art and science of sailing for over 30 years. It is the Seacoast's only public sailing school and youth racing program, taught by US Sailing certified instructors on the quiet waters of the Back Channel. No matter your experience level, you will leave the school with a better understanding of sailing.</p>
<div class="info">Enrollment for the 2027 season, session dates and fees will be announced here and by email. For information contact the Sailing School Director, Kevin McCoole (<a href="mailto:kevinmccoole@rocketmail.com">kevinmccoole@rocketmail.com</a>, 207-703-4691).</div>

<h2 id="programs">Programs</h2>
<p>All programs run Monday through Thursday for two weeks; Fridays are reserved for make-up days lost to weather. Minimum age is 8. Parents are welcome at the orientation meeting during the first half hour of the first day of each session. Classes are held as scheduled regardless of weather and holidays unless notified by email.</p>
<h3>Beginner, mornings</h3>
<p>For sailors ages eight and older who are ready to learn and practice fundamental sailing skills while gaining confidence skippering 420s and Optimists. Sailors generally spend two to three years in the Beginner program before advancing. Students sail one to three per boat depending on skill. The goal is for each sailor to control the tiller and sail simultaneously and handle the boat independently. The curriculum covers nomenclature, knot tying, rigging, boat handling, wind direction, water safety and boat maintenance.</p>
<h3>Intermediate, afternoons</h3>
<p>A framework for racing practice, aimed at young people who have completed the Beginner course and are competent sailors. One-design racing in Optimists and 420s with a good deal of fun and friendly competition; young racers are encouraged to attend local events.</p>
<h3>Adult lessons, evenings</h3>
<p>For adults wanting to learn to sail, with a curriculum that parallels the Beginner course, one to three students per boat.</p>

<h2 id="know">Things students and parents need to know</h2>
<p><strong>Safety.</strong> All students take a swim test on the first day of each session. Life jackets are worn and fastened at all times on the water and on the docks. All instructors are US Sailing certified with basic first aid and CPR training. On-the-water activity is postponed for sudden weather changes, high winds or lightning. Bring sun protection.</p>
<p><strong>What to bring.</strong> A Coast Guard approved Type III (vest style) life jacket; sneakers or closed-toe boat shoes (no flip-flops or open sandals); appropriate clothing including a change of clothes, jacket, hat, sunglasses, sun block and towel; a snack and water bottle (no glass). Label personal items and leave valuables at home.</p>
<p><strong>Weather.</strong> Classes are held in inclement weather; on-the-water instruction may take place in the rain, and land-based instruction replaces it in severe weather.</p>
<p><strong>Clubhouse.</strong> Please arrive on time and pick up promptly. Students wait for class on the clubhouse porch or the grass near the boat racks, and may not pass through the gate to the dock ramp without an instructor. Bags may be stored inside on the sailing school table during class. Youth students are accompanied by an instructor while in the clubhouse. Sailing school students may park along the left-hand property line in summer.</p>

<h2 id="scholarship">Thomas Tarbell Memorial Scholarship</h2>
<p>The Sailing School offers scholarships through the Thomas Tarbell Memorial Scholarship Fund, providing free lessons for children in need. For information contact the Sailing School Director.</p>
"""

SOCIAL = """
<h2 id="upcoming">Upcoming club events</h2>
<p>Until the new website brings back the online calendar, upcoming club events are listed here and announced by email.</p>
""" + events_table(("club",)) + """
<h2 id="social">The social season</h2>
<div class="photos">
  <div><img src="assets/racing_66.jpg" alt="Racing off the club"></div>
  <div><img src="assets/racing_08.jpg" alt="Club racing"></div>
</div>
<p>Every Friday night in season is Pub Night on the deck. Around it the Social and Race Committees run a summer of events. Members may always bring guests; there is no dress code. Most events ask a modest contribution that covers dinner and refreshments, and some are potluck. Recent seasons have included:</p>
<ul>
  <li>Docks In and Docks Out work days, spring and fall</li>
  <li>Club barbecue and pig roast with live music</li>
  <li>Reggae night on the deck, followed by fireworks</li>
  <li>Ron Gibbons Memorial Regatta</li>
  <li>Fish fry with live music</li>
  <li>Edmund Tarbell Regatta, surf and turf with live music</li>
  <li>Lobsterman's bake (members only)</li>
  <li>Single Handed Regatta and Lobster Double Handed Regatta</li>
  <li>Launch driver appreciation night and the anniversary potluck (the club marked its 70th in September 2026)</li>
</ul>
<p>The current calendar is emailed to members and posted on the clubhouse bulletin board. Contact the Social Chair, Alison Magill (<a href="mailto:alimagill@gmail.com">alimagill@gmail.com</a>), for events, and the Rear Commodore, Sally Elshout (<a href="mailto:sallyelshout@yahoo.com">sallyelshout@yahoo.com</a>), for racing and regattas.</p>

<h2 id="racing">Racing</h2>
<p>Club racing takes place on Tuesday and Thursday evenings through the season, with regattas on selected weekends. Racers and members are asked to carpool on race nights, since parking is limited. Notices of race, sailing instructions and results are distributed by the Race Committee.</p>

<h2 id="education">Education program</h2>
<p>The Fleet Captain, Adam Shapiro (<a href="mailto:adamhshapiro@gmail.com">adamhshapiro@gmail.com</a>), organizes education events for members based on member interest. Past seasons have offered, with partners including Maine Maritime, Boatwise and New England Ropes:</p>
<ul>
  <li>Survival at sea tactics and survival equipment seminars</li>
  <li>Marine electronics, basic navigation and advanced navigation classes</li>
  <li>USCG launch operator and USCG Master (captain's) courses</li>
  <li>NASBLA safe boating certification</li>
  <li>Marine ropes seminar, anchoring workshop, and first aid, CPR and AED certification</li>
</ul>
<p>Upcoming classes are announced by email with registration deadlines and costs.</p>
"""

DOCUMENTS = """
<h2 id="downloads">Downloads</h2>
<div class="tiles">
  <a class="tile" href="docs/KPYC_ByLaws_January_2024.pdf"><div class="t">Constitution and By-Laws</div><div class="d">Revised January 2024 (PDF)</div></a>
  <a class="tile" href="docs/KPYC_Membership_Application_2026.pdf"><div class="t">Membership Application</div><div class="d">Procedures, application, and sponsor recommendation pages (PDF)</div></a>
  <a class="tile" href="docs/KPYC_Welcome_Booklet_2026.pdf"><div class="t">New Member Welcome Booklet</div><div class="d">2026 edition of the booklet given to new members (PDF)</div></a>
</div>

<h2 id="pages">Club rules and guides on this site</h2>
<div class="tiles">
  <a class="tile" href="new-members.html"><div class="t">New Member Reference Guide</div><div class="d">Getting around the club</div></a>
  <a class="tile" href="launch.html#rules"><div class="t">Launch Rules and Etiquette</div><div class="d">Hours, capacity, conduct</div></a>
  <a class="tile" href="clubhouse.html#rules"><div class="t">Clubhouse Rules</div><div class="d">Eighteen house rules</div></a>
  <a class="tile" href="clubhouse.html#rentals"><div class="t">Rental Policy and Rules</div><div class="d">Off-season member rentals</div></a>
  <a class="tile" href="docks-moorings.html"><div class="t">Docks and Moorings</div><div class="d">Float, dinghies, river and Shoals moorings</div></a>
  <a class="tile" href="membership.html"><div class="t">Membership</div><div class="d">How to join, dues, Share Value</div></a>
</div>

<h2 id="policies">Board of Directors' established policies</h2>
<h3>House</h3>
<p><strong>January 1990.</strong> Club members only may rent the club and that member must be present at the function. The checks for the rental and security deposit must be written and submitted by the club member, not the person they are sponsoring.</p>
<p><strong>June 1990.</strong> An event that involves decorating the club and inviting people, as opposed to a more casual event, constitutes a "party" and is subject to the rental policy.</p>
<p><strong>January 1992.</strong> No one (including construction-related parties) is to be in the club without a member present.</p>
<h3>Moorings</h3>
<p><strong>May 1989.</strong> The $10 guest fee per night for a guest mooring covers launch service, use of the club, propane and similar; the fee goes to the Club. The Club will ask renters of Club moorings for permission before assigning their mooring to a guest.</p>
<h3>Launch</h3>
<p><strong>June 1998.</strong> A "No Open Container" rule applies to all passengers of the club launch.</p>

<h2 id="about">About this interim site</h2>
<p>The club's website went offline in July 2026. The Board has approved a move to ClubExpress, a club management service used by yacht clubs across the country, and it is being purchased and deployed as the club's new website and member portal, expected to launch by early January 2027 and possibly as early as mid October 2026. In the meantime this site carries the club's essential information, drawn from the printed Welcome booklet given to new members and from archived copies of the previous website. Committee chairs are reviewing each section; if you spot something out of date, email the Webmaster, Jeff Reilly (<a href="mailto:jeffreilly@outlook.com">jeffreilly@outlook.com</a>).</p>
"""

HOME_TILES = """
  <div class="card" id="club-info">
    <div class="card-header">
      <h1>Club Information</h1>
      <div class="est">Rules, guides and how to join, while the full website is rebuilt</div>
    </div>
    <div class="card-body">
      <div class="tiles">
        <a class="tile" href="membership.html"><div class="t">Membership</div><div class="d">How to join, dues and Share Value, application form</div></a>
        <a class="tile" href="new-members.html"><div class="t">New Member Guide</div><div class="d">Getting around the clubhouse and the club year</div></a>
        <a class="tile" href="launch.html"><div class="t">Launch</div><div class="d">Hours, VHF 68, rules and etiquette</div></a>
        <a class="tile" href="clubhouse.html"><div class="t">Clubhouse</div><div class="d">Facilities, house rules, off-season rentals</div></a>
        <a class="tile" href="docks-moorings.html"><div class="t">Docks &amp; Moorings</div><div class="d">Float, dinghy and kayak storage, river and Shoals moorings</div></a>
        <a class="tile" href="sailing-school.html"><div class="t">Sailing School</div><div class="d">Programs, what to bring, scholarship</div></a>
        <a class="tile" href="social-education.html"><div class="t">Social &amp; Education</div><div class="d">The season's events, racing, member classes</div></a>
        <a class="tile" href="documents.html"><div class="t">Documents</div><div class="d">By-Laws, application, board policies</div></a>
      </div>
    </div>
  </div>
"""


def build_pages():
    page("membership.html", "Membership", "How to join the Kittery Point Yacht Club", MEMBERSHIP,
         [("join", "How to join"), ("dues", "Dues and Share"), ("application", "Application"), ("faq", "FAQ")])
    page("new-members.html", "New Member Reference Guide", "Finding your way around the club", NEW_MEMBERS,
         [("welcome", "Welcome"), ("structure", "Organization"), ("using", "Using the clubhouse"), ("season", "The club year")])
    page("launch.html", "Launch Service", "Hours, channel 68, rules and etiquette", LAUNCH,
         [("hours", "Hours"), ("rules", "Rules")])
    page("clubhouse.html", "Clubhouse", "Facilities, house rules and off-season rentals", CLUBHOUSE,
         [("facilities", "Facilities"), ("rules", "Clubhouse rules"), ("rentals", "Rentals and calendar")])
    page("docks-moorings.html", "Docks &amp; Moorings", "Float, dinghies, river and Isles of Shoals moorings", DOCKS,
         [("tieup", "Front float"), ("dinghies", "Dinghy and kayak storage"), ("moorings", "Club moorings"), ("shoals", "Isles of Shoals"), ("workdays", "Docks In and Out")])
    page("sailing-school.html", "KPYC Sailing School", "Teaching sailing on the Seacoast for over 30 years", SCHOOL,
         [("programs", "Programs"), ("know", "Need to know"), ("scholarship", "Scholarship")])
    page("social-education.html", "Social &amp; Education", "The season's events, racing and member classes", SOCIAL,
         [("upcoming", "Upcoming events"), ("social", "Social season"), ("racing", "Racing"), ("education", "Education")])
    page("documents.html", "Documents", "By-Laws, forms, rules and Board policies", DOCUMENTS,
         [("downloads", "Downloads"), ("pages", "Rules and guides"), ("policies", "Board policies"), ("about", "About this site")])


def update_index():
    p = ROOT / "index.html"
    s = p.read_text()
    nav = nav_html("index.html")
    if "<!-- nav:start -->" in s:
        s = re.sub(r"<!-- nav:start -->.*?<!-- nav:end -->", f"<!-- nav:start -->{nav}<!-- nav:end -->", s, flags=re.S)
    else:
        s = s.replace("<body>\n", f"<body>\n<!-- nav:start -->{nav}<!-- nav:end -->\n", 1)
    events_card = "  <div class=\"card\" id=\"upcoming\">\n    <div class=\"card-header\"><h1>Upcoming Club Events</h1><div class=\"est\">Announced by email until the online calendar returns</div></div>\n    <div class=\"card-body\">" + stack_tables(events_table(("club",))) + "<p style=\"margin:0.4rem 0 0;font-size:0.9rem;\"><a href=\"clubhouse.html#rentals\">Reserved clubhouse dates</a> are on the Clubhouse page.</p></div>\n  </div>\n"
    s = re.sub(r"  <div class=\"card\" id=\"upcoming\">.*?</div>\n  </div>\n", "", s, flags=re.S)
    s = s.replace("  <div class=\"card\" id=\"club-info\">", events_card + "  <div class=\"card\" id=\"club-info\">", 1)
    if 'id="club-info"' not in s:
        s = s.replace('  <div class="card contacts-card" id="contacts">', HOME_TILES + '\n  <div class="card contacts-card" id="contacts">', 1)
    # shared nav styles appended once
    extra = "\n    .card { max-width: 860px; }\n    body { padding-top: 0; justify-content: flex-start; }\n    .nav { margin-top: 0; }\n    .toc-card { top: 3.4rem; }\n    .card[id] { scroll-margin-top: 8rem; }\n    @media (max-width: 700px) { .toc-card { position: static; } .card[id] { scroll-margin-top: 4rem; } .card-body { padding: 1.4rem 1.2rem 1.6rem; } }\n"
    tstart = CSS.index("    table {"); tend = CSS.index("    .rules-box {")
    table_css = "\n" + CSS[tstart:tend].rstrip("\n") + "\n"
    block = NAV_CSS.strip("\n") + table_css + extra
    if "/* nav-css:start */" in s:
        s = re.sub(r"\n?    /\* nav-css:start \*/.*?(?=\n  </style>)", "\n" + block, s, flags=re.S)
    else:
        s = re.sub(r"\n    \.nav \{ position: sticky;.*?(?=\n  </style>)", "", s, flags=re.S)
        s = s.replace("  </style>", block + "\n  </style>", 1)
    s = re.sub(r"<script>document\.addEventListener\('DOMContentLoaded'.*?</script>\n?", "", s, flags=re.S)
    s = s.replace("</body>", NAV_SCRIPT + "\n</body>", 1)
    p.write_text(s)
    print("updated index.html")


if __name__ == "__main__":
    build_pages()
    update_index()
