#!/usr/bin/env python3
"""
Generate Yoshi contribution grid: Yoshi enters, eats commits with tongue,
exits screen, cells stay eaten, then reset with sparkle animation.
"""

import json, os, sys, urllib.request, urllib.error

USERNAME = os.environ.get("GITHUB_USER", "taylfrad")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT = os.environ.get("OUTPUT_PATH", "dist/yoshi-contrib.svg")

BG = "#050c21"
EMPTY = "#0a1628"
COLORS = ["#0a1628", "#1a3a2a", "#30A230", "#58D858", "#FFD700"]

CELL = 11
GAP = 3
STEP = CELL + GAP
GX, GY = 40, 25
DUR = 25  # total animation seconds


def fetch():
    q = '{"query":"query{user(login:\\"' + USERNAME + '\\"){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount weekday}}}}}}"}'
    req = urllib.request.Request("https://api.github.com/graphql", q.encode(),
        {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "yoshi"})
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read())
    c = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return c["weeks"], c["totalContributions"]


def level(n):
    return 0 if n == 0 else 1 if n <= 3 else 2 if n <= 6 else 3 if n <= 9 else 4


def yoshi_sprite():
    """Mario riding Yoshi, facing right. 2px per pixel."""
    p = 2
    px = [
        # Mario hat
        (8,0,5,1,"#E02020"),(7,1,7,1,"#E02020"),(6,2,8,1,"#E02020"),
        # Mario hair/face
        (6,3,2,1,"#804020"),(5,4,2,1,"#804020"),
        (8,3,4,1,"#E8A030"),(7,4,5,1,"#E8A030"),(12,3,2,1,"#E8A030"),(12,4,2,1,"#E8A030"),
        (11,3,1,1,"#000"),(10,5,4,1,"#000"),(8,5,2,1,"#E8A030"),
        # Cape
        (4,5,3,3,"#0058F8"),(3,6,2,2,"#0058F8"),
        # Shirt
        (7,5,3,1,"#E02020"),(6,6,5,2,"#E02020"),(5,7,2,1,"#E02020"),
        (5,6,1,1,"#E8A030"),(11,6,2,1,"#E8A030"),
        (5,8,2,2,"#E02020"),(11,8,2,2,"#E02020"),
        # Yoshi head
        (12,7,4,1,"#30A230"),(11,8,6,1,"#30A230"),(11,9,7,1,"#30A230"),(12,10,6,1,"#30A230"),
        (17,8,2,1,"#30A230"),(17,9,3,1,"#30A230"),(18,10,2,1,"#30A230"),
        (14,7,2,2,"#fff"),(15,8,1,1,"#000"),
        (13,11,6,1,"#30A230"),(17,11,2,1,"#fff"),
        (12,6,2,1,"#E84030"),(13,5,1,1,"#E84030"),
        # Saddle
        (7,8,4,1,"#E84030"),(6,9,6,1,"#E84030"),
        # Body
        (7,9,4,1,"#30A230"),(6,10,6,2,"#30A230"),(7,12,5,1,"#30A230"),
        (8,11,3,1,"#fff"),(8,12,3,1,"#fff"),
        (5,11,2,1,"#30A230"),(4,12,2,1,"#30A230"),
        # Legs
        (6,13,3,2,"#30A230"),(10,13,3,2,"#30A230"),
        (5,15,4,1,"#E87020"),(10,15,4,1,"#E87020"),
    ]
    return "\n    ".join(
        f'<rect x="{x*p}" y="{y*p}" width="{w*p}" height="{h*p}" fill="{c}"/>'
        for x, y, w, h, c in px
    )


def generate(weeks, total):
    nw = len(weeks)
    gw = nw * STEP
    sw = gw + GX + 20
    sh = 7 * STEP + GY + 45

    sprite = yoshi_sprite()

    # Phase percentages
    enter_end = 4       # Yoshi fully on screen
    traverse_end = 72   # Yoshi reaches far right
    exit_end = 78       # Yoshi off screen right
    pause_end = 84      # cells stay eaten
    reset_end = 96      # cells have reset
    # 96-100: brief pause before loop

    cells = []
    for wi, wk in enumerate(weeks):
        for di, day in enumerate(wk["contributionDays"]):
            lv = level(day["contributionCount"])
            color = COLORS[lv]
            x = GX + wi * STEP
            y = GY + day["weekday"] * STEP

            if lv == 0:
                cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{EMPTY}"/>')
                continue

            # When does Yoshi eat this cell? Map column to enter_end..traverse_end
            col_pct = wi / max(nw - 1, 1)
            eat_pct = enter_end + col_pct * (traverse_end - enter_end)

            # When does this cell reset? Map column to pause_end..reset_end
            reset_pct = pause_end + col_pct * (reset_end - pause_end)

            # Cell animation: visible -> eaten (pop+vanish) -> stays gone -> reset (pop back in)
            eat1 = f"{eat_pct:.1f}"
            eat2 = f"{eat_pct + 1:.1f}"
            eat3 = f"{eat_pct + 1.5:.1f}"
            rst1 = f"{reset_pct:.1f}"
            rst2 = f"{reset_pct + 1.5:.1f}"
            rst3 = f"{reset_pct + 2:.1f}"

            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}">'
                f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" '
                f'keyTimes="0;{float(eat1)/100:.4f};{float(eat2)/100:.4f};{float(eat3)/100:.4f};{float(rst1)/100:.4f};{float(rst2)/100:.4f};{float(rst3)/100:.4f};1" '
                f'values="1;1;0.8;0;0;0.5;1;1"/>'
                f'<animate attributeName="rx" dur="{DUR}s" repeatCount="indefinite" '
                f'keyTimes="0;{float(eat1)/100:.4f};{float(eat2)/100:.4f};{float(eat3)/100:.4f};{float(rst1)/100:.4f};{float(rst2)/100:.4f};{float(rst3)/100:.4f};1" '
                f'values="2;2;6;6;6;4;2;2"/>'
                f'</rect>'
            )

    cells_svg = "\n    ".join(cells)

    # Day labels
    days = ["Mon", "", "Wed", "", "Fri", "", ""]
    labels = "\n    ".join(
        f'<text x="{GX-5}" y="{GY + i*STEP + CELL-1}" font-family="monospace" font-size="6" fill="#6B7280" text-anchor="end">{d}</text>'
        for i, d in enumerate(days) if d
    )

    # Yoshi vertical position
    yy = GY + 2 * STEP - 16

    # Tongue: extends ~30px ahead of Yoshi to "grab" cells
    tongue_dur = 0.6

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sw} {sh}" width="{sw}" height="{sh}">
  <style>
    @keyframes yoshi-go {{
      0% {{ transform: translateX(-60px); }}
      {enter_end}% {{ transform: translateX(0px); }}
      {traverse_end}% {{ transform: translateX({gw}px); }}
      {exit_end}% {{ transform: translateX({gw + 80}px); }}
      {exit_end + 0.1}% {{ transform: translateX(-60px); }}
      100% {{ transform: translateX(-60px); }}
    }}
    @keyframes bob {{
      0%,100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-2px); }}
    }}
    @keyframes flutter {{
      0%,100% {{ transform: rotate(0deg); }}
      25% {{ transform: rotate(-3deg); }}
      75% {{ transform: rotate(3deg); }}
    }}
    @keyframes tongue-shoot {{
      0%,60% {{ width: 0; }}
      70% {{ width: 25px; }}
      85% {{ width: 25px; }}
      100% {{ width: 0; }}
    }}
    @keyframes tongue-tip {{
      0%,60% {{ r: 0; cx: 38px; }}
      70% {{ r: 3px; cx: 63px; }}
      85% {{ r: 3px; cx: 63px; }}
      100% {{ r: 0; cx: 38px; }}
    }}
    /* Reset sparkle on cells */
    @keyframes sparkle {{
      0%,{pause_end}% {{ opacity: 0; }}
      {pause_end + 1}% {{ opacity: 1; }}
      {reset_end - 2}% {{ opacity: 1; }}
      {reset_end}%,100% {{ opacity: 0; }}
    }}
    .yoshi {{ animation: yoshi-go {DUR}s linear infinite; }}
    .yoshi-bob {{ animation: bob 0.3s ease-in-out infinite; }}
    .yoshi-flutter {{ animation: flutter 0.2s ease-in-out infinite; }}
  </style>

  <rect width="{sw}" height="{sh}" fill="{BG}" rx="6"/>

  <!-- Title -->
  <text x="{sw//2}" y="{GY-8}" font-family="'Press Start 2P',monospace" font-size="7" fill="#30A230" text-anchor="middle" opacity=".7">{total} contributions</text>

  <!-- Day labels -->
  {labels}

  <!-- Grid -->
  <g>{cells_svg}</g>

  <!-- Reset sparkle overlay -->
  <g style="animation:sparkle {DUR}s linear infinite">
    <text x="{GX + gw//4}" y="{GY + 3*STEP}" font-size="10" fill="#FFD700" opacity="0">
      <animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite"
        keyTimes="0;{pause_end/100:.2f};{(pause_end+2)/100:.2f};{(reset_end-2)/100:.2f};{reset_end/100:.2f};1"
        values="0;0;0.8;0.8;0;0"/>
      ✦ ✦ ✦
    </text>
    <text x="{GX + gw//2}" y="{GY + 5*STEP}" font-size="8" fill="#FFD700" opacity="0">
      <animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite"
        keyTimes="0;{(pause_end+1)/100:.2f};{(pause_end+3)/100:.2f};{(reset_end-3)/100:.2f};{(reset_end-1)/100:.2f};1"
        values="0;0;0.6;0.6;0;0"/>
      ✦ ✦
    </text>
    <text x="{GX + 3*gw//4}" y="{GY + 2*STEP}" font-size="10" fill="#FFD700" opacity="0">
      <animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite"
        keyTimes="0;{(pause_end+2)/100:.2f};{(pause_end+4)/100:.2f};{(reset_end-4)/100:.2f};{(reset_end-2)/100:.2f};1"
        values="0;0;0.7;0.7;0;0"/>
      ✦ ✦ ✦
    </text>
  </g>

  <!-- Yoshi -->
  <g class="yoshi" transform="translate({GX},{yy})">
    <g class="yoshi-bob">
      <g class="yoshi-flutter">
        <!-- Tongue -->
        <rect x="38" y="20" width="0" height="4" fill="#E84030" rx="2">
          <animate attributeName="width" dur="{tongue_dur}s" repeatCount="indefinite"
            values="0;25;25;0" keyTimes="0;0.3;0.7;1"/>
        </rect>
        <circle cx="38" cy="22" r="0" fill="#E84030">
          <animate attributeName="cx" dur="{tongue_dur}s" repeatCount="indefinite"
            values="38;63;63;38" keyTimes="0;0.3;0.7;1"/>
          <animate attributeName="r" dur="{tongue_dur}s" repeatCount="indefinite"
            values="0;3;3;0" keyTimes="0;0.3;0.7;1"/>
        </circle>
        <!-- Sprite -->
        {sprite}
      </g>
    </g>
  </g>
</svg>'''
    return svg


def main():
    print(f"Fetching contributions for {USERNAME}...")
    weeks, total = fetch()
    print(f"Found {total} contributions, {len(weeks)} weeks")
    svg = generate(weeks, total)
    os.makedirs(os.path.dirname(OUTPUT) or ".", exist_ok=True)
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
