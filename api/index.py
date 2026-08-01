import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Query

app = FastAPI()

# Realistic browser headers to bypass basic Amazon anti-bot blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/"
}

@app.get("/api/check")
def check_product(url: str = Query(...), tag: str = Query(None)):
    if not url or not url.strip():
        return {"error": "Invalid URL"}
    
    try:
        # Send request with custom headers & follow redirects
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return {"error": f"Failed to fetch page. Status: {response.status_code}"}
            
        soup = BeautifulSoup(response.content, "lxml")

        # Extract Title
        title_el = soup.find("span", {"id": "productTitle"})
        title = title_el.get_text(strip=True) if title_el else "Amazon Product"

        # Extract Image
        img_el = soup.find("img", {"id": "landingImage"}) or soup.find("img", {"id": "imgBlkFront"})
        image = ""
        if img_el:
            image = img_el.get("src") or img_el.get("data-old-hires") or ""

        # Extract Price
        price_el = soup.find("span", {"class": "a-price-whole"})
        price = price_el.get_text(strip=True) if price_el else ""

        # Extract MRP / Original Price
        mrp_el = soup.find("span", {"class": "a-price a-text-price"})
        mrp = mrp_el.find("span", {"class": "a-offscreen"}).get_text(strip=True) if mrp_el and mrp_el.find("span", {"class": "a-offscreen"}) else ""

        # Build final link with affiliate tag appended
        final_url = response.url
        if tag and "tag=" not in final_url:
            connector = "&" if "?" in final_url else "?"
            final_url = f"{final_url}{connector}tag={tag}"

        return {
            "title": title,
            "image": image,
            "price": price,
            "mrp": mrp,
            "link": final_url
        }

    except Exception as e:
        return {"error": str(e)}
