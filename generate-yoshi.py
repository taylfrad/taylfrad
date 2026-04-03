#!/usr/bin/env python3
"""
Yoshi contribution grid — snake-style traversal.
Standalone Yoshi (no Mario) zigzags row by row eating commits one at a time.
Row 0: left→right, Row 1: right→left, etc.
After eating all, Yoshi exits, cells reset with sparkle, loop.
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
DUR = 30
NUM_ROWS = 7


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
    """Standalone Yoshi facing right — Yoshi's Island style. 2px per pixel."""
    p = 2
    px = [
        # Head crest (red spines on top)
        (9,0,1,1,"#E84030"),(10,0,2,1,"#E84030"),
        (8,1,1,1,"#E84030"),(9,1,1,1,"#30A230"),
        # Head dome (green)
        (7,2,5,1,"#30A230"),(6,3,7,1,"#30A230"),(5,4,8,1,"#30A230"),
        (5,5,8,1,"#30A230"),(5,6,7,1,"#30A230"),
        # Snout/nose (extends right)
        (12,3,3,1,"#30A230"),(13,4,3,1,"#30A230"),(13,5,3,1,"#30A230"),
        (12,6,3,1,"#30A230"),
        # Eye (large white with pupil)
        (9,3,3,2,"#fff"),
        (11,3,1,2,"#000"),
        # Cheek/mouth (white jaw)
        (8,7,4,1,"#fff"),(12,7,3,1,"#fff"),
        # Nose tip
        (15,4,1,2,"#30A230"),
        # Body
        (5,8,2,1,"#30A230"),(4,9,4,1,"#30A230"),(3,10,6,1,"#30A230"),
        (3,11,6,1,"#30A230"),(4,12,5,1,"#30A230"),
        # Saddle (red on back)
        (7,8,3,1,"#E84030"),(7,9,4,1,"#E84030"),(8,10,3,1,"#E84030"),
        # Belly (white)
        (4,10,4,1,"#fff"),(4,11,4,1,"#fff"),(5,12,3,1,"#fff"),
        # Arms
        (3,9,1,1,"#30A230"),(10,9,2,1,"#30A230"),
        (2,10,1,2,"#30A230"),(10,10,2,1,"#30A230"),
        # Tail
        (2,12,2,1,"#30A230"),(1,13,2,1,"#30A230"),
        # Legs
        (4,13,3,2,"#30A230"),(8,13,3,2,"#30A230"),
        # Boots (orange with dark sole)
        (3,15,4,1,"#E87020"),(3,16,4,1,"#C04010"),
        (8,15,4,1,"#E87020"),(8,16,4,1,"#C04010"),
    ]
    return "\n      ".join(
        f'<rect x="{x*p}" y="{y*p}" width="{w*p}" height="{h*p}" fill="{c}"/>'
        for x, y, w, h, c in px
    )


def generate(weeks, total):
    nw = len(weeks)
    gw = nw * STEP
    sw = gw + GX + 20
    sh = NUM_ROWS * STEP + GY + 50
    sprite = yoshi_sprite()
    sprite_w, sprite_h = 34, 34

    # Animation phase percentages
    traverse_pct = 75  # 0-75%: zigzag traverse
    exit_pct = 80      # 75-80%: exit
    pause_pct = 85     # 80-85%: pause
    reset_pct = 95     # 85-95%: reset
    # 95-100%: wait

    row_pct = traverse_pct / NUM_ROWS  # ~10.7% per row

    # Generate Yoshi path keyframes (zigzag)
    kf_lines = []
    for r in range(NUM_ROWS):
        row_start = r * row_pct
        row_end = (r + 1) * row_pct
        ry = r * STEP  # Y offset for this row
        left_to_right = (r % 2 == 0)

        if left_to_right:
            # Enter from left, exit right
            sx = -1 if r == 0 else 1  # scaleX for direction
            kf_lines.append(f"  {row_start:.2f}% {{ transform: translate({-sprite_w}px, {ry}px) scaleX(1); }}")
            kf_lines.append(f"  {row_start + 0.5:.2f}% {{ transform: translate(0px, {ry}px) scaleX(1); }}")
            kf_lines.append(f"  {row_end - 0.5:.2f}% {{ transform: translate({gw}px, {ry}px) scaleX(1); }}")
        else:
            # Enter from right, exit left
            kf_lines.append(f"  {row_start:.2f}% {{ transform: translate({gw}px, {ry}px) scaleX(-1); }}")
            kf_lines.append(f"  {row_start + 0.5:.2f}% {{ transform: translate({gw}px, {ry}px) scaleX(-1); }}")
            kf_lines.append(f"  {row_end - 0.5:.2f}% {{ transform: translate(0px, {ry}px) scaleX(-1); }}")

    # Exit off screen
    kf_lines.append(f"  {traverse_pct:.2f}% {{ transform: translate({gw + 60}px, {(NUM_ROWS-1) * STEP}px) scaleX(1); }}")
    kf_lines.append(f"  {exit_pct:.2f}% {{ transform: translate({gw + 60}px, {(NUM_ROWS-1) * STEP}px) scaleX(1); }}")
    # Teleport back
    kf_lines.append(f"  {exit_pct + 0.1:.2f}% {{ transform: translate({-sprite_w - 20}px, 0px) scaleX(1); }}")
    kf_lines.append(f"  100% {{ transform: translate({-sprite_w - 20}px, 0px) scaleX(1); }}")

    yoshi_kf = "@keyframes yoshi-path {\n" + "\n".join(kf_lines) + "\n    }"

    # Generate cell animations
    cells = []
    for wi, wk in enumerate(weeks):
        for di, day in enumerate(wk["contributionDays"]):
            lv = level(day["contributionCount"])
            color = COLORS[lv]
            x = GX + wi * STEP
            y = GY + day["weekday"] * STEP
            r = day["weekday"]  # row

            if lv == 0:
                cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{EMPTY}"/>')
                continue

            # Calculate eat time: when does Yoshi reach this cell?
            left_to_right = (r % 2 == 0)
            row_start_pct = r * row_pct
            if left_to_right:
                col_progress = wi / max(nw - 1, 1)
            else:
                col_progress = (nw - 1 - wi) / max(nw - 1, 1)

            eat_pct = row_start_pct + 0.5 + col_progress * (row_pct - 1.0)

            # Reset time
            reset_start = pause_pct
            reset_span = reset_pct - pause_pct
            # Reset in same order as eating
            total_cells_before = r * nw + (wi if left_to_right else (nw - 1 - wi))
            total_cells = NUM_ROWS * nw
            reset_progress = total_cells_before / max(total_cells - 1, 1)
            rst_pct = reset_start + reset_progress * reset_span

            # SMIL animation values
            e1 = eat_pct / 100
            e2 = (eat_pct + 0.8) / 100
            e3 = (eat_pct + 1.2) / 100
            r1 = rst_pct / 100
            r2 = (rst_pct + 0.8) / 100
            r3 = min((rst_pct + 1.2) / 100, 0.99)

            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}">'
                f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" '
                f'keyTimes="0;{e1:.4f};{e2:.4f};{e3:.4f};{r1:.4f};{r2:.4f};{r3:.4f};1" '
                f'values="1;1;0.5;0;0;0.5;1;1"/>'
                f'</rect>'
            )

    cells_svg = "\n    ".join(cells)

    # Day labels
    days = ["Mon", "", "Wed", "", "Fri", "", ""]
    labels = "\n    ".join(
        f'<text x="{GX-5}" y="{GY + i*STEP + CELL-1}" font-family="monospace" font-size="6" fill="#6B7280" text-anchor="end">{d}</text>'
        for i, d in enumerate(days) if d
    )

    # Tongue animation
    tongue_dur = 0.5

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sw} {sh}" width="{sw}" height="{sh}">
  <style>
    {yoshi_kf}
    @keyframes bob {{
      0%,100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-1px); }}
    }}
    @keyframes sparkle-in {{
      0%,{pause_pct}% {{ opacity: 0; }}
      {pause_pct+2}% {{ opacity: 0.8; }}
      {reset_pct-2}% {{ opacity: 0.8; }}
      {reset_pct}%,100% {{ opacity: 0; }}
    }}
    .yoshi {{ animation: yoshi-path {DUR}s linear infinite; }}
    .yoshi-bob {{ animation: bob 0.25s ease-in-out infinite; }}
  </style>

  <rect width="{sw}" height="{sh}" fill="{BG}" rx="6"/>

  <!-- Title -->
  <text x="{sw//2}" y="{GY-8}" font-family="'Press Start 2P',monospace" font-size="7" fill="#30A230" text-anchor="middle" opacity=".7">{total} contributions</text>

  {labels}

  <!-- Grid -->
  <g>{cells_svg}</g>

  <!-- Reset sparkles -->
  <g style="animation:sparkle-in {DUR}s linear infinite">
    <text x="{GX + gw//4}" y="{GY + 2*STEP}" font-size="10" fill="#FFD700" opacity="0" style="animation:sparkle-in {DUR}s linear infinite">✦</text>
    <text x="{GX + gw//2}" y="{GY + 5*STEP}" font-size="8" fill="#FFD700" opacity="0" style="animation:sparkle-in {DUR}s linear infinite;animation-delay:0.5s">✦</text>
    <text x="{GX + 3*gw//4}" y="{GY + 3*STEP}" font-size="10" fill="#FFD700" opacity="0" style="animation:sparkle-in {DUR}s linear infinite;animation-delay:1s">✦</text>
  </g>

  <!-- Yoshi -->
  <g class="yoshi" transform="translate({GX},{GY - 4})" style="transform-origin:{GX + sprite_w//2}px {GY + sprite_h//2}px">
    <g class="yoshi-bob">
      <!-- Tongue -->
      <rect x="30" y="14" width="0" height="3" fill="#E84030" rx="1">
        <animate attributeName="width" dur="{tongue_dur}s" repeatCount="indefinite"
          values="0;20;20;0" keyTimes="0;0.25;0.65;1"/>
      </rect>
      <circle cx="30" cy="16" r="0" fill="#E84030">
        <animate attributeName="cx" dur="{tongue_dur}s" repeatCount="indefinite"
          values="30;50;50;30" keyTimes="0;0.25;0.65;1"/>
        <animate attributeName="r" dur="{tongue_dur}s" repeatCount="indefinite"
          values="0;2.5;2.5;0" keyTimes="0;0.25;0.65;1"/>
      </circle>
      <!-- Sprite -->
      {sprite}
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
