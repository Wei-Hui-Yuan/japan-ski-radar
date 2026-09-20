/**
 * Nagano Powder Radar - Frontend Application Logic
 * Integrates Live Lodging Tracker, Ski Lifts & Rentals Guide, and 5-Person Group Trip Calculator
 */

let allLodges = [];
let resortsData = {};
let currentResortFilter = "all";
let currentStatusFilter = "all";
let currentSearchQuery = "";
let currentSortOrder = "priority";

let activeResortKey = "Nozawa Onsen";
let selectedGearTier = "standard"; // "standard", "powder", "wear"
let includeNightSki = false;

// DOM Elements - Navigation & Core Controls
const lodgesGrid = document.getElementById("lodges-grid");
const inputSearch = document.getElementById("input-search");
const btnClearSearch = document.getElementById("btn-clear-search");
const selectStatus = document.getElementById("select-status-filter");
const selectSort = document.getElementById("select-sort-filter");
const resortChips = document.querySelectorAll(".filter-chip");
const statCards = document.querySelectorAll(".stat-card");

const btnRunScrape = document.getElementById("btn-run-scrape");
const scrapeBtnText = document.getElementById("scrape-btn-text");
const scrapeIcon = document.getElementById("scrape-icon");
const btnExportCsv = document.getElementById("btn-export-csv");

// Scrape Modal Elements
const modalScrape = document.getElementById("modal-scrape");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnCancelModal = document.getElementById("btn-cancel-modal");
const btnStartScrape = document.getElementById("btn-start-scrape");

// Mountain Lifts & Rentals Modal Elements
const modalResorts = document.getElementById("modal-resorts");
const btnOpenResortsModal = document.getElementById("btn-open-resorts-modal");
const btnCloseResortsModal = document.getElementById("btn-close-resorts-modal");
const resortTabsContainer = document.getElementById("resort-tabs-container");
const resortDetailContent = document.getElementById("resort-detail-content");

// Total Trip Cost Calculator Elements
const modalCalculator = document.getElementById("modal-calculator");
const btnOpenTripCalc = document.getElementById("btn-open-trip-calc");
const btnCloseCalcModal = document.getElementById("btn-close-calc-modal");

// Stats Elements
const statTotal = document.getElementById("stat-total");
const statAvailable = document.getElementById("stat-available");
const statUnlocking = document.getElementById("stat-unlocking");
const statPartial = document.getElementById("stat-partial");
const statInquiry = document.getElementById("stat-inquiry");
const displayUpdated = document.getElementById("display-updated");

// Initialize application
document.addEventListener("DOMContentLoaded", () => {
  fetchStats();
  fetchLodges();
  fetchResorts();
  setupEventListeners();
  setupCalculatorEventListeners();
});

function setupEventListeners() {
  // Search input
  inputSearch.addEventListener("input", (e) => {
    currentSearchQuery = e.target.value.trim().toLowerCase();
    btnClearSearch.classList.toggle("hidden", currentSearchQuery.length === 0);
    renderLodges();
  });

  btnClearSearch.addEventListener("click", () => {
    inputSearch.value = "";
    currentSearchQuery = "";
    btnClearSearch.classList.add("hidden");
    renderLodges();
  });

  // Resort filter chips
  resortChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      resortChips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      currentResortFilter = chip.dataset.resort;
      renderLodges();
    });
  });

  // Status select filter
  selectStatus.addEventListener("change", (e) => {
    currentStatusFilter = e.target.value;
    updateActiveStatCard(currentStatusFilter);
    renderLodges();
  });

  // Sort select filter
  if (selectSort) {
    selectSort.addEventListener("change", (e) => {
      currentSortOrder = e.target.value;
      renderLodges();
    });
  }

  // Stat cards filter clicks
  statCards.forEach((card) => {
    card.addEventListener("click", () => {
      const filter = card.dataset.filter;
      currentStatusFilter = filter;
      selectStatus.value = filter;
      updateActiveStatCard(filter);
      renderLodges();
    });
  });

  // Export CSV
  btnExportCsv.addEventListener("click", () => {
    window.location.href = "/api/export";
  });

  // Scrape Modal interactions
  btnRunScrape.addEventListener("click", () => {
    modalScrape.classList.remove("hidden");
  });

  btnCloseModal.addEventListener("click", () => {
    modalScrape.classList.add("hidden");
  });

  btnCancelModal.addEventListener("click", () => {
    modalScrape.classList.add("hidden");
  });

  modalScrape.addEventListener("click", (e) => {
    if (e.target === modalScrape) {
      modalScrape.classList.add("hidden");
    }
  });

  btnStartScrape.addEventListener("click", triggerScrape);

  // Mountain Lifts & Rentals Modal
  if (btnOpenResortsModal) {
    btnOpenResortsModal.addEventListener("click", () => {
      openResortsModal();
    });
  }

  if (btnCloseResortsModal) {
    btnCloseResortsModal.addEventListener("click", () => {
      closeResortsModal();
    });
  }

  if (modalResorts) {
    modalResorts.addEventListener("click", (e) => {
      if (e.target === modalResorts) {
        closeResortsModal();
      }
    });
  }
}

function updateActiveStatCard(filterValue) {
  statCards.forEach((card) => {
    if (card.dataset.filter === filterValue) {
      card.classList.add("active-stat");
    } else {
      card.classList.remove("active-stat");
    }
  });
}

// Data Fetching: Stats
async function fetchStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    if (statTotal) statTotal.textContent = data.total_monitored || 0;
    if (statAvailable) statAvailable.textContent = data.available_now || 0;
    if (statUnlocking) statUnlocking.textContent = data.unlocking_oct_1 || 0;
    if (statPartial) statPartial.textContent = data.partial_open || 0;
    if (statInquiry) statInquiry.textContent = data.direct_inquiry || 0;

    if (data.last_scraped_at && displayUpdated) {
      displayUpdated.textContent = data.last_scraped_at;
    }
  } catch (err) {
    console.error("Error fetching radar stats:", err);
  }
}

// Data Fetching: Lodges
async function fetchLodges() {
  try {
    const res = await fetch("/api/lodges");
    const json = await res.json();
    allLodges = json.data || [];
    renderLodges();
    populateCalcLodgeSelect();
  } catch (err) {
    console.error("Error fetching lodges:", err);
    lodgesGrid.innerHTML = `
      <div class="empty-state">
        <p>⚠️ Failed to load lodge data from server.</p>
      </div>
    `;
  }
}

// Data Fetching: Resorts (Mountain Lifts & Rentals)
async function fetchResorts() {
  try {
    const res = await fetch("/api/resorts");
    const json = await res.json();
    resortsData = json.data || {};
    renderResortTabs();
  } catch (err) {
    console.error("Error fetching resort mountain data:", err);
  }
}

const RESORT_SHORT_LABELS = {
  "Nozawa Onsen": "♨️ Nozawa Onsen",
  "Hakuba Valley": "🏔️ Hakuba Valley",
  "Madarao & Tangram": "🌲 Madarao & Tangram",
  "Myoko Kogen": "❄️ Myoko Kogen",
  "Echigo-Yuzawa & Naeba": "🚅 Yuzawa & Naeba",
  "Shiga Kogen": "🗻 Shiga Kogen",
  "Karuizawa & Sugadaira": "🛍️ Karuizawa & Sugadaira",
  "Kusatsu & Manza Onsen": "♨️ Kusatsu & Manza",
  "Ryuoo & Togakushi": "☁️ Ryuoo & Togakushi"
};

// Render Resort Tabs inside Modal
function renderResortTabs() {
  if (!resortTabsContainer) return;
  const keys = Object.keys(resortsData);
  if (keys.length === 0) return;

  resortTabsContainer.innerHTML = keys.map((key) => {
    const r = resortsData[key];
    const label = RESORT_SHORT_LABELS[key] || (r ? r.name.split(' (')[0] : key);
    const isActive = key === activeResortKey ? "active" : "";
    return `
      <button type="button" class="resort-tab-btn ${isActive}" onclick="selectResortTab('${key}')">
        ${label}
      </button>
    `;
  }).join("");
}

function selectResortTab(key) {
  activeResortKey = key;
  renderResortTabs();
  renderResortDetail(key);
}

// Open / Close Resorts Modal
function openResortsModal(resortName = null) {
  if (resortName && resortsData) {
    // Find matching resort key
    const matchKey = Object.keys(resortsData).find(k =>
      resortName.toLowerCase().includes(k.toLowerCase()) ||
      k.toLowerCase().includes(resortName.toLowerCase()) ||
      (resortsData[k].id && resortName.toLowerCase().includes(resortsData[k].id))
    );
    if (matchKey) {
      activeResortKey = matchKey;
    }
  }
  renderResortTabs();
  renderResortDetail(activeResortKey);
  modalResorts.classList.remove("hidden");
}

function closeResortsModal() {
  modalResorts.classList.add("hidden");
}

// Render Detailed Mountain & Rental View
function renderResortDetail(resortKey) {
  if (!resortDetailContent) return;
  const resort = resortsData[resortKey] || Object.values(resortsData)[0];
  if (!resort) return;

  const lp = resort.lift_passes || {};
  const terrain = resort.terrain || { beginner: 35, intermediate: 40, advanced: 25 };
  const rentals = resort.rentals || [];

  // Calculate costs for 5 adults x 4 days
  const fourDayPassNum = lp.four_day_val || 26000;
  const liftTotal5p4d = fourDayPassNum * 5;

  let dailyGearCostPerPerson = 5000;
  let gearTierTitle = "Standard Alpine Set";
  if (rentals.length > 0) {
    const firstShop = rentals[0];
    if (selectedGearTier === "powder") {
      dailyGearCostPerPerson = firstShop.powder_day_val || 7000;
      gearTierTitle = "Powder Demo Fleet";
    } else if (selectedGearTier === "wear") {
      const g = firstShop.standard_day_val || 5000;
      const w = firstShop.wear_day_val || 3500;
      dailyGearCostPerPerson = g + w;
      gearTierTitle = "Gear + Ski Outerwear";
    } else {
      dailyGearCostPerPerson = firstShop.standard_day_val || 5000;
      gearTierTitle = "Standard Alpine Set";
    }
  }

  const rentalTotal5p4d = dailyGearCostPerPerson * 4 * 5;
  const combinedTotal = liftTotal5p4d + rentalTotal5p4d;
  const perPersonCombined = Math.round(combinedTotal / 5);

  resortDetailContent.innerHTML = `
    <!-- Mountain Hero Banner -->
    <div class="mountain-hero">
      <div class="mountain-hero-title">
        <h3>${resort.name}</h3>
        <div class="mountain-hero-ja">${resort.name_ja}</div>
        <div class="mountain-hero-region">📍 ${resort.region} • ${resort.elevation}</div>
      </div>
      <div class="mountain-hero-badges">
        <span class="powder-tag">${resort.powder_rating}</span>
        <span class="elevation-tag">🏔️ Vertical Drop: ${resort.vertical_drop}m</span>
      </div>
    </div>

    <!-- Mountain Key Specs Grid -->
    <div class="mountain-stats-grid">
      <div class="mountain-stat-box">
        <div class="stat-label">Total Lifts</div>
        <div class="stat-val">${resort.total_lifts} Lifts</div>
        <div class="stat-sub">${resort.total_gondolas} High-Speed Gondolas</div>
      </div>
      <div class="mountain-stat-box">
        <div class="stat-label">Courses / Trails</div>
        <div class="stat-val">${resort.courses_count} Trails</div>
        <div class="stat-sub">Glades & Groomers</div>
      </div>
      <div class="mountain-stat-box">
        <div class="stat-label">Longest Cruising Run</div>
        <div class="stat-val">${resort.longest_run.split(' ')[0]}</div>
        <div class="stat-sub">Top to Bottom Cruiser</div>
      </div>
      <div class="mountain-stat-box">
        <div class="stat-label">Lift Pass (4-Day)</div>
        <div class="stat-val">${lp.four_day}</div>
        <div class="stat-sub">Dec 29 – Jan 2 Holiday</div>
      </div>
    </div>

    <!-- Terrain Difficulty Distribution -->
    <div class="terrain-container">
      <div class="terrain-header">
        <span>Terrain Profile Breakdown</span>
        <span>${terrain.beginner}% Beginner • ${terrain.intermediate}% Intermediate • ${terrain.advanced}% Advanced</span>
      </div>
      <div class="terrain-bar-track">
        <div class="terrain-seg-beg" style="width: ${terrain.beginner}%;" title="Beginner: ${terrain.beginner}%"></div>
        <div class="terrain-seg-int" style="width: ${terrain.intermediate}%;" title="Intermediate: ${terrain.intermediate}%"></div>
        <div class="terrain-seg-adv" style="width: ${terrain.advanced}%;" title="Advanced / Powder: ${terrain.advanced}%"></div>
      </div>
      <div class="terrain-legend">
        <span><span class="legend-dot" style="background:#10b981;"></span> Beginner (Green)</span>
        <span><span class="legend-dot" style="background:#0284c7;"></span> Intermediate (Red/Blue)</span>
        <span><span class="legend-dot" style="background:#ef4444;"></span> Advanced / Tree Run (Black)</span>
      </div>
    </div>

    <!-- Two-Column Lift Pass & Rentals Grid -->
    <div class="lifts-rentals-grid">
      <!-- Card 1: Official Lift Pass Rates -->
      <div class="guide-card">
        <div class="guide-card-header">
          <span style="font-size:1.3rem;">🚡</span>
          <h4>Official Lift Pass Matrix</h4>
        </div>
        <div class="lift-price-matrix">
          <div class="lift-price-row">
            <span class="lift-price-label">1-Day Lift Pass:</span>
            <span class="lift-price-value">${lp.one_day}</span>
          </div>
          <div class="lift-price-row">
            <span class="lift-price-label">4-Day Holiday Pass:</span>
            <span class="lift-price-value">${lp.four_day}</span>
          </div>
          <div class="lift-price-row">
            <span class="lift-price-label">5-Person Group (4 Days):</span>
            <span class="lift-price-value" style="color:#10b981;">${lp.group_5p_4d}</span>
          </div>
          <div class="lift-price-row">
            <span class="lift-price-label">Night Skiing:</span>
            <span class="lift-price-value" style="font-size:0.95rem; color:#f59e0b;">${lp.night_ski}</span>
          </div>
        </div>
        <div class="lift-perks-box">
          <strong>Pass Type:</strong> ${lp.pass_type}<br>
          <strong>Highlights:</strong> ${lp.highlights}
        </div>
      </div>

      <!-- Card 2: Recommended Gear Rental Shops -->
      <div class="guide-card">
        <div class="guide-card-header">
          <span style="font-size:1.3rem;">🎿</span>
          <h4>Curated Rental Shops Directory</h4>
        </div>
        <div class="rental-shop-list">
          ${rentals.map(shop => `
            <div class="rental-shop-item">
              <div class="rental-shop-top">
                <div>
                  <div class="rental-shop-name">${shop.name}</div>
                  <div class="rental-shop-base">📍 ${shop.base}</div>
                </div>
                <a href="tel:${shop.phone.replace(/[^0-9]/g, '')}" class="rental-tel-btn">📞 ${shop.phone}</a>
              </div>
              <div class="rental-price-tags">
                <span class="rental-price-tag">Standard: <strong>${shop.standard_day}/d</strong></span>
                <span class="rental-price-tag">Powder Demo: <strong>${shop.powder_day}/d</strong></span>
                <span class="rental-price-tag">Wear: <strong>${shop.wear_day}/d</strong></span>
              </div>
              <div class="rental-features">✨ ${shop.features}</div>
            </div>
          `).join("")}
        </div>
      </div>
    </div>

    <!-- Card 3: Interactive 5-Person Group Trip Cost Estimator -->
    <div class="trip-calculator-box">
      <div class="calculator-header">
        <div>
          <h4>🧮 5-Person Trip Cost Estimator (${resort.name.split(' (')[0]})</h4>
          <span class="calculator-sub">Dec 29, 2026 – Jan 2, 2027 (4 Days • 5 Adult Males)</span>
        </div>
        <span class="badge-accent">Custom Group Math</span>
      </div>

      <!-- Option Selector -->
      <div class="calc-options-grid">
        <div class="calc-option-card ${selectedGearTier === 'standard' ? 'active' : ''}" onclick="setGearTier('standard')">
          <div class="calc-option-title">Tier 1: Standard Gear</div>
          <div class="calc-option-rate">~¥5,000 / day / person</div>
          <p style="font-size:0.72rem; color:var(--text-muted); margin-top:2px;">Carving skis/snowboard, boots & poles</p>
        </div>

        <div class="calc-option-card ${selectedGearTier === 'powder' ? 'active' : ''}" onclick="setGearTier('powder')">
          <div class="calc-option-title">Tier 2: Powder Demo Fleet</div>
          <div class="calc-option-rate">~¥7,000 / day / person</div>
          <p style="font-size:0.72rem; color:var(--text-muted); margin-top:2px;">Armada/Salomon wide fat skis & powder boards</p>
        </div>

        <div class="calc-option-card ${selectedGearTier === 'wear' ? 'active' : ''}" onclick="setGearTier('wear')">
          <div class="calc-option-title">Tier 3: Gear + Outerwear</div>
          <div class="calc-option-rate">~¥8,500 / day / person</div>
          <p style="font-size:0.72rem; color:var(--text-muted); margin-top:2px;">Skis/board + waterproof jacket & pants set</p>
        </div>
      </div>

      <!-- Live Calculation Results -->
      <div class="calc-totals-display">
        <div class="calc-total-item">
          <div class="calc-total-label">4-Day Lift Passes (5 Guests)</div>
          <div class="calc-total-value">${lp.group_5p_4d}</div>
          <div class="calc-total-sub">${lp.four_day} × 5 skiers</div>
        </div>

        <div class="calc-total-item highlight-total">
          <div class="calc-total-label">4-Day Gear Rentals (5 Guests)</div>
          <div class="calc-total-value">¥${rentalTotal5p4d.toLocaleString()}</div>
          <div class="calc-total-sub">${gearTierTitle} (${dailyGearCostPerPerson.toLocaleString()} × 4d × 5p)</div>
        </div>

        <div class="calc-total-item">
          <div class="calc-total-label">Total Mountain Lifts & Gear</div>
          <div class="calc-total-value color-cyan">¥${combinedTotal.toLocaleString()}</div>
          <div class="calc-total-sub">~¥${perPersonCombined.toLocaleString()} / person total</div>
        </div>
      </div>
    </div>
  `;
}

function setGearTier(tier) {
  selectedGearTier = tier;
  const currentScroll = resortDetailContent ? resortDetailContent.scrollTop : 0;
  renderResortDetail(activeResortKey);
  if (resortDetailContent) {
    resortDetailContent.scrollTop = currentScroll;
  }
}

// Lodges Rendering Logic
function renderLodges() {
  let filtered = allLodges.filter((lodge) => {
    // Resort filter
    if (currentResortFilter !== "all") {
      if (!lodge.resort.toLowerCase().includes(currentResortFilter.toLowerCase())) {
        return false;
      }
    }

    // Status filter
    if (currentStatusFilter !== "all") {
      if (lodge.status_code !== currentStatusFilter) {
        return false;
      }
    }

    // Search query
    if (currentSearchQuery) {
      const match =
        lodge.name.toLowerCase().includes(currentSearchQuery) ||
        lodge.name_en.toLowerCase().includes(currentSearchQuery) ||
        lodge.area.toLowerCase().includes(currentSearchQuery) ||
        (lodge.notes && lodge.notes.toLowerCase().includes(currentSearchQuery)) ||
        (lodge.price_display && lodge.price_display.toLowerCase().includes(currentSearchQuery)) ||
        (lodge.recommended_rental_shop && lodge.recommended_rental_shop.toLowerCase().includes(currentSearchQuery));
      if (!match) return false;
    }

    return true;
  });

  // Sort Order
  if (currentSortOrder === "price_asc") {
    filtered.sort((a, b) => (parseInt(a.price_per_person_night, 10) || 999999) - (parseInt(b.price_per_person_night, 10) || 999999));
  } else if (currentSortOrder === "price_desc") {
    filtered.sort((a, b) => (parseInt(b.price_per_person_night, 10) || 0) - (parseInt(a.price_per_person_night, 10) || 0));
  }

  if (filtered.length === 0) {
    lodgesGrid.innerHTML = `
      <div class="empty-state">
        <p>No accommodations match your current filter criteria.</p>
        <button class="btn btn-secondary" onclick="resetFilters()">Reset All Filters</button>
      </div>
    `;
    return;
  }

  lodgesGrid.innerHTML = filtered.map((lodge) => createLodgeCardHtml(lodge)).join("");
}

function resetFilters() {
  currentResortFilter = "all";
  currentStatusFilter = "all";
  currentSearchQuery = "";
  currentSortOrder = "priority";
  inputSearch.value = "";
  selectStatus.value = "all";
  if (selectSort) selectSort.value = "priority";
  resortChips.forEach((c) => c.classList.toggle("active", c.dataset.resort === "all"));
  updateActiveStatCard("all");
  renderLodges();
}

function escapeJs(str) {
  if (!str) return "";
  return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function createLodgeCardHtml(lodge) {
  const badgeClass = `badge-${lodge.status_code}`;
  const phoneBtn = lodge.phone
    ? `<a href="tel:${lodge.phone.replace(/[^0-9]/g, '')}" class="btn btn-call" title="Call directly">
        📞 ${lodge.phone}
       </a>`
    : "";

  const priceHtml = `
    <div class="card-price-banner">
      <div class="price-main-line">
        <span class="price-amount">${lodge.price_display || 'Contact for Pricing'}</span>
        <span class="price-unit">${lodge.price_unit || '/ person / night'}</span>
      </div>
      <div class="price-group-sub">
        Group Est. (5p • 4n): <strong>${lodge.group_total_est || 'Calculated on inquiry'}</strong>
      </div>
      <div class="price-meal-tag">
        <span>🍱</span> ${lodge.meal_plan || 'Contact lodge for meal package'}
      </div>
    </div>
  `;

  const mountainPreviewHtml = `
    <div class="card-mountain-preview">
      <div class="mountain-stat-pill">
        <span class="pill-icon">🚡</span>
        <span class="pill-title">Lift Pass:</span>
        <span class="pill-value">${lodge.lift_pass_est || '1-Day: ~¥7,300 | 4-Day: ~¥26,000'}</span>
      </div>
      <div class="mountain-stat-pill">
        <span class="pill-icon">🎿</span>
        <span class="pill-title">Nearby Rental:</span>
        <span class="pill-value">${lodge.recommended_rental_shop || 'Compass House / Base Station'}</span>
      </div>
      <button type="button" class="btn-resort-details" onclick="openResortsModal('${escapeJs(lodge.resort)}')">
        View Mountain & Rental Guide ➔
      </button>
    </div>
  `;

  return `
    <article class="lodge-card">
      <div>
        <div class="card-top">
          <span class="resort-tag">${lodge.resort}</span>
          <span class="status-badge ${badgeClass}">${lodge.status}</span>
        </div>

        <div class="card-title-group">
          <h2 class="lodge-name-ja">${lodge.name}</h2>
          <div class="lodge-name-en">${lodge.name_en}</div>
        </div>

        ${priceHtml}

        <div class="card-details-list">
          <div class="detail-row">
            <span class="detail-icon">📍</span>
            <span class="detail-text"><strong>Area:</strong> ${lodge.area}</span>
          </div>
          <div class="detail-row">
            <span class="detail-icon">⛷️</span>
            <span class="detail-text"><strong>Lift Proximity:</strong> ${lodge.lift_proximity}</span>
          </div>
          <div class="detail-row">
            <span class="detail-icon">🛏️</span>
            <span class="detail-text"><strong>Setup:</strong> ${lodge.room_recommendation}</span>
          </div>
        </div>

        ${mountainPreviewHtml}

        <div class="card-notes">
          "${lodge.notes}"
        </div>
      </div>

      <div class="card-actions">
        ${phoneBtn}
        <a href="${lodge.direct_link}" target="_blank" rel="noopener noreferrer" class="btn btn-book">
          Open Booking Page ↗
        </a>
        <button type="button" class="btn-calc-lodge" onclick="openTripCalculator('${escapeJs(lodge.id)}')">
          💰 Calculate Trip Total
        </button>
      </div>
    </article>
  `;
}

// Custom Scrape Execution Handler
async function triggerScrape() {
  const checkin = document.getElementById("scrape-checkin").value;
  const checkout = document.getElementById("scrape-checkout").value;
  const adults = parseInt(document.getElementById("scrape-adults").value, 10) || 5;
  const rooms = parseInt(document.getElementById("scrape-rooms").value, 10) || 1;

  modalScrape.classList.add("hidden");

  btnRunScrape.disabled = true;
  scrapeBtnText.textContent = "Scanning Engines...";
  scrapeIcon.classList.add("spinning");

  try {
    const res = await fetch("/api/scrape", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ checkin, checkout, adults, rooms })
    });

    const data = await res.json();
    console.log("Scrape triggered response:", data);

    // Poll or re-fetch after brief execution
    setTimeout(async () => {
      await fetchStats();
      await fetchLodges();
      btnRunScrape.disabled = false;
      scrapeBtnText.textContent = "Run Live Scrape";
      scrapeIcon.classList.remove("spinning");
    }, 4000);
  } catch (err) {
    console.error("Error triggering scrape:", err);
    btnRunScrape.disabled = false;
    scrapeBtnText.textContent = "Run Live Scrape";
    scrapeIcon.classList.remove("spinning");
  }
}

/* ==========================================================================
   Total Trip Budget & Cost Calculator Engine (5 Guests • 4 Nights)
   ========================================================================== */

let calcCurrency = "JPY"; // "JPY", "USD", "SGD"
let calcGearTier = "standard"; // "standard", "powder", "none"
let calcFoodTier = "izakaya"; // "budget", "izakaya", "gourmet"
let calcTransportMode = "van"; // "van", "shinkansen", "bus"
let cachedTripTotals = {
  lodgeCost: 167670,
  lodgePerPax: 33534,
  liftCost: 130000,
  liftPerPax: 26000,
  gearCost: 100000,
  gearPerPax: 20000,
  transCost: 75000,
  transPerPax: 15000,
  foodCost: 130000,
  foodPerPax: 26000,
  groupTotal: 602670,
  totalPax: 120534,
  transLabel: "5-Pax 4WD Van + Tolls & Fuel",
  foodLabel: "Standard Izakaya (¥6,500/d)"
};

// Rates Constants
const CONVERSION_RATES = {
  JPY: 1,
  USD: 1 / 150,
  SGD: 1 / 112
};

function formatCurrency(amountJpy, targetCurrency = calcCurrency) {
  if (targetCurrency === "USD") {
    const usd = Math.round(amountJpy * CONVERSION_RATES.USD);
    return `$${usd.toLocaleString()}`;
  } else if (targetCurrency === "SGD") {
    const sgd = Math.round(amountJpy * CONVERSION_RATES.SGD);
    return `S$${sgd.toLocaleString()}`;
  }
  return `¥${Math.round(amountJpy).toLocaleString()}`;
}

function setupCalculatorEventListeners() {
  if (btnOpenTripCalc) {
    btnOpenTripCalc.addEventListener("click", () => openTripCalculator());
  }

  if (btnCloseCalcModal) {
    btnCloseCalcModal.addEventListener("click", closeTripCalculator);
  }

  if (modalCalculator) {
    modalCalculator.addEventListener("click", (e) => {
      if (e.target === modalCalculator) {
        closeTripCalculator();
      }
    });
  }

  // Currency switcher
  const currencyBtns = document.querySelectorAll(".currency-btn");
  currencyBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      currencyBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      calcCurrency = btn.dataset.currency || "JPY";
      calculateTotalTripCost();
    });
  });

  // Lodge select
  const calcLodgeSelect = document.getElementById("calc-lodge-select");
  if (calcLodgeSelect) {
    calcLodgeSelect.addEventListener("change", onCalcLodgeChange);
  }

  // Lodge cost manual input
  const calcLodgeCost = document.getElementById("calc-lodge-cost");
  if (calcLodgeCost) {
    calcLodgeCost.addEventListener("input", () => calculateTotalTripCost());
  }

  // Lift Days & Skiers count
  const calcLiftDays = document.getElementById("calc-lift-days");
  const calcSkiersCount = document.getElementById("calc-skiers-count");
  const calcNightSkiToggle = document.getElementById("calc-night-ski-toggle");

  if (calcLiftDays) calcLiftDays.addEventListener("change", () => calculateTotalTripCost());
  if (calcSkiersCount) calcSkiersCount.addEventListener("change", () => calculateTotalTripCost());
  if (calcNightSkiToggle) calcNightSkiToggle.addEventListener("change", () => calculateTotalTripCost());

  // Gear Tier Buttons
  const calcTierBtns = document.querySelectorAll(".calc-tier-btn");
  calcTierBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      calcTierBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      calcGearTier = btn.dataset.gearTier || "standard";
      calculateTotalTripCost();
    });
  });

  // Gear & Wear Pax Selects
  const calcGearPax = document.getElementById("calc-gear-pax");
  const calcWearPax = document.getElementById("calc-wear-pax");
  if (calcGearPax) calcGearPax.addEventListener("change", () => calculateTotalTripCost());
  if (calcWearPax) calcWearPax.addEventListener("change", () => calculateTotalTripCost());

  // Transport Radio options
  const transportPills = document.querySelectorAll(".calc-transport-pill");
  const transportRadios = document.querySelectorAll('input[name="calc-transport"]');
  transportRadios.forEach((radio) => {
    radio.addEventListener("change", (e) => {
      calcTransportMode = e.target.value;
      transportPills.forEach((p) => {
        const input = p.querySelector('input[type="radio"]');
        p.classList.toggle("active", input && input.checked);
      });
      calculateTotalTripCost();
    });
  });

  // Food Tier Buttons
  const calcFoodBtns = document.querySelectorAll(".calc-food-btn");
  calcFoodBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      calcFoodBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      calcFoodTier = btn.dataset.foodTier || "izakaya";
      calculateTotalTripCost();
    });
  });

  // WhatsApp / Clipboard summary button
  const btnCopyChatSummary = document.getElementById("btn-copy-chat-summary");
  if (btnCopyChatSummary) {
    btnCopyChatSummary.addEventListener("click", copyChatSummary);
  }
}

function populateCalcLodgeSelect() {
  const calcLodgeSelect = document.getElementById("calc-lodge-select");
  if (!calcLodgeSelect) return;

  if (allLodges.length === 0) return;

  const currentVal = calcLodgeSelect.value;
  let optionsHtml = `<option value="custom">-- Custom Accommodation Rate (Custom ¥) --</option>`;

  optionsHtml += allLodges.map((lodge) => {
    const priceText = lodge.price_display || "Contact";
    return `<option value="${lodge.id}">${lodge.resort}: ${lodge.name} (${lodge.name_en || ''}) - ${priceText}</option>`;
  }).join("");

  calcLodgeSelect.innerHTML = optionsHtml;

  if (currentVal && calcLodgeSelect.querySelector(`option[value="${currentVal}"]`)) {
    calcLodgeSelect.value = currentVal;
  } else {
    // Default to the first lodge with confirmed pricing (or Ryokan Azumaya)
    const preferred = allLodges.find((l) => l.price_per_person_night && parseInt(l.price_per_person_night, 10) > 0) || allLodges[0];
    if (preferred) {
      calcLodgeSelect.value = preferred.id;
      applyLodgeToCalculator(preferred);
    }
  }

  calculateTotalTripCost();
}

function onCalcLodgeChange(e) {
  const selectedId = e.target.value;
  if (selectedId === "custom") {
    const calcResortSub = document.getElementById("calc-resort-name-sub");
    if (calcResortSub) calcResortSub.textContent = "Custom Mountain Rates";
    calculateTotalTripCost();
    return;
  }

  const lodge = allLodges.find((l) => l.id === selectedId);
  if (lodge) {
    applyLodgeToCalculator(lodge);
  }
  calculateTotalTripCost();
}

function applyLodgeToCalculator(lodge) {
  const calcLodgeCost = document.getElementById("calc-lodge-cost");
  const calcResortSub = document.getElementById("calc-resort-name-sub");

  if (!lodge) return;

  let totalEst = 167670;
  if (lodge.price_per_person_night && parseInt(lodge.price_per_person_night, 10) > 0) {
    // 5 persons * 4 nights
    totalEst = parseInt(lodge.price_per_person_night, 10) * 5 * 4;
  } else if (lodge.group_total_est) {
    const parsed = parseInt(lodge.group_total_est.replace(/[^0-9]/g, ""), 10);
    if (!isNaN(parsed) && parsed > 0) totalEst = parsed;
  }

  if (calcLodgeCost) {
    calcLodgeCost.value = totalEst;
  }

  if (calcResortSub) {
    calcResortSub.textContent = `Synced with ${lodge.resort}`;
  }
}

function openTripCalculator(lodgeId = null) {
  if (allLodges.length > 0) {
    populateCalcLodgeSelect();
  }

  const calcLodgeSelect = document.getElementById("calc-lodge-select");

  if (lodgeId) {
    const targetLodge = allLodges.find((l) => l.id === lodgeId);
    if (targetLodge && calcLodgeSelect) {
      calcLodgeSelect.value = targetLodge.id;
      applyLodgeToCalculator(targetLodge);
    }
  }

  calculateTotalTripCost();

  if (modalCalculator) {
    modalCalculator.classList.remove("hidden");
  }
}

function closeTripCalculator() {
  if (modalCalculator) {
    modalCalculator.classList.add("hidden");
  }
}

function calculateTotalTripCost() {
  const calcLodgeSelect = document.getElementById("calc-lodge-select");
  const calcLodgeCost = document.getElementById("calc-lodge-cost");
  const calcLodgeRateTag = document.getElementById("calc-lodge-rate-tag");

  const calcLiftDays = document.getElementById("calc-lift-days");
  const calcSkiersCount = document.getElementById("calc-skiers-count");
  const calcNightSkiToggle = document.getElementById("calc-night-ski-toggle");

  const calcGearPax = document.getElementById("calc-gear-pax");
  const calcWearPax = document.getElementById("calc-wear-pax");

  // 1. Accommodation
  const lodgeTotal = parseInt(calcLodgeCost?.value, 10) || 0;
  const perPersonPerNight = Math.round(lodgeTotal / 5 / 4);
  if (calcLodgeRateTag) {
    calcLodgeRateTag.textContent = `~¥${perPersonPerNight.toLocaleString()} / person / night`;
  }

  const selectedLodgeId = calcLodgeSelect ? calcLodgeSelect.value : "";
  const selectedLodge = allLodges.find((l) => l.id === selectedLodgeId);
  const lodgeName = selectedLodge ? selectedLodge.name : (selectedLodgeId === "custom" ? "Custom Ryokan" : "Selected Accommodation");

  // 2. Mountain Lift Passes
  const liftDays = parseInt(calcLiftDays?.value, 10) ?? 4;
  const skiers = parseInt(calcSkiersCount?.value, 10) ?? 5;
  const hasNightSki = calcNightSkiToggle ? calcNightSkiToggle.checked : false;

  // Resolve Resort Lift Pass Base Rate
  let fourDayPassVal = 26000;
  let oneDayPassVal = 7300;
  if (selectedLodge && resortsData) {
    const matchKey = Object.keys(resortsData).find((k) =>
      selectedLodge.resort.toLowerCase().includes(k.toLowerCase()) ||
      k.toLowerCase().includes(selectedLodge.resort.toLowerCase())
    );
    if (matchKey && resortsData[matchKey].lift_passes) {
      const lp = resortsData[matchKey].lift_passes;
      if (lp.four_day_val) fourDayPassVal = lp.four_day_val;
      if (lp.one_day_val) oneDayPassVal = lp.one_day_val;
    }
  }

  let passPerSkier = 0;
  if (liftDays === 4) {
    passPerSkier = fourDayPassVal;
  } else if (liftDays === 3) {
    passPerSkier = Math.round(fourDayPassVal * 0.77);
  } else if (liftDays === 2) {
    passPerSkier = Math.round(oneDayPassVal * 1.85);
  } else if (liftDays === 1) {
    passPerSkier = oneDayPassVal;
  } else {
    passPerSkier = 0;
  }

  const nightSkiCost = hasNightSki ? 2500 * skiers : 0;
  const liftTotal = (passPerSkier * skiers) + nightSkiCost;

  // 3. Gear & Outerwear Rentals
  let gearDailyRate = 5000;
  let gearTierLabel = "Standard Carving Set";
  if (calcGearTier === "powder") {
    gearDailyRate = 7000;
    gearTierLabel = "Powder Demo Fleet";
  } else if (calcGearTier === "none") {
    gearDailyRate = 0;
    gearTierLabel = "Bring Own Gear";
  }

  const gearPax = parseInt(calcGearPax?.value, 10) ?? 5;
  const wearPax = parseInt(calcWearPax?.value, 10) ?? 0;
  const wearDailyRate = 3500;

  const rentalTotal = (gearDailyRate * liftDays * gearPax) + (wearDailyRate * liftDays * wearPax);

  // 4. Tokyo Roundtrip Transportation
  let transTotal = 75000;
  let transLabel = "🚐 5-Pax 4WD Van + Tolls & Fuel";
  if (calcTransportMode === "shinkansen") {
    transTotal = 85000; // ~17,000 * 5
    transLabel = "🚅 Shinkansen Bullet Train (5 Pax)";
  } else if (calcTransportMode === "bus") {
    transTotal = 50000; // ~10,000 * 5
    transLabel = "🚌 Direct Ski Highway Bus (5 Pax)";
  }

  // 5. Dining, Food & Village Onsens (4 Days x 5 Pax)
  let foodDailyRatePerPerson = 6500;
  let foodLabel = "Standard Izakaya (¥6,500/d)";
  if (calcFoodTier === "budget") {
    foodDailyRatePerPerson = 3500;
    foodLabel = "Budget / Casual (¥3,500/d)";
  } else if (calcFoodTier === "gourmet") {
    foodDailyRatePerPerson = 12000;
    foodLabel = "Gourmet Feast (¥12,000/d)";
  }

  const foodTotal = foodDailyRatePerPerson * 4 * 5;

  // Grand Totals
  const groupTotal = lodgeTotal + liftTotal + rentalTotal + transTotal + foodTotal;
  const perPersonTotal = Math.round(groupTotal / 5);

  cachedTripTotals = {
    lodgeCost: lodgeTotal,
    lodgePerPax: Math.round(lodgeTotal / 5),
    liftCost: liftTotal,
    liftPerPax: Math.round(liftTotal / 5),
    gearCost: rentalTotal,
    gearPerPax: Math.round(rentalTotal / 5),
    transCost: transTotal,
    transPerPax: Math.round(transTotal / 5),
    foodCost: foodTotal,
    foodPerPax: Math.round(foodTotal / 5),
    groupTotal: groupTotal,
    totalPax: perPersonTotal,
    transLabel: transLabel,
    foodLabel: foodLabel
  };

  // Update Main Receipt Callouts
  const receiptPerPerson = document.getElementById("receipt-per-person");
  const receiptPerPersonAlt = document.getElementById("receipt-per-person-alt");
  const receiptGroupTotal = document.getElementById("receipt-group-total");
  const receiptGroupTotalAlt = document.getElementById("receipt-group-total-alt");

  if (receiptPerPerson) receiptPerPerson.textContent = formatCurrency(perPersonTotal, calcCurrency);
  if (receiptGroupTotal) receiptGroupTotal.textContent = formatCurrency(groupTotal, calcCurrency);

  // Secondary Currency Callouts
  if (calcCurrency === "JPY") {
    if (receiptPerPersonAlt) receiptPerPersonAlt.textContent = `~${formatCurrency(perPersonTotal, "USD")} USD`;
    if (receiptGroupTotalAlt) receiptGroupTotalAlt.textContent = `~${formatCurrency(groupTotal, "USD")} USD Total`;
  } else if (calcCurrency === "USD") {
    if (receiptPerPersonAlt) receiptPerPersonAlt.textContent = `~${formatCurrency(perPersonTotal, "JPY")} JPY`;
    if (receiptGroupTotalAlt) receiptGroupTotalAlt.textContent = `~${formatCurrency(groupTotal, "JPY")} JPY Total`;
  } else {
    // SGD
    if (receiptPerPersonAlt) receiptPerPersonAlt.textContent = `~${formatCurrency(perPersonTotal, "JPY")} JPY`;
    if (receiptGroupTotalAlt) receiptGroupTotalAlt.textContent = `~${formatCurrency(groupTotal, "JPY")} JPY Total`;
  }

  // Update Expense Distribution Bar
  const barSegLodge = document.getElementById("bar-seg-lodge");
  const barSegLift = document.getElementById("bar-seg-lift");
  const barSegRental = document.getElementById("bar-seg-rental");
  const barSegTrans = document.getElementById("bar-seg-trans");
  const barSegFood = document.getElementById("bar-seg-food");
  const receiptBreakdownSummary = document.getElementById("receipt-breakdown-summary");

  if (groupTotal > 0) {
    const pctLodge = Math.round((lodgeTotal / groupTotal) * 100);
    const pctLift = Math.round((liftTotal / groupTotal) * 100);
    const pctRental = Math.round((rentalTotal / groupTotal) * 100);
    const pctTrans = Math.round((transTotal / groupTotal) * 100);
    const pctFood = Math.max(0, 100 - (pctLodge + pctLift + pctRental + pctTrans));

    if (barSegLodge) barSegLodge.style.width = `${pctLodge}%`;
    if (barSegLift) barSegLift.style.width = `${pctLift}%`;
    if (barSegRental) barSegRental.style.width = `${pctRental}%`;
    if (barSegTrans) barSegTrans.style.width = `${pctTrans}%`;
    if (barSegFood) barSegFood.style.width = `${pctFood}%`;

    if (receiptBreakdownSummary) {
      receiptBreakdownSummary.textContent = `Lodging ${pctLodge}% • Lifts ${pctLift}% • Gear ${pctRental}% • Trans ${pctTrans}% • Food ${pctFood}%`;
    }
  }

  // Update Line Items Table
  // 1. Lodge
  const itemLodgeSub = document.getElementById("receipt-item-lodge-sub");
  const lodgeGroup = document.getElementById("receipt-lodge-group");
  const lodgePax = document.getElementById("receipt-lodge-pax");
  if (itemLodgeSub) itemLodgeSub.textContent = `${lodgeName} (5 Guests • 4 Nights)`;
  if (lodgeGroup) lodgeGroup.textContent = formatCurrency(lodgeTotal, calcCurrency);
  if (lodgePax) lodgePax.textContent = `${formatCurrency(Math.round(lodgeTotal / 5), calcCurrency)} /pax`;

  // 2. Lifts
  const itemLiftSub = document.getElementById("receipt-item-lift-sub");
  const liftGroup = document.getElementById("receipt-lift-group");
  const liftPax = document.getElementById("receipt-lift-pax");
  const nightSkiText = hasNightSki ? " + Night Ski" : "";
  if (itemLiftSub) itemLiftSub.textContent = `${liftDays}-Day Mountain Pass (${skiers} Skiers${nightSkiText})`;
  if (liftGroup) liftGroup.textContent = formatCurrency(liftTotal, calcCurrency);
  if (liftPax) liftPax.textContent = `${formatCurrency(Math.round(liftTotal / 5), calcCurrency)} /pax`;

  // 3. Gear Rentals
  const itemRentalSub = document.getElementById("receipt-item-rental-sub");
  const rentalGroup = document.getElementById("receipt-rental-group");
  const rentalPax = document.getElementById("receipt-rental-pax");
  if (itemRentalSub) itemRentalSub.textContent = `${gearTierLabel} (${gearPax} Sets • ${wearPax} Outerwear • ${liftDays}d)`;
  if (rentalGroup) rentalGroup.textContent = formatCurrency(rentalTotal, calcCurrency);
  if (rentalPax) rentalPax.textContent = `${formatCurrency(Math.round(rentalTotal / 5), calcCurrency)} /pax`;

  // 4. Transportation
  const itemTransSub = document.getElementById("receipt-item-trans-sub");
  const transGroup = document.getElementById("receipt-trans-group");
  const transPax = document.getElementById("receipt-trans-pax");
  if (itemTransSub) itemTransSub.textContent = transLabel;
  if (transGroup) transGroup.textContent = formatCurrency(transTotal, calcCurrency);
  if (transPax) transPax.textContent = `${formatCurrency(Math.round(transTotal / 5), calcCurrency)} /pax`;

  // 5. Food & Onsens
  const itemFoodSub = document.getElementById("receipt-item-food-sub");
  const foodGroup = document.getElementById("receipt-food-group");
  const foodPax = document.getElementById("receipt-food-pax");
  if (itemFoodSub) itemFoodSub.textContent = `${foodLabel} (4d × 5p)`;
  if (foodGroup) foodGroup.textContent = formatCurrency(foodTotal, calcCurrency);
  if (foodPax) foodPax.textContent = `${formatCurrency(Math.round(foodTotal / 5), calcCurrency)} /pax`;
}

function copyChatSummary() {
  const calcLodgeSelect = document.getElementById("calc-lodge-select");
  const calcLiftDays = document.getElementById("calc-lift-days");
  const calcSkiersCount = document.getElementById("calc-skiers-count");
  const calcGearPax = document.getElementById("calc-gear-pax");
  const calcWearPax = document.getElementById("calc-wear-pax");

  const lodgeName = calcLodgeSelect && calcLodgeSelect.selectedIndex >= 0
    ? calcLodgeSelect.options[calcLodgeSelect.selectedIndex].text
    : "Nagano Alpine Ryokan";

  const groupTotalStr = formatCurrency(cachedTripTotals.groupTotal, calcCurrency);
  const paxTotalStr = formatCurrency(cachedTripTotals.totalPax, calcCurrency);
  const altCurrency = calcCurrency === "JPY" ? "USD" : "JPY";
  const altGroupTotalStr = formatCurrency(cachedTripTotals.groupTotal, altCurrency);
  const altPaxTotalStr = formatCurrency(cachedTripTotals.totalPax, altCurrency);

  const summary = `🎿 JAPAN POWDER TRIP 2026/2027 — TOTAL COST BREAKDOWN
👥 Group: 5 Adults | 📅 Dec 29, 2026 – Jan 2, 2027 (4 Nights)
🏨 Base: ${lodgeName}

💰 GROUP TOTAL (5 Pax): ${groupTotalStr} (~${altGroupTotalStr})
👤 PER PERSON SHARE:    ${paxTotalStr} (~${altPaxTotalStr})

━━━━━━━━━━━━━━━━━━━━━━━━━━
🏨 1. Lodging (4 Nights):  ${formatCurrency(cachedTripTotals.lodgeCost, calcCurrency)} (~${formatCurrency(cachedTripTotals.lodgePerPax, calcCurrency)}/pax)
🚡 2. Ski Lift Passes:     ${formatCurrency(cachedTripTotals.liftCost, calcCurrency)} (${calcLiftDays?.value || 4} Days • ${calcSkiersCount?.value || 5} Skiers)
🎿 3. Gear & Outerwear:    ${formatCurrency(cachedTripTotals.gearCost, calcCurrency)} (${calcGearPax?.value || 5} Gear Sets • ${calcWearPax?.value || 0} Outerwear)
🚅 4. Tokyo Transport:     ${formatCurrency(cachedTripTotals.transCost, calcCurrency)} (${cachedTripTotals.transLabel})
🍱 5. Food, Drinks & Onsen: ${formatCurrency(cachedTripTotals.foodCost, calcCurrency)} (${cachedTripTotals.foodLabel})
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 Live Radar & Availability: https://japan-ski-radar.vercel.app`;

  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(summary)
      .then(showCopiedFeedback)
      .catch(() => fallbackClipboardCopy(summary));
  } else {
    fallbackClipboardCopy(summary);
  }
}

function fallbackClipboardCopy(text) {
  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.left = "-999999px";
  textArea.style.top = "-999999px";
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  try {
    document.execCommand("copy");
    showCopiedFeedback();
  } catch (err) {
    console.error("Fallback copy failed:", err);
  }
  document.body.removeChild(textArea);
}

function showCopiedFeedback() {
  const copyBtnText = document.getElementById("copy-btn-text");
  const btn = document.getElementById("btn-copy-chat-summary");
  if (!copyBtnText) return;

  const originalText = copyBtnText.textContent;
  copyBtnText.textContent = "✅ Copied to Clipboard! Ready for WhatsApp/Telegram";
  if (btn) btn.style.background = "linear-gradient(135deg, #059669 0%, #047857 100%)";

  setTimeout(() => {
    copyBtnText.textContent = originalText;
    if (btn) btn.style.background = "";
  }, 2500);
}

// Expose globally for inline button handlers
window.openTripCalculator = openTripCalculator;
window.closeTripCalculator = closeTripCalculator;
