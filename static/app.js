const $ = (selector) => document.querySelector(selector);
const state = { scanner: null, scanLocked: false, product: null };

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
    const items = await api("/api/inventory");
    container.replaceChildren();
    if (!items.length) {
      container.innerHTML = '<div class="empty"><strong>Your fridge log is empty.</strong><span>Scan your first item above.</span></div>';
      return;
    }
    const template = $("#item-template");
    for (const item of items) {
      const card = template.content.firstElementChild.cloneNode(true);
      card.querySelector("strong").textContent = item.name;
      card.querySelector(".item-meta").textContent = item.expires_on ? `Expires ${formatDate(item.expires_on)}` : "No expiration date";
      card.querySelector("small").textContent = `Barcode ${item.barcode}`;
      card.querySelector(".quantity").textContent = `×${item.quantity}`;
      card.querySelector(".edit-item").addEventListener("click", () => openEditor(item));
      card.querySelector(".remove-one").addEventListener("click", () => removeItem(item.id, false));
      card.querySelector(".remove-all").addEventListener("click", () => removeItem(item.id, true));
      container.append(card);
    }
  } catch (error) {
    container.innerHTML = `<div class="empty error">${error.message}</div>`;
  }
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
  } catch {
    $("#status-line").textContent = "Fridge status unavailable";
  }
}

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" }).format(new Date(`${value}T00:00:00Z`));
}

$("#lookup").addEventListener("click", () => lookupBarcode());
$("#start-scan").addEventListener("click", startScanner);
$("#stop-scan").addEventListener("click", stopScanner);
$("#barcode-photo").addEventListener("change", scanPhoto);
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
$("#refresh").addEventListener("click", () => Promise.all([loadInventory(), loadStatus()]));
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
loadInventory();
loadStatus();
