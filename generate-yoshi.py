#!/usr/bin/env python3
"""
Generate a Mario/Yoshi-themed contribution grid SVG.
A pixel art Yoshi sprite animates across the contribution grid, "eating" each cell.
"""

import json
import os
import sys
import urllib.request
import urllib.error

USERNAME = os.environ.get("GITHUB_USER", "taylfrad")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT = os.environ.get("OUTPUT_PATH", "dist/yoshi-contrib.svg")

# Colors matching Mario night theme
BG_COLOR = "#050c21"
EMPTY_COLOR = "#0a1628"
# Contribution level colors (green -> gold like collecting coins)
LEVEL_COLORS = ["#0a1628", "#1a3a2a", "#30A230", "#58D858", "#FFD700"]

# Grid layout
CELL_SIZE = 11
CELL_GAP = 3
CELL_TOTAL = CELL_SIZE + CELL_GAP
GRID_X = 40
GRID_Y = 20

# Animation
ANIM_DURATION = 20  # seconds for full traverse


def fetch_contributions():
    """Fetch contribution data from GitHub GraphQL API."""
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
    """Map contribution count to a level 0-4."""
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


def build_yoshi_sprite():
    """Build pixel art Yoshi as SVG group (facing right, ~16x18 px grid at 2px per pixel)."""
    p = 2  # pixel size
    pixels = [
        # Head dome (green)
        (5, 0, 4, 2, "#30A230"),
        (4, 2, 6, 2, "#30A230"),
        (3, 4, 8, 2, "#30A230"),
        # Eye (white + pupil)
        (8, 2, 3, 3, "#fff"),
        (10, 3, 1, 2, "#000"),
        # Nose/snout (green, extends forward)
        (11, 4, 3, 2, "#30A230"),
        (11, 6, 3, 2, "#30A230"),
        (12, 8, 2, 1, "#30A230"),
        # Head bottom / mouth
        (3, 6, 5, 1, "#30A230"),
        (4, 7, 7, 1, "#fff"),  # mouth line white
        # Red crest/ridge on top
        (4, 0, 1, 1, "#E84030"),
        (3, 1, 1, 1, "#E84030"),
        # Body (green)
        (4, 8, 6, 3, "#30A230"),
        (3, 9, 1, 2, "#30A230"),
        # Belly (white)
        (5, 9, 4, 2, "#fff"),
        # Shell (red on back)
        (3, 8, 2, 1, "#E84030"),
        (2, 9, 2, 2, "#E84030"),
        # Arms
        (2, 8, 1, 2, "#30A230"),
        (10, 8, 1, 2, "#30A230"),
        # Legs / boots (orange-red)
        (3, 11, 3, 2, "#E87020"),
        (7, 11, 3, 2, "#E87020"),
        # Tail
        (1, 10, 2, 1, "#30A230"),
        (0, 11, 2, 1, "#30A230"),
    ]
    rects = []
    for x, y, w, h, color in pixels:
        rects.append(f'<rect x="{x*p}" y="{y*p}" width="{w*p}" height="{h*p}" fill="{color}"/>')
    return "\n      ".join(rects)


def generate_svg(weeks, total):
    """Generate the full SVG with contribution grid and animated Yoshi."""
    num_weeks = len(weeks)
    max_days = 7

    grid_width = num_weeks * CELL_TOTAL
    svg_width = grid_width + GRID_X + 20
    svg_height = max_days * CELL_TOTAL + GRID_Y + 40

    yoshi_svg = build_yoshi_sprite()
    yoshi_width = 28  # sprite width in svg units
    yoshi_travel = grid_width + yoshi_width + 40

    # Build grid cells with eat animation
    cells = []
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week["contributionDays"]):
            level = contribution_level(day["contributionCount"])
            color = LEVEL_COLORS[level]
            x = GRID_X + wi * CELL_TOTAL
            y = GRID_Y + day["weekday"] * CELL_TOTAL

            # Calculate when Yoshi reaches this column
            col_pct = wi / max(num_weeks - 1, 1)
            eat_pct = col_pct * 75 + 5  # Yoshi traverses from 5% to 80%

            cell_id = f"c{wi}_{di}"

            if level > 0:
                cells.append(
                    f'<rect id="{cell_id}" x="{x}" y="{y}" '
                    f'width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" '
                    f'fill="{color}" class="cell" '
                    f'style="animation-delay:{eat_pct / 100 * ANIM_DURATION:.1f}s"/>'
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
            y = GRID_Y + i * CELL_TOTAL + CELL_SIZE - 1
            labels_svg += f'<text x="{GRID_X - 5}" y="{y}" font-family="\'Press Start 2P\',monospace" font-size="6" fill="#6B7280" text-anchor="end">{label}</text>\n    '

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <style>
    @keyframes yoshi-run {{
      0% {{ transform: translateX(-{yoshi_width + 20}px); }}
      5% {{ transform: translateX(0px); }}
      80% {{ transform: translateX({grid_width}px); }}
      85%,100% {{ transform: translateX({grid_width + 40}px); }}
    }}
    @keyframes eat {{
      0%,90% {{ transform: scale(1); opacity: 1; }}
      95% {{ transform: scale(1.3); opacity: 0.8; }}
      100% {{ transform: scale(0); opacity: 0; }}
    }}
    @keyframes legs {{
      0%,49% {{ transform: translateX(0); }}
      50%,100% {{ transform: translateX(2px); }}
    }}
    @keyframes chomp {{
      0%,40% {{ transform: scaleY(1); }}
      50% {{ transform: scaleY(0.7); }}
      60%,100% {{ transform: scaleY(1); }}
    }}
    .yoshi-wrap {{
      animation: yoshi-run {ANIM_DURATION}s linear infinite;
    }}
    .yoshi-legs {{
      animation: legs 0.2s step-end infinite;
      transform-origin: center bottom;
    }}
    .yoshi-mouth {{
      animation: chomp 0.4s ease-in-out infinite;
      transform-origin: right center;
    }}
    .cell {{
      animation: eat {ANIM_DURATION}s ease-in-out infinite;
    }}
  </style>

  <!-- Background -->
  <rect width="{svg_width}" height="{svg_height}" fill="{BG_COLOR}" rx="6"/>

  <!-- Title -->
  <text x="{svg_width // 2}" y="{GRID_Y - 6}" font-family="\'Press Start 2P\',monospace" font-size="7" fill="#30A230" text-anchor="middle" opacity=".7">{total} contributions</text>

  <!-- Day labels -->
  {labels_svg}

  <!-- Contribution grid -->
  <g>
    {cells_svg}
  </g>

  <!-- Yoshi sprite — animated -->
  <g class="yoshi-wrap" transform="translate({GRID_X}, {GRID_Y + 2 * CELL_TOTAL - 6})">
    <g class="yoshi-legs">
      <g class="yoshi-mouth">
        {yoshi_svg}
      </g>
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
