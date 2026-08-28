import os
import requests
from datetime import date, datetime, timedelta

USERNAME = "MRNobody1803"
TOKEN = os.environ["GITHUB_TOKEN"]

today = date.today()
year = today.year

query = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

variables = {
    "username": USERNAME,
    "from": f"{year}-01-01T00:00:00Z",
    "to": f"{year}-12-31T23:59:59Z",
}

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": variables},
    headers={"Authorization": f"Bearer {TOKEN}"},
)

data = response.json()

days = (
    data["data"]["user"]["contributionsCollection"]
    ["contributionCalendar"]["weeks"]
)

contributions = []

for week in days:
    for day in week["contributionDays"]:
        d = datetime.strptime(day["date"], "%Y-%m-%d").date()

        if d <= today:
            contributions.append(
                (d, day["contributionCount"])
            )

contributions.sort()

total = sum(count for _, count in contributions)

# -------------------------
# Longest streak this year
# -------------------------

longest_streak = 0
running_streak = 0

for _, count in contributions:
    if count > 0:
        running_streak += 1
        longest_streak = max(longest_streak, running_streak)
    else:
        running_streak = 0


# -------------------------
# Current streak
# -------------------------

current_streak = 0

for _, count in reversed(contributions):
    if count > 0:
        current_streak += 1
    else:
        break


# -------------------------
# SVG
# -------------------------

svg = f"""
<svg
    width="500"
    height="180"
    viewBox="0 0 500 180"
    xmlns="http://www.w3.org/2000/svg"
>

<style>

.title {{
    font: 600 22px sans-serif;
    fill: #70a5fd;
}}

.number {{
    font: 600 24px sans-serif;
    fill: #bf91f3;
}}

.label {{
    font: 14px sans-serif;
    fill: #a9b1d6;
}}

.year {{
    font: 13px sans-serif;
    fill: #787c99;
}}

</style>

<rect
    x="1"
    y="1"
    width="498"
    height="178"
    rx="10"
    fill="#1a1b27"
    stroke="#2f3549"
/>

<text
    x="250"
    y="35"
    text-anchor="middle"
    class="title"
>
    This Year's Streak
</text>


<!-- Current -->

<text
    x="85"
    y="90"
    text-anchor="middle"
    class="number"
>
    {current_streak}
</text>

<text
    x="85"
    y="115"
    text-anchor="middle"
    class="label"
>
    🔥 Current Streak
</text>


<!-- Longest -->

<text
    x="250"
    y="90"
    text-anchor="middle"
    class="number"
>
    {longest_streak}
</text>

<text
    x="250"
    y="115"
    text-anchor="middle"
    class="label"
>
    🏆 Longest Streak
</text>


<!-- Contributions -->

<text
    x="415"
    y="90"
    text-anchor="middle"
    class="number"
>
    {total}
</text>

<text
    x="415"
    y="115"
    text-anchor="middle"
    class="label"
>
    📊 Contributions
</text>


<text
    x="250"
    y="150"
    text-anchor="middle"
    class="year"
>
    {year}
</text>

</svg>
"""

os.makedirs("assets", exist_ok=True)

with open("assets/year-streak.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("Year streak card generated.")
