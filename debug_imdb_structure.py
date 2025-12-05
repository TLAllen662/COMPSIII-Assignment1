import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print("Fetching IMDb top 250 page...")
r = requests.get('https://www.imdb.com/chart/top/', headers=headers, timeout=10)
print(f"Status: {r.status_code}")

soup = BeautifulSoup(r.content, 'html.parser')

# Look for movie data in different possible locations
print("\nLooking for movies...")

# Try to find rows
rows = soup.find_all("tr", {"data-testid": "rating-cell-wrapper"})
print(f"Found {len(rows)} rows with data-testid='rating-cell-wrapper'")

if not rows:
    rows = soup.find_all("tr")
    print(f"Found {len(rows)} total <tr> elements")

# Show first few rows structure
print("\nFirst 3 rows structure:")
for i, row in enumerate(rows[:3]):
    print(f"\n--- Row {i} ---")
    print(row.prettify()[:500])

# Try to find all links
print("\n\nLooking for movie links...")
links = soup.find_all("a", {"data-testid": "title"})
print(f"Found {len(links)} links with data-testid='title'")

if links:
    print("\nFirst 3 links:")
    for i, link in enumerate(links[:3]):
        print(f"{i+1}. {link.get_text()} - {link.get('href')}")

# Try to find titles with alternate selectors
print("\n\nTrying alternate selectors...")
td_cells = soup.find_all("td", {"data-testid": "titleCell"})
print(f"Found {len(td_cells)} td with data-testid='titleCell'")

if td_cells:
    print("\nFirst 2 title cells:")
    for i, cell in enumerate(td_cells[:2]):
        print(f"\n--- Cell {i} ---")
        print(cell.prettify()[:1000])
