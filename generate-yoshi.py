#!/usr/bin/env python3
"""
Yoshi contribution grid — snake-style traversal.
Standalone Yoshi zigzags row by row eating commits.
Row 0: left→right, Row 1: right→left, etc.
Tongue only extends when eating (during traverse phase).
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
DUR = 60          # slower pace — 60s full cycle
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


YOSHI_B64 = "iVBORw0KGgoAAAANSUhEUgAAACgAAAAtCAYAAADcMyneAAACRElEQVR4nO1ZvUoDQRCekSA+gIWCmHRnnRQnWqUUJIIgPoA+gGJtJdiJvoCFjYVW5g1sRIsUgoUphFMERbQwCIIWI3t7P7t7t5eNudUk+sHlZnbndr/MzM7eJgD/6A4IdkHdzjUE9oiRSwBja/xSyP46wZ4GucSvsbXvec02iBFLITeYIcacxiGDcUloN7HP7ugA5NVipVTPHNcnxla3iAvZWtIKYAFL5PgUjrEZTTa77dDbYlOyO4Jr//5+DbAMU758yW92Cd6BTITh5qkJRUdum4SgwQEY+ckcdAPtdj1uK+7qH2YhJuIPIaLEK9ccLNX5rpFFxgRCTmLPl5mh35j0Vgh9O+SxSLBUN9slzgMz3OMxNEmFvxVirwbwuJfniJbqoC68QQnpKD9zJTh/KusH0JD0RiPWp+cqMDzB5fENgIcdLr8ccrtWqwXVajVfglevsu5AWdLL5Vj/fAL4uI/7Qpm1VyqVyNUFG4U6DSy84W7BwOQw5EreotWtziVt3jFBV46wb8tMwfComPbNE31heKOCrGz834mYloCYIyszAJujcV/xJO4jwY6FNySnIdgx+ivELiVevyNsPcfy5kK60bmFU6Y6E4kvjspLpGqYsEsM/udCrEOah0SvorBgbINEhD8CZV1eLbO/a+gO2FL5YPK0YhouJk85E3dwRh6MHEQTD7aDJ3hNRB4eNCLIdhId9s+SRANiWXMMdplB/wPRaBWS4GnFc9FYeRMUB29LcnXWyvtl/4QY2/RTj/2t8Y/Bwxfj/dtkNWGQuwAAAABJRU5ErkJggg=="


def yoshi_sprite():
    """SMW Yoshi facing right — embedded PNG sprite for pixel-perfect accuracy."""
    return f'<image width="40" height="45" style="image-rendering:pixelated" href="data:image/png;base64,{YOSHI_B64}" />'


def generate(weeks, total):
    nw = len(weeks)
    gw = nw * STEP
    sw = gw + GX + 20
    sh = NUM_ROWS * STEP + GY + 50
    sprite = yoshi_sprite()
    sprite_w, sprite_h = 40, 45

    # Animation phase percentages
    traverse_pct = 75   # 0-75%: zigzag traverse (eating)
    exit_pct = 80       # 75-80%: exit screen
    pause_pct = 85      # 80-85%: pause off-screen
    reset_pct = 95      # 85-95%: cells reset with sparkle
    # 95-100%: wait before next loop

    row_pct = traverse_pct / NUM_ROWS

    # Generate Yoshi path keyframes (snake-style zigzag)
    kf_lines = []
    for r in range(NUM_ROWS):
        row_start = r * row_pct
        row_end = (r + 1) * row_pct
        ry = r * STEP
        left_to_right = (r % 2 == 0)

        if left_to_right:
            kf_lines.append(f"  {row_start:.2f}% {{ transform: translate({-sprite_w}px, {ry}px) scaleX(1); }}")
            kf_lines.append(f"  {row_start + 0.5:.2f}% {{ transform: translate(0px, {ry}px) scaleX(1); }}")
            kf_lines.append(f"  {row_end - 0.5:.2f}% {{ transform: translate({gw}px, {ry}px) scaleX(1); }}")
        else:
            kf_lines.append(f"  {row_start:.2f}% {{ transform: translate({gw}px, {ry}px) scaleX(-1); }}")
            kf_lines.append(f"  {row_start + 0.5:.2f}% {{ transform: translate({gw}px, {ry}px) scaleX(-1); }}")
            kf_lines.append(f"  {row_end - 0.5:.2f}% {{ transform: translate(0px, {ry}px) scaleX(-1); }}")

    last_row_y = (NUM_ROWS - 1) * STEP
    kf_lines.append(f"  {traverse_pct:.2f}% {{ transform: translate({gw + 60}px, {last_row_y}px) scaleX(1); }}")
    kf_lines.append(f"  {exit_pct:.2f}% {{ transform: translate({gw + 60}px, {last_row_y}px) scaleX(1); }}")
    kf_lines.append(f"  {exit_pct + 0.1:.2f}% {{ transform: translate({-sprite_w - 20}px, 0px) scaleX(1); }}")
    kf_lines.append(f"  100% {{ transform: translate({-sprite_w - 20}px, 0px) scaleX(1); }}")

    yoshi_kf = "@keyframes yoshi-path {\n" + "\n".join(kf_lines) + "\n    }"

    tongue_dur = 0.7  # quick flick

    # Generate cell animations
    cells = []
    for wi, wk in enumerate(weeks):
        for di, day in enumerate(wk["contributionDays"]):
            lv = level(day["contributionCount"])
            color = COLORS[lv]
            x = GX + wi * STEP
            y = GY + day["weekday"] * STEP
            r = day["weekday"]

            if lv == 0:
                cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{EMPTY}"/>')
                continue

            left_to_right = (r % 2 == 0)
            row_start_pct = r * row_pct
            if left_to_right:
                col_progress = wi / max(nw - 1, 1)
            else:
                col_progress = (nw - 1 - wi) / max(nw - 1, 1)

            eat_pct = row_start_pct + 0.5 + col_progress * (row_pct - 1.0)

            reset_start = pause_pct
            reset_span = reset_pct - pause_pct
            total_cells_before = r * nw + (wi if left_to_right else (nw - 1 - wi))
            total_cells = NUM_ROWS * nw
            reset_progress = total_cells_before / max(total_cells - 1, 1)
            rst_pct = reset_start + reset_progress * reset_span

            e1 = eat_pct / 100
            e2 = min((eat_pct + 0.15) / 100, 0.99)
            r1 = rst_pct / 100
            r2 = min((rst_pct + 0.15) / 100, 0.99)

            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}">'
                f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" '
                f'keyTimes="0;{e1:.4f};{e2:.4f};{r1:.4f};{r2:.4f};1" '
                f'values="1;1;0;0;1;1"/>'
                f'</rect>'
            )

    cells_svg = "\n    ".join(cells)

    days = ["Mon", "", "Wed", "", "Fri", "", ""]
    labels = "\n    ".join(
        f'<text x="{GX-5}" y="{GY + i*STEP + CELL-1}" font-family="monospace" font-size="9" fill="#8B9AB0" text-anchor="end">{d}</text>'
        for i, d in enumerate(days) if d
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sw} {sh}" width="{sw}" height="{sh}">
  <style>
    {yoshi_kf}
    @keyframes bob {{
      0%,100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-2px); }}
    }}
    @keyframes tongue-visible {{
      0% {{ opacity: 1; }}
      {traverse_pct - 0.5}% {{ opacity: 1; }}
      {traverse_pct}% {{ opacity: 0; }}
      100% {{ opacity: 0; }}
    }}
    @keyframes sparkle-in {{
      0%,{pause_pct}% {{ opacity: 0; }}
      {pause_pct+2}% {{ opacity: 0.8; }}
      {reset_pct-2}% {{ opacity: 0.8; }}
      {reset_pct}%,100% {{ opacity: 0; }}
    }}
    .yoshi {{ animation: yoshi-path {DUR}s linear infinite; }}
    .yoshi-bob {{ animation: bob 0.35s ease-in-out infinite; }}
    .tongue-wrap {{ animation: tongue-visible {DUR}s linear infinite; }}
  </style>

  <rect width="{sw}" height="{sh}" fill="{BG}"/>

  <!-- Title -->
  <text x="{sw//2}" y="{GY-8}" font-family="'Press Start 2P',monospace" font-size="11" fill="#30A230" text-anchor="middle" opacity=".8">{total} contributions</text>

  {labels}

  <!-- Grid -->
  <g>{cells_svg}</g>

  <!-- Reset sparkles -->
  <g style="animation:sparkle-in {DUR}s linear infinite">
    <text x="{GX + gw//4}" y="{GY + 2*STEP}" font-size="10" fill="#FFD700" opacity="0" style="animation:sparkle-in {DUR}s linear infinite">&#x2726;</text>
    <text x="{GX + gw//2}" y="{GY + 5*STEP}" font-size="8" fill="#FFD700" opacity="0" style="animation:sparkle-in {DUR}s linear infinite;animation-delay:0.5s">&#x2726;</text>
    <text x="{GX + 3*gw//4}" y="{GY + 3*STEP}" font-size="10" fill="#FFD700" opacity="0" style="animation:sparkle-in {DUR}s linear infinite;animation-delay:1s">&#x2726;</text>
  </g>

  <!-- Yoshi -->
  <g class="yoshi" transform="translate({GX},{GY - 6})" style="transform-origin:{GX + sprite_w//2}px {GY + sprite_h//2}px">
    <g class="yoshi-bob">
      <!-- Tongue — only visible during traverse (eating) phase -->
      <g class="tongue-wrap">
        <rect x="32" y="13" width="0" height="3" fill="#E84030" rx="1">
          <animate attributeName="width" dur="{tongue_dur}s" repeatCount="indefinite"
            values="0;20;20;0" keyTimes="0;0.3;0.7;1"/>
        </rect>
        <circle cx="32" cy="14" r="0" fill="#E84030">
          <animate attributeName="cx" dur="{tongue_dur}s" repeatCount="indefinite"
            values="32;52;52;32" keyTimes="0;0.3;0.7;1"/>
          <animate attributeName="r" dur="{tongue_dur}s" repeatCount="indefinite"
            values="0;2;2;0" keyTimes="0;0.3;0.7;1"/>
        </circle>
      </g>
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
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
