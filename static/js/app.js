/* SkyGlass Weather front-end logic */

let state = {
  raw: null, // original metric data from API
  unit: "metric", // "metric" or "imperial"
  chart: null,
};

const elements = {};

function selectElements() {
  elements.cityInput = document.getElementById("cityInput");
  elements.searchBtn = document.getElementById("searchBtn");
  elements.geoBtn = document.getElementById("geoBtn");
  elements.errorAlert = document.getElementById("errorAlert");
  elements.unitToggle = document.getElementById("unitToggle");
  elements.unitLabel = document.getElementById("unitLabel");
  elements.themeToggle = document.getElementById("themeToggle");
  elements.loadingOverlay = document.getElementById("loadingOverlay");

  elements.currentCity = document.getElementById("currentCity");
  elements.currentMeta = document.getElementById("currentMeta");
  elements.currentIcon = document.getElementById("currentIcon");
  elements.currentTemp = document.getElementById("currentTemp");
  elements.currentDescription = document.getElementById("currentDescription");
  elements.feelsLike = document.getElementById("feelsLike");
  elements.humidity = document.getElementById("humidity");
  elements.wind = document.getElementById("wind");
  elements.pressure = document.getElementById("pressure");
  elements.sunTimes = document.getElementById("sunTimes");
  elements.updatedAt = document.getElementById("updatedAt");

  elements.forecastList = document.getElementById("forecastList");
  elements.trendChart = document.getElementById("trendChart");
}

function init() {
  selectElements();
  attachEventListeners();
  restorePreferences();

  // Try geolocation first, otherwise wait for manual search
  if (navigator.geolocation) {
    showLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        fetchWeather({ lat: pos.coords.latitude, lon: pos.coords.longitude });
      },
      () => {
        showLoading(false);
        // Leave UI idle, user can search manually
      },
      { timeout: 8000 }
    );
  }
}

function attachEventListeners() {
  elements.searchBtn.addEventListener("click", async () => {
    const city = (elements.cityInput.value || "").trim();
    if (!city) {
      showError("Type a city name to search.");
      return;
    }

    const originalContent = elements.searchBtn.innerHTML;
    elements.searchBtn.disabled = true;
    elements.searchBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Searching...';

    await fetchWeather({ city }, { showOverlay: false });

    elements.searchBtn.disabled = false;
    elements.searchBtn.innerHTML = originalContent;
  });

  elements.cityInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      elements.searchBtn.click();
    }
  });

  elements.geoBtn.addEventListener("click", () => {
    if (!navigator.geolocation) {
      showError("Geolocation is not supported in this browser.");
      return;
    }
    showLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        fetchWeather({ lat: pos.coords.latitude, lon: pos.coords.longitude });
      },
      (err) => {
        showLoading(false);
        if (err.code === err.PERMISSION_DENIED) {
          showError("Location permission denied. You can still search by city.");
        } else {
          showError("Unable to detect your location. Please search by city.");
        }
      },
      { timeout: 8000 }
    );
  });

  elements.unitToggle.addEventListener("change", () => {
    state.unit = elements.unitToggle.checked ? "imperial" : "metric";
    elements.unitLabel.textContent = state.unit === "metric" ? "°C" : "°F";
    if (state.raw) {
      renderAll();
      savePreferences();
    }
  });

  elements.themeToggle.addEventListener("change", () => {
    const mode = elements.themeToggle.checked ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", mode);
    document.body.setAttribute("data-theme", mode);
    savePreferences();
  });
}

function showLoading(isLoading) {
  if (!elements.loadingOverlay) return;
  elements.loadingOverlay.classList.toggle("d-none", !isLoading);
}

function showError(message) {
  if (!elements.errorAlert) return;
  elements.errorAlert.textContent = message;
  elements.errorAlert.classList.remove("d-none");
  setTimeout(() => {
    elements.errorAlert.classList.add("d-none");
  }, 4000);
}

async function fetchWeather({ city, lat, lon }, { showOverlay = true } = {}) {
  try {
    if (showOverlay) showLoading(true);
    elements.errorAlert?.classList.add("d-none");

    const params = new URLSearchParams();
    if (city) params.append("city", city);
    if (lat != null && lon != null) {
      params.append("lat", lat);
      params.append("lon", lon);
    }

    const response = await fetch(`/api/weather?${params.toString()}`);
    const data = await response.json();

    if (!response.ok) {
      showError(data.error || "Weather service error.");
      return;
    }

    state.raw = data;
    renderAll();
  } catch (err) {
    console.error(err);
    showError("Network error. Please check your connection and try again.");
  } finally {
    if (showOverlay) showLoading(false);
  }
}

function renderAll() {
  if (!state.raw) return;
  renderCurrentWeather();
  renderForecast();
  renderChart();
  applyTheme();
}

function toUnitCelsius(valC) {
  if (valC == null) return "--";
  return Math.round(valC);
}

function toUnitTemperature(valC) {
  if (valC == null) return "--";
  if (state.unit === "metric") return Math.round(valC);
  return Math.round((valC * 9) / 5 + 32);
}

function toUnitWind(speedMs) {
  if (speedMs == null) return "--";
  if (state.unit === "metric") {
    return Math.round(speedMs * 3.6); // m/s -> km/h
  }
  return Math.round(speedMs * 2.237); // m/s -> mph
}

function renderCurrentWeather() {
  const { location, current } = state.raw;
  const unitSymbol = state.unit === "metric" ? "°C" : "°F";

  elements.currentCity.textContent = `${location.city || "Unknown city"}, ${location.country || ""}`;

  const localTime = current.datetime ? new Date(current.datetime) : null;
  const dateStr = localTime
    ? localTime.toLocaleString(undefined, {
        weekday: "short",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";
  elements.currentMeta.textContent = dateStr;

  elements.currentTemp.textContent = toUnitTemperature(current.temp_c);
  elements.currentDescription.textContent = current.description || "--";
  elements.feelsLike.textContent = `Feels like ${toUnitTemperature(current.feels_like_c)} ${unitSymbol}`;

  elements.humidity.textContent = current.humidity != null ? `${current.humidity} %` : "--";
  elements.wind.textContent = `${toUnitWind(current.wind_speed_ms)} ${
    state.unit === "metric" ? "km/h" : "mph"
  }`;
  elements.pressure.textContent = current.pressure != null ? `${current.pressure} hPa` : "--";

  const sunrise = current.sunrise ? new Date(current.sunrise) : null;
  const sunset = current.sunset ? new Date(current.sunset) : null;
  if (sunrise && sunset) {
    const sunriseStr = sunrise.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
    const sunsetStr = sunset.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
    elements.sunTimes.textContent = `${sunriseStr} / ${sunsetStr}`;
  } else {
    elements.sunTimes.textContent = "--";
  }

  elements.updatedAt.textContent = `Updated just now`;

  const iconClass = mapIconToClass(current.icon, state.raw.meta.is_day);
  elements.currentIcon.className = `wi ${iconClass}`;
}

function renderForecast() {
  const list = state.raw.forecast_daily || [];
  elements.forecastList.innerHTML = "";

  if (!list.length) {
    elements.forecastList.innerHTML = '<div class="text-soft small">No forecast data.</div>';
    return;
  }

  const unitSymbol = state.unit === "metric" ? "°C" : "°F";

  list.forEach((day) => {
    const tempMin = toUnitTemperature(day.temp_min_c);
    const tempMax = toUnitTemperature(day.temp_max_c);
    const humidity = day.humidity_avg != null ? `${Math.round(day.humidity_avg)} %` : "--";

    const iconClass = mapIconToClass(day.icon, true);
    const card = document.createElement("div");
    card.className = "forecast-card d-flex flex-column align-items-center text-center";
    card.innerHTML = `
      <div class="small text-soft mb-1">${day.label}</div>
      <i class="wi ${iconClass} forecast-icon mb-1"></i>
      <div class="fw-semibold small mb-1">${day.description}</div>
      <div class="fw-bold">${tempMax}${unitSymbol}</div>
      <div class="text-soft small">Low ${tempMin}${unitSymbol}</div>
      <div class="text-soft small mt-1">Hum. ${humidity}</div>
    `;
    elements.forecastList.appendChild(card);
  });
}

function renderChart() {
  const { chart } = state.raw;
  if (!chart || !elements.trendChart) return;

  const labels = chart.labels;
  const temps = chart.temperature_c.map((v) => (state.unit === "metric" ? v : (v * 9) / 5 + 32));
  const humidity = chart.humidity;

  const ctx = elements.trendChart.getContext("2d");

  if (state.chart) {
    state.chart.data.labels = labels;
    state.chart.data.datasets[0].data = temps;
    state.chart.data.datasets[1].data = humidity;
    state.chart.options.scales.y.temperature.title.text = state.unit === "metric" ? "Temperature (°C)" : "Temperature (°F)";
    state.chart.update();
    return;
  }

  state.chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Temperature",
          data: temps,
          yAxisID: "temperature",
          borderColor: "rgba(249, 115, 22, 0.95)",
          backgroundColor: "rgba(249, 115, 22, 0.15)",
          tension: 0.35,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: "Humidity",
          data: humidity,
          yAxisID: "humidity",
          borderColor: "rgba(56, 189, 248, 0.95)",
          backgroundColor: "rgba(56, 189, 248, 0.15)",
          tension: 0.35,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false,
      },
      plugins: {
        legend: {
          labels: {
            color: getComputedStyle(document.body).getPropertyValue("--text-soft") || "#cbd5f5",
          },
        },
      },
      scales: {
        temperature: {
          type: "linear",
          position: "left",
          title: {
            display: true,
            text: state.unit === "metric" ? "Temperature (°C)" : "Temperature (°F)",
          },
          grid: {
            color: "rgba(148, 163, 184, 0.25)",
          },
          ticks: {
            color: "rgba(226, 232, 240, 0.9)",
          },
        },
        humidity: {
          type: "linear",
          position: "right",
          title: {
            display: true,
            text: "Humidity (%)",
          },
          grid: {
            drawOnChartArea: false,
          },
          ticks: {
            color: "rgba(148, 163, 184, 0.9)",
          },
        },
        x: {
          grid: {
            color: "rgba(148, 163, 184, 0.1)",
          },
          ticks: {
            color: "rgba(148, 163, 184, 0.9)",
          },
        },
      },
    },
  });
}

function mapIconToClass(iconCode, isDay) {
  if (!iconCode) {
    return isDay ? "wi-day-sunny" : "wi-night-clear";
  }

  const code = iconCode.slice(0, 2); // e.g. "01", "02"...
  const dayPrefix = isDay ? "day" : "night-alt";

  switch (code) {
    case "01":
      return isDay ? "wi-day-sunny" : "wi-night-clear";
    case "02":
      return `wi-${dayPrefix}-cloudy`;
    case "03":
      return "wi-cloud";
    case "04":
      return "wi-cloudy";
    case "09":
      return `wi-${dayPrefix}-showers`;
    case "10":
      return `wi-${dayPrefix}-rain`;
    case "11":
      return `wi-${dayPrefix}-thunderstorm`;
    case "13":
      return `wi-${dayPrefix}-snow`;
    case "50":
      return `wi-${dayPrefix}-fog`;
    default:
      return isDay ? "wi-day-sunny" : "wi-night-clear";
  }
}

function applyTheme() {
  const meta = state.raw.meta || {};
  const theme = meta.theme || "default";

  document.body.classList.remove(
    "theme-clear-day",
    "theme-clear-night",
    "theme-rain",
    "theme-snow",
    "theme-clouds",
    "theme-thunderstorm",
    "theme-fog",
    "theme-default"
  );
  document.body.classList.add(`theme-${theme}`);
}

function savePreferences() {
  const prefs = {
    unit: state.unit,
    theme: document.documentElement.getAttribute("data-theme") || "dark",
  };
  try {
    window.localStorage.setItem("skyglass_prefs", JSON.stringify(prefs));
  } catch (e) {
    console.warn("Unable to persist preferences", e);
  }
}

function restorePreferences() {
  try {
    const stored = window.localStorage.getItem("skyglass_prefs");
    if (!stored) return;
    const prefs = JSON.parse(stored);

    if (prefs.unit === "imperial") {
      state.unit = "imperial";
      elements.unitToggle.checked = true;
      elements.unitLabel.textContent = "°F";
    }

    const mode = prefs.theme === "light" ? "light" : "dark";
    elements.themeToggle.checked = mode === "dark";
    document.documentElement.setAttribute("data-theme", mode);
    document.body.setAttribute("data-theme", mode);
  } catch (e) {
    console.warn("Unable to restore preferences", e);
  }
}

window.addEventListener("DOMContentLoaded", init);
