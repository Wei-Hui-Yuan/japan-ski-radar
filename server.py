"""
FastAPI Server for Japanese Ski Resort Accommodation Radar
Serves REST API and Web Dashboard
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import csv
from fastapi import FastAPI, Query, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json

from scraper_engine import (
    SkiResortScraper,
    DEFAULT_CHECKIN,
    DEFAULT_CHECKOUT,
    DEFAULT_ADULTS,
    DEFAULT_ROOMS,
    RESORT_MOUNTAIN_DATA,
    get_resort_mountain_info
)

app = FastAPI(title="Japan Ski Lodging Radar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory cache
cached_data = {
    "checkin": DEFAULT_CHECKIN,
    "checkout": DEFAULT_CHECKOUT,
    "adults": DEFAULT_ADULTS,
    "rooms": DEFAULT_ROOMS,
    "lodges": [],
    "last_scraped_at": None,
    "is_scraping": False
}

CSV_FILEPATH = os.path.join(os.path.dirname(__file__), "lodges_availability.csv")

def run_background_scrape(checkin: str, checkout: str, adults: int, rooms: int):
    global cached_data
    cached_data["is_scraping"] = True
    try:
        scraper = SkiResortScraper(checkin=checkin, checkout=checkout, adults=adults, rooms=rooms)
        results = scraper.run_all()
        scraper.export_to_csv(results, CSV_FILEPATH)
        cached_data["checkin"] = checkin
        cached_data["checkout"] = checkout
        cached_data["adults"] = adults
        cached_data["rooms"] = rooms
        cached_data["lodges"] = results
        from datetime import datetime
        cached_data["last_scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    finally:
        cached_data["is_scraping"] = False

# Initialize cache
def initialize_cache():
    global cached_data
    if os.path.exists(CSV_FILEPATH):
        try:
            with open(CSV_FILEPATH, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                lodges = list(reader)
                if lodges:
                    for l in lodges:
                        l["available_dates"] = [DEFAULT_CHECKIN] if l.get("status_code") in ["AVAILABLE", "UNLOCKING_OCT_1"] else []
                        # parse numeric price for sorting
                        try:
                            l["price_per_person_night"] = int(l.get("price_per_person_night", 0) or 0)
                        except:
                            l["price_per_person_night"] = 0
                        # Ensure lift pass and rental fields are populated
                        if not l.get("lift_pass_est") or not l.get("recommended_rental_shop"):
                            info = get_resort_mountain_info(l.get("resort", ""))
                            lp = info["lift_passes"]
                            rentals = info.get("rentals", [])
                            r_shop = rentals[0]["name"] if rentals else "Resort Rental Base"
                            r_base = rentals[0]["base"] if rentals else "Main Station"
                            r_price = rentals[0]["standard_day"] if rentals else "¥5,000"
                            p_price = rentals[0]["powder_day"] if rentals else "¥7,000"
                            l["resort_id"] = info["id"]
                            l["lift_pass_est"] = f"1-Day: {lp['one_day']} | 4-Day: {lp['four_day']}"
                            l["lift_pass_1day"] = lp["one_day"]
                            l["lift_pass_4day"] = lp["four_day"]
                            l["lift_pass_5p_4d"] = lp["group_5p_4d"]
                            l["recommended_rental_shop"] = f"{r_shop} ({r_base})"
                            l["rental_daily_est"] = f"Standard {r_price}/d | Powder Demo {p_price}/d"
                    cached_data["lodges"] = lodges
                    from datetime import datetime
                    cached_data["last_scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[Cache] Loaded {len(lodges)} lodges with pricing and lift/rental info from CSV.")
                    return
        except Exception as e:
            print(f"[Cache] Error loading existing CSV: {e}")
    run_background_scrape(DEFAULT_CHECKIN, DEFAULT_CHECKOUT, DEFAULT_ADULTS, DEFAULT_ROOMS)

initialize_cache()

@app.on_event("startup")
def startup_event():
    print("[Startup] Server ready.")

class ScrapeRequest(BaseModel):
    checkin: Optional[str] = DEFAULT_CHECKIN
    checkout: Optional[str] = DEFAULT_CHECKOUT
    adults: Optional[int] = DEFAULT_ADULTS
    rooms: Optional[int] = DEFAULT_ROOMS

@app.get("/api/resorts")
@app.get("/resorts")
def get_resorts():
    """Returns comprehensive mountain lift pass rates, trail specs, and rental shop directories for all 9 ski regions."""
    return {
        "status": "success",
        "total": len(RESORT_MOUNTAIN_DATA),
        "data": RESORT_MOUNTAIN_DATA
    }

@app.get("/api/debug")
@app.get("/debug")
def debug_endpoint(request: Request):
    return {
        "path": request.scope.get("path"),
        "root_path": request.scope.get("root_path"),
        "url": str(request.url)
    }

@app.get("/api/lodges")
@app.get("/lodges")
def get_lodges(
    resort: Optional[str] = Query(None, description="Filter by resort name"),
    status: Optional[str] = Query(None, description="Filter by status_code"),
    search: Optional[str] = Query(None, description="Search query"),
    sort: Optional[str] = Query("priority", description="Sort order: priority, price_asc, price_desc")
):
    global cached_data
    lodges = list(cached_data["lodges"])
    
    # Filter by resort
    if resort and resort != "all":
        lodges = [l for l in lodges if resort.lower() in l["resort"].lower()]
        
    # Filter by status code
    if status and status != "all":
        lodges = [l for l in lodges if l["status_code"] == status]
        
    # Filter by search
    if search:
        s = search.lower()
        lodges = [
            l for l in lodges 
            if s in l["name"].lower() or s in l["name_en"].lower() or s in l["area"].lower() or s in l.get("notes", "").lower()
        ]

    # Sort
    if sort == "price_asc":
        lodges.sort(key=lambda x: (x.get("price_per_person_night", 999999) or 999999))
    elif sort == "price_desc":
        lodges.sort(key=lambda x: (x.get("price_per_person_night", 0) or 0), reverse=True)

    return {
        "status": "success",
        "total": len(lodges),
        "checkin": cached_data["checkin"],
        "checkout": cached_data["checkout"],
        "adults": cached_data["adults"],
        "rooms": cached_data["rooms"],
        "last_scraped_at": cached_data["last_scraped_at"],
        "is_scraping": cached_data["is_scraping"],
        "data": lodges
    }

@app.post("/api/scrape")
@app.post("/scrape")
def trigger_scrape(req: ScrapeRequest, background_tasks: BackgroundTasks):
    global cached_data
    if cached_data["is_scraping"]:
        return {"status": "in_progress", "message": "Scrape currently executing"}
    
    # Run synchronously or in background
    run_background_scrape(req.checkin, req.checkout, req.adults, req.rooms)
    return {
        "status": "completed",
        "message": f"Scrape completed for {req.checkin} to {req.checkout} ({req.adults} adults)",
        "total_lodges": len(cached_data["lodges"])
    }

@app.get("/api/stats")
@app.get("/stats")
def get_stats():
    global cached_data
    lodges = cached_data["lodges"]
    return {
        "total_monitored": len(lodges),
        "available_now": sum(1 for l in lodges if l["status_code"] == "AVAILABLE"),
        "unlocking_oct_1": sum(1 for l in lodges if l["status_code"] == "UNLOCKING_OCT_1"),
        "partial_open": sum(1 for l in lodges if l["status_code"] == "PARTIAL"),
        "direct_inquiry": sum(1 for l in lodges if l["status_code"] == "INQUIRY"),
        "unavailable": sum(1 for l in lodges if l["status_code"] == "UNAVAILABLE"),
        "last_scraped_at": cached_data["last_scraped_at"],
        "checkin": cached_data["checkin"],
        "checkout": cached_data["checkout"],
        "adults": cached_data["adults"]
    }

@app.get("/api/export")
@app.get("/export")
def export_csv():
    global cached_data
    if os.path.exists(CSV_FILEPATH):
        return FileResponse(
            path=CSV_FILEPATH,
            filename=f"Japan_Ski_Accommodations_{cached_data['checkin']}_to_{cached_data['checkout']}.csv",
            media_type="text/csv"
        )
    # In-memory CSV streaming fallback for serverless read-only containers
    import io
    from fastapi import Response
    output = io.StringIO()
    fieldnames = [
        "resort", "name", "name_en", "status", "status_code", "price_per_person_night",
        "price_display", "price_unit", "group_total_est", "meal_plan",
        "lift_pass_est", "lift_pass_4day", "recommended_rental_shop", "rental_daily_est",
        "total_nights_available", "phone", "lift_proximity", "room_recommendation",
        "area", "address", "direct_link", "notes"
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(cached_data["lodges"])
    return Response(
        content=output.getvalue().encode("utf-8-sig"),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=Japan_Ski_Accommodations_{cached_data['checkin']}_to_{cached_data['checkout']}.csv"}
    )

# Mount public / static folder
public_dir = os.path.join(os.path.dirname(__file__), "public")
static_dir = os.path.join(os.path.dirname(__file__), "static")
mount_dir = public_dir if os.path.exists(public_dir) else static_dir
if os.path.exists(mount_dir):
    app.mount("/", StaticFiles(directory=mount_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
