#!/usr/bin/env python3
"""
Generate a Mario/Yoshi-themed contribution grid SVG.
Mario rides Yoshi across the contribution grid. Yoshi's tongue
extends to eat each contribution cell.
"""

import json
import os
import sys
import urllib.request
import urllib.error

USERNAME = os.environ.get("GITHUB_USER", "taylfrad")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT = os.environ.get("OUTPUT_PATH", "dist/yoshi-contrib.svg")

BG_COLOR = "#050c21"
EMPTY_COLOR = "#0a1628"
LEVEL_COLORS = ["#0a1628", "#1a3a2a", "#30A230", "#58D858", "#FFD700"]

CELL_SIZE = 11
CELL_GAP = 3
CELL_TOTAL = CELL_SIZE + CELL_GAP
GRID_X = 40
GRID_Y = 25
ANIM_DURATION = 20


def fetch_contributions():
    query = """
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                weekday
              }
            }
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"username": USERNAME}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "yoshi-contrib-generator",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print(f"Error fetching contributions: {e}", file=sys.stderr)
        sys.exit(1)

    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["weeks"], cal["totalContributions"]


def contribution_level(count):
    if count == 0:
        return 0
    elif count <= 3:
        return 1
    elif count <= 6:
        return 2
    elif count <= 9:
        return 3
    else:
        return 4


def build_mario_yoshi_sprite():
    """
    Build pixel art of Mario riding Yoshi (facing right).
    Based on Super Mario World SNES sprite.
    Grid: ~20 wide x 22 tall, 2px per pixel = 40x44 SVG units.
    """
    p = 2
    pixels = [
        # === MARIO (on top) ===
        # Hat
        (8, 0, 5, 1, "#E02020"),
        (7, 1, 7, 1, "#E02020"),
        (6, 2, 8, 1, "#E02020"),
        # Hair
        (6, 3, 2, 1, "#804020"),
        (5, 4, 2, 1, "#804020"),
        # Face (golden skin)
        (8, 3, 4, 1, "#E8A030"),
        (7, 4, 5, 1, "#E8A030"),
        (12, 3, 2, 1, "#E8A030"),
        (12, 4, 2, 1, "#E8A030"),
        # Eye
        (11, 3, 1, 1, "#000"),
        # Mustache
        (10, 5, 4, 1, "#000"),
        (8, 5, 2, 1, "#E8A030"),
        # Cape (blue, behind)
        (4, 5, 3, 3, "#0058F8"),
        (3, 6, 2, 2, "#0058F8"),
        # Shirt/body (red)
        (7, 5, 3, 1, "#E02020"),
        (6, 6, 5, 2, "#E02020"),
        (5, 7, 2, 1, "#E02020"),
        # Arms (skin)
        (5, 6, 1, 1, "#E8A030"),
        (11, 6, 2, 1, "#E8A030"),
        # Mario's boots on Yoshi's sides
        (5, 8, 2, 2, "#E02020"),
        (11, 8, 2, 2, "#E02020"),

        # === YOSHI (bottom) ===
        # Head — round green dome extending forward
        (12, 7, 4, 1, "#30A230"),
        (11, 8, 6, 1, "#30A230"),
        (11, 9, 7, 1, "#30A230"),
        (12, 10, 6, 1, "#30A230"),
        # Snout/nose (extends right)
        (17, 8, 2, 1, "#30A230"),
        (17, 9, 3, 1, "#30A230"),
        (18, 10, 2, 1, "#30A230"),
        # Eye (white + pupil)
        (14, 7, 2, 2, "#fff"),
        (15, 8, 1, 1, "#000"),
        # Mouth line
        (13, 11, 6, 1, "#30A230"),
        (17, 11, 2, 1, "#fff"),  # lower jaw white
        # Red crest on head
        (12, 6, 2, 1, "#E84030"),
        (13, 5, 1, 1, "#E84030"),

        # Saddle (red, where Mario sits)
        (7, 8, 4, 1, "#E84030"),
        (6, 9, 6, 1, "#E84030"),

        # Body (green)
        (7, 9, 4, 1, "#30A230"),
        (6, 10, 6, 2, "#30A230"),
        (7, 12, 5, 1, "#30A230"),

        # Belly (white)
        (8, 11, 3, 1, "#fff"),
        (8, 12, 3, 1, "#fff"),

        # Tail
        (5, 11, 2, 1, "#30A230"),
        (4, 12, 2, 1, "#30A230"),

        # Legs/boots (green with orange shoes)
        (6, 13, 3, 2, "#30A230"),
        (10, 13, 3, 2, "#30A230"),
        (5, 15, 4, 1, "#E87020"),  # left boot
        (10, 15, 4, 1, "#E87020"),  # right boot
    ]

    rects = []
    for x, y, w, h, color in pixels:
        rects.append(
            f'<rect x="{x * p}" y="{y * p}" width="{w * p}" height="{h * p}" fill="{color}"/>'
        )

    # Tongue — extends from mouth, animated separately
    tongue = (
        f'<g class="yoshi-tongue" transform-origin="{19 * p}px {11 * p}px">'
        f'<rect x="{19 * p}" y="{10 * p}" width="0" height="{2 * p}" fill="#E84030" rx="1">'
        f'<animate attributeName="width" values="0;30;30;0" keyTimes="0;0.3;0.6;1" dur="0.8s" repeatCount="indefinite"/>'
        f'</rect>'
        f'<circle cx="{19 * p}" cy="{11 * p}" r="0" fill="#E84030">'
        f'<animate attributeName="cx" values="{19 * p};{19 * p + 30};{19 * p + 30};{19 * p}" keyTimes="0;0.3;0.6;1" dur="0.8s" repeatCount="indefinite"/>'
        f'<animate attributeName="r" values="0;3;3;0" keyTimes="0;0.3;0.6;1" dur="0.8s" repeatCount="indefinite"/>'
        f'</circle>'
        f'</g>'
    )

    return "\n      ".join(rects) + "\n      " + tongue


def generate_svg(weeks, total):
    num_weeks = len(weeks)
    max_days = 7

    grid_width = num_weeks * CELL_TOTAL
    svg_width = grid_width + GRID_X + 20
    svg_height = max_days * CELL_TOTAL + GRID_Y + 45

    sprite_svg = build_mario_yoshi_sprite()
    sprite_height = 34  # approximate SVG units
    sprite_width = 42

    # Build grid cells
    cells = []
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week["contributionDays"]):
            level = contribution_level(day["contributionCount"])
            color = LEVEL_COLORS[level]
            x = GRID_X + wi * CELL_TOTAL
            y = GRID_Y + day["weekday"] * CELL_TOTAL

            col_pct = wi / max(num_weeks - 1, 1)
            # Yoshi reaches this column at this percentage of the animation
            eat_delay = col_pct * 0.75 + 0.05  # 5% to 80% of duration

            if level > 0:
                cells.append(
                    f'<rect x="{x}" y="{y}" '
                    f'width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" '
                    f'fill="{color}" class="cell" '
                    f'style="animation-delay:{eat_delay * ANIM_DURATION:.2f}s"/>'
                )
            else:
                cells.append(
                    f'<rect x="{x}" y="{y}" '
                    f'width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" '
                    f'fill="{EMPTY_COLOR}"/>'
                )

    cells_svg = "\n    ".join(cells)

    # Day labels
    day_labels = ["Mon", "", "Wed", "", "Fri", "", ""]
    labels_svg = ""
    for i, label in enumerate(day_labels):
        if label:
            ly = GRID_Y + i * CELL_TOTAL + CELL_SIZE - 1
            labels_svg += (
                f'<text x="{GRID_X - 5}" y="{ly}" '
                f'font-family="\'Press Start 2P\',monospace" font-size="6" '
                f'fill="#6B7280" text-anchor="end">{label}</text>\n    '
            )

    # Yoshi vertical position — centered on the grid
    yoshi_y = GRID_Y + 2 * CELL_TOTAL - sprite_height // 2

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <style>
    @keyframes yoshi-run {{
      0% {{ transform: translateX(-{sprite_width + 20}px); }}
      5% {{ transform: translateX(0px); }}
      80% {{ transform: translateX({grid_width}px); }}
      85%,100% {{ transform: translateX({grid_width + 40}px); }}
    }}
    @keyframes eat {{
      0% {{ transform: scale(1); opacity: 1; }}
      70% {{ transform: scale(1); opacity: 1; }}
      85% {{ transform: scale(1.4); opacity: 0.6; }}
      100% {{ transform: scale(0); opacity: 0; }}
    }}
    @keyframes bob {{
      0%,100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-2px); }}
    }}
    @keyframes legs {{
      0%,40% {{ transform: translateY(0); }}
      50%,90% {{ transform: translateY(1px); }}
    }}
    .yoshi-wrap {{
      animation: yoshi-run {ANIM_DURATION}s linear infinite;
    }}
    .yoshi-bob {{
      animation: bob 0.3s ease-in-out infinite;
    }}
    .cell {{
      animation: eat {ANIM_DURATION}s ease-in-out infinite;
    }}
  </style>

  <!-- Background -->
  <rect width="{svg_width}" height="{svg_height}" fill="{BG_COLOR}" rx="6"/>

  <!-- Title -->
  <text x="{svg_width // 2}" y="{GRID_Y - 8}" font-family="'Press Start 2P',monospace" font-size="7" fill="#30A230" text-anchor="middle" opacity=".7">{total} contributions</text>

  <!-- Day labels -->
  {labels_svg}

  <!-- Contribution grid -->
  <g>
    {cells_svg}
  </g>

  <!-- Mario riding Yoshi — animated -->
  <g class="yoshi-wrap" transform="translate({GRID_X}, {yoshi_y})">
    <g class="yoshi-bob">
      {sprite_svg}
    </g>
  </g>
</svg>'''

    return svg


def main():
    print(f"Fetching contributions for {USERNAME}...")
    weeks, total = fetch_contributions()
    print(f"Found {total} contributions across {len(weeks)} weeks")

    svg = generate_svg(weeks, total)

    os.makedirs(os.path.dirname(OUTPUT) or ".", exist_ok=True)
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
