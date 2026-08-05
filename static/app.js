const $ = (selector) => document.querySelector(selector);
const state = { scanner: null, scanLocked: false, product: null, inventory: [], filter: "all", history: null, historyHours: 24 };

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || "Something went wrong.");
  return body;
}

function setMessage(text, error = false) {
  const node = $("#form-message");
  node.textContent = text;
  node.classList.toggle("error", error);
}

async function lookupBarcode(barcode = $("#barcode").value) {
  barcode = barcode.trim();
  if (!barcode) return setMessage("Scan or enter a barcode first.", true);
  setMessage("Looking up product…");
  try {
    const product = await api("/api/products/lookup", {
      method: "POST",
      body: JSON.stringify({ barcode }),
    });
    state.product = product;
    $("#barcode").value = product.barcode;
    $("#name").value = product.name;
    $("#product-result").textContent = product.name;
    $("#product-preview").hidden = false;
    const image = $("#product-image");
    image.hidden = !product.image_url;
    if (product.image_url) image.src = product.image_url;
    setMessage(product.found ? "Product found. Add its expiration date." : "Product was not found. Edit the item name before saving.", !product.found);
    $("#expires-on").focus();
  } catch (error) {
    setMessage(error.message, true);
  }
}

async function startScanner() {
  if (!window.isSecureContext) {
    return setMessage("Live camera access needs HTTPS. You can still type the barcode manually.", true);
  }
  if (!window.ZXingBrowser) {
    return setMessage("The camera scanner could not load. Check internet access or enter the barcode manually.", true);
  }
  $("#camera-wrap").hidden = false;
  state.scanLocked = false;
  try {
    const reader = new ZXingBrowser.BrowserMultiFormatReader();
    state.scanner = await reader.decodeFromConstraints(
      { video: { facingMode: { ideal: "environment" } }, audio: false },
      $("#camera"),
      async (result) => {
        if (!result || state.scanLocked) return;
        state.scanLocked = true;
        $("#barcode").value = result.getText();
        stopScanner();
        await lookupBarcode(result.getText());
      },
    );
    setMessage("Point the rear camera at the product barcode.");
  } catch (error) {
    stopScanner();
    setMessage(`Camera could not start: ${error.message}`, true);
  }
}

function stopScanner() {
  if (state.scanner) state.scanner.stop();
  state.scanner = null;
  const video = $("#camera");
  if (video.srcObject) video.srcObject.getTracks().forEach((track) => track.stop());
  video.srcObject = null;
  $("#camera-wrap").hidden = true;
}

async function scanPhoto(event) {
  const file = event.target.files[0];
  event.target.value = "";
  if (!file) return;
  if (!window.ZXingBrowser) return setMessage("The barcode reader could not load. Type the barcode digits manually.", true);
  const url = URL.createObjectURL(file);
  setMessage("Reading barcode photo…");
  try {
    const reader = new ZXingBrowser.BrowserMultiFormatReader();
    const result = await reader.decodeFromImageUrl(url);
    $("#barcode").value = result.getText();
    await lookupBarcode(result.getText());
  } catch {
    setMessage("No barcode was found in that photo. Try again in bright light with the entire barcode visible.", true);
  } finally {
    URL.revokeObjectURL(url);
  }
}

async function loadInventory() {
  const container = $("#inventory");
  try {
    state.inventory = await api("/api/inventory");
    updateFilterCounts();
    renderInventory();
  } catch (error) {
    container.innerHTML = `<div class="empty error">${error.message}</div>`;
  }
}

function renderInventory() {
  const container = $("#inventory");
  container.replaceChildren();
  if (!state.inventory.length) {
    container.innerHTML = '<div class="empty"><strong>Your fridge log is empty.</strong><span>Scan your first item above.</span></div>';
    return;
  }

  const items = state.inventory.filter((item) => {
    if (state.filter === "all") return true;
    return expirationState(item.expires_on).key === state.filter;
  });
  if (!items.length) {
    container.innerHTML = '<div class="empty"><strong>Nothing in this group.</strong><span>Choose another filter to see more food.</span></div>';
    return;
  }

  const template = $("#item-template");
  for (const item of items) {
    const dateState = expirationState(item.expires_on);
    const card = template.content.firstElementChild.cloneNode(true);
    card.classList.add(`date-${dateState.key}`);
    card.querySelector("strong").textContent = item.name;
    card.querySelector(".item-meta").textContent = item.expires_on ? `Expires ${formatDate(item.expires_on)}` : "No expiration date";
    const badge = card.querySelector(".date-badge");
    badge.textContent = dateState.label;
    badge.classList.add(dateState.key);
    card.querySelector("small").textContent = `Barcode ${item.barcode}`;
    card.querySelector(".quantity").textContent = `x${item.quantity}`;
    card.querySelector(".edit-item").addEventListener("click", () => openEditor(item));
    card.querySelector(".remove-one").addEventListener("click", () => removeItem(item.id, false));
    card.querySelector(".remove-all").addEventListener("click", () => removeItem(item.id, true));
    container.append(card);
  }
}

function expirationState(expiresOn) {
  if (!expiresOn) return { key: "undated", label: "No date" };
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const cutoff = new Date(today);
  cutoff.setDate(cutoff.getDate() + 3);
  const expiration = new Date(`${expiresOn}T00:00:00`);
  if (expiration < today) return { key: "expired", label: "Expired" };
  if (expiration <= cutoff) {
    return { key: "soon", label: expiration.getTime() === today.getTime() ? "Today" : "Soon" };
  }
  return { key: "fresh", label: "Fresh" };
}

function updateFilterCounts() {
  const counts = { all: 0, expired: 0, soon: 0, undated: 0 };
  for (const item of state.inventory) {
    counts.all += item.quantity;
    const key = expirationState(item.expires_on).key;
    if (key in counts) counts[key] += item.quantity;
  }
  document.querySelectorAll(".filter").forEach((button) => {
    button.querySelector("span").textContent = counts[button.dataset.filter];
  });
}

function setInventoryFilter(filter) {
  state.filter = filter;
  document.querySelectorAll(".filter").forEach((button) => {
    const active = button.dataset.filter === filter;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", active);
  });
  renderInventory();
}

function openEditor(item) {
  $("#edit-id").value = item.id;
  $("#edit-barcode").value = item.barcode;
  $("#edit-name").value = item.name;
  $("#edit-expires-on").value = item.expires_on || "";
  $("#edit-quantity").value = item.quantity;
  $("#edit-message").textContent = "";
  $("#edit-dialog").showModal();
}

function closeEditor() {
  $("#edit-dialog").close();
}

async function removeItem(id, all) {
  try {
    const result = await api(`/api/inventory/${id}${all ? "?all=1" : ""}`, { method: "DELETE" });
    setMessage(result.message);
    await Promise.all([loadInventory(), loadStatus()]);
  } catch (error) {
    setMessage(error.message, true);
  }
}

async function loadStatus() {
  try {
    const status = await api("/api/status");
    const temperature = status.temperature_f === null ? "No temperature sensor" : `${status.temperature_f}°F · ${status.temperature_status}`;
    $("#status-line").textContent = `${temperature} · ${status.inventory_count} items · ${status.expiring_count} expiring soon`;
    const face = $("#bmo-face");
    face.className = `face ${status.bmo_mood}`;
    face.setAttribute("aria-label", `BMO mood: ${status.bmo_mood}. ${temperature}`);
  } catch {
    $("#status-line").textContent = "Fridge status unavailable";
  }
}

async function loadTemperatureHistory(hours = state.historyHours) {
  state.historyHours = hours;
  document.querySelectorAll(".range").forEach((button) => {
    button.classList.toggle("active", Number(button.dataset.hours) === hours);
  });
  try {
    state.history = await api(`/api/temperature-history?hours=${hours}`);
    drawTemperatureChart();
  } catch (error) {
    state.history = null;
    $("#temperature-chart").hidden = true;
    $("#chart-empty").hidden = false;
    $("#chart-summary").textContent = error.message;
  }
}

function drawTemperatureChart() {
  const canvas = $("#temperature-chart");
  const empty = $("#chart-empty");
  const points = state.history?.points || [];
  if (!points.length) {
    canvas.hidden = true;
    empty.hidden = false;
    $("#chart-summary").textContent = "No readings yet";
    return;
  }

  canvas.hidden = false;
  empty.hidden = true;
  const ratio = window.devicePixelRatio || 1;
  const width = Math.max(canvas.clientWidth, 280);
  const height = 230;
  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  const context = canvas.getContext("2d");
  context.scale(ratio, ratio);

  const padding = { left: 38, right: 12, top: 12, bottom: 28 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const temperatures = points.map((point) => point.temperature_f);
  const minimum = Math.floor(Math.min(...temperatures, state.history.safe_min_f) - 2);
  const maximum = Math.ceil(Math.max(...temperatures, state.history.safe_max_f) + 2);
  const timestamps = points.map((point) => new Date(point.timestamp).getTime());
  const timeMin = Math.min(...timestamps);
  const timeMax = Math.max(...timestamps);
  const x = (timestamp) => padding.left + (timeMax === timeMin ? plotWidth / 2 : ((timestamp - timeMin) / (timeMax - timeMin)) * plotWidth);
  const y = (temperature) => padding.top + ((maximum - temperature) / (maximum - minimum)) * plotHeight;

  context.clearRect(0, 0, width, height);
  context.fillStyle = "rgba(98, 185, 170, 0.18)";
  context.fillRect(padding.left, y(state.history.safe_max_f), plotWidth, y(state.history.safe_min_f) - y(state.history.safe_max_f));

  context.strokeStyle = "#d7dfd8";
  context.lineWidth = 1;
  context.fillStyle = "#647a78";
  context.font = "11px system-ui";
  context.textAlign = "right";
  for (const temperature of [minimum, state.history.safe_min_f, state.history.safe_max_f, maximum]) {
    context.beginPath();
    context.moveTo(padding.left, y(temperature));
    context.lineTo(width - padding.right, y(temperature));
    context.stroke();
    context.fillText(`${temperature}°`, padding.left - 6, y(temperature) + 4);
  }

  context.strokeStyle = "#327e74";
  context.lineWidth = 2.5;
  context.lineJoin = "round";
  context.beginPath();
  points.forEach((point, index) => {
    const pointX = x(timestamps[index]);
    const pointY = y(point.temperature_f);
    if (index === 0) context.moveTo(pointX, pointY);
    else context.lineTo(pointX, pointY);
  });
  context.stroke();

  const last = points.at(-1);
  context.fillStyle = last.temperature_f > state.history.safe_max_f || last.temperature_f < state.history.safe_min_f ? "#bf4d45" : "#327e74";
  context.beginPath();
  context.arc(x(timestamps.at(-1)), y(last.temperature_f), 4, 0, Math.PI * 2);
  context.fill();

  context.fillStyle = "#647a78";
  context.textAlign = "left";
  context.fillText(new Date(timeMin).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }), padding.left, height - 8);
  context.textAlign = "right";
  context.fillText(new Date(timeMax).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }), width - padding.right, height - 8);
  $("#chart-summary").textContent = `${last.temperature_f.toFixed(1)}°F latest · ${points.length} readings`;
}

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" }).format(new Date(`${value}T00:00:00Z`));
}

$("#lookup").addEventListener("click", () => lookupBarcode());
$("#start-scan").addEventListener("click", startScanner);
$("#stop-scan").addEventListener("click", stopScanner);
$("#barcode-photo").addEventListener("change", scanPhoto);
document.querySelectorAll(".range").forEach((button) => {
  button.addEventListener("click", () => loadTemperatureHistory(Number(button.dataset.hours)));
});
document.querySelectorAll(".filter").forEach((button) => {
  button.addEventListener("click", () => setInventoryFilter(button.dataset.filter));
});
$("#close-edit").addEventListener("click", closeEditor);
$("#edit-dialog").addEventListener("click", (event) => {
  if (event.target === $("#edit-dialog")) closeEditor();
});
$("#edit-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = $("#edit-id").value;
  const payload = {
    barcode: $("#edit-barcode").value,
    name: $("#edit-name").value,
    expires_on: $("#edit-expires-on").value,
    quantity: $("#edit-quantity").value,
  };
  try {
    const result = await api(`/api/inventory/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    closeEditor();
    setMessage(result.message);
    await Promise.all([loadInventory(), loadStatus()]);
  } catch (error) {
    const message = $("#edit-message");
    message.textContent = error.message;
    message.classList.add("error");
  }
});
$("#refresh").addEventListener("click", () => Promise.all([loadInventory(), loadStatus(), loadTemperatureHistory()]));
window.addEventListener("resize", () => { if (state.history) drawTemperatureChart(); });
$("#barcode").addEventListener("input", () => { state.product = null; $("#product-preview").hidden = true; });
$("#item-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(event.currentTarget));
  try {
    const result = await api("/api/inventory", { method: "POST", body: JSON.stringify(payload) });
    setMessage(result.message);
    event.currentTarget.reset();
    $("#quantity").value = 1;
    $("#product-preview").hidden = true;
    await Promise.all([loadInventory(), loadStatus()]);
    $("#barcode").focus();
  } catch (error) {
    setMessage(error.message, true);
  }
});
window.addEventListener("pagehide", stopScanner);
if (window.isSecureContext) {
  $("#camera-note").textContent = "Secure camera access is ready. Use Live scan for the fastest entry.";
}
loadInventory();
loadStatus();
loadTemperatureHistory();
