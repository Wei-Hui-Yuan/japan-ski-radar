/**
 * Nagano Powder Radar - Frontend Application Logic
 */

let allLodges = [];
let currentResortFilter = "all";
let currentStatusFilter = "all";
let currentSearchQuery = "";

// DOM Elements
const lodgesGrid = document.getElementById("lodges-grid");
const inputSearch = document.getElementById("input-search");
const btnClearSearch = document.getElementById("btn-clear-search");
const selectStatus = document.getElementById("select-status-filter");
const selectSort = document.getElementById("select-sort-filter");
const resortChips = document.querySelectorAll(".filter-chip");
const statCards = document.querySelectorAll(".stat-card");

let currentSortOrder = "priority";

const btnRunScrape = document.getElementById("btn-run-scrape");
const scrapeBtnText = document.getElementById("scrape-btn-text");
const scrapeIcon = document.getElementById("scrape-icon");
const btnExportCsv = document.getElementById("btn-export-csv");

const modalScrape = document.getElementById("modal-scrape");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnCancelModal = document.getElementById("btn-cancel-modal");
const btnStartScrape = document.getElementById("btn-start-scrape");

// Stat elements
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
  setupEventListeners();
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

  // Open Live Scrape Modal
  btnRunScrape.addEventListener("click", () => {
    modalScrape.classList.remove("hidden");
  });

  btnCloseModal.addEventListener("click", () => modalScrape.classList.add("hidden"));
  btnCancelModal.addEventListener("click", () => modalScrape.classList.add("hidden"));

  // Start Scrape
  btnStartScrape.addEventListener("click", async () => {
    modalScrape.classList.add("hidden");
    const checkin = document.getElementById("scrape-checkin").value;
    const checkout = document.getElementById("scrape-checkout").value;
    const adults = parseInt(document.getElementById("scrape-adults").value, 10);
    const rooms = parseInt(document.getElementById("scrape-rooms").value, 10);

    setScrapingState(true);
    try {
      const res = await fetch("/api/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ checkin, checkout, adults, rooms }),
      });
      const data = await res.json();
      console.log("Scrape result:", data);
      await fetchStats();
      await fetchLodges();
    } catch (err) {
      console.error("Scrape error:", err);
      alert("Failed to complete scrape: " + err.message);
    } finally {
      setScrapingState(false);
    }
  });
}

function updateActiveStatCard(filter) {
  statCards.forEach((card) => {
    if (card.dataset.filter === filter) {
      card.classList.add("active-stat");
    } else {
      card.classList.remove("active-stat");
    }
  });
}

function setScrapingState(isScraping) {
  if (isScraping) {
    btnRunScrape.disabled = true;
    scrapeBtnText.textContent = "Scanning Systems...";
    scrapeIcon.style.animation = "spin 1s linear infinite";
    lodgesGrid.innerHTML = `
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Probing live 489ban & DirectIn endpoints across Nozawa, Hakuba & Madarao...</p>
      </div>
    `;
  } else {
    btnRunScrape.disabled = false;
    scrapeBtnText.textContent = "Run Live Scrape";
    scrapeIcon.style.animation = "none";
  }
}

async function fetchStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();
    statTotal.textContent = data.total_monitored || 0;
    statAvailable.textContent = data.available_now || 0;
    statUnlocking.textContent = data.unlocking_oct_1 || 0;
    statPartial.textContent = data.partial_open || 0;
    statInquiry.textContent = data.direct_inquiry || 0;
    displayUpdated.textContent = data.last_scraped_at ? data.last_scraped_at.split(" ")[1] : "Just now";
  } catch (err) {
    console.error("Error fetching stats:", err);
  }
}

async function fetchLodges() {
  try {
    const res = await fetch("/api/lodges");
    const json = await res.json();
    allLodges = json.data || [];
    renderLodges();
  } catch (err) {
    console.error("Error fetching lodges:", err);
    lodgesGrid.innerHTML = `
      <div class="empty-state">
        <p>⚠️ Failed to load lodge data from server.</p>
      </div>
    `;
  }
}

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
        (lodge.price_display && lodge.price_display.toLowerCase().includes(currentSearchQuery));
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

        <div class="card-notes">
          "${lodge.notes}"
        </div>
      </div>

      <div class="card-actions">
        ${phoneBtn}
        <a href="${lodge.direct_link}" target="_blank" rel="noopener noreferrer" class="btn btn-book">
          Open Booking Page ↗
        </a>
      </div>
    </article>
  `;
}
