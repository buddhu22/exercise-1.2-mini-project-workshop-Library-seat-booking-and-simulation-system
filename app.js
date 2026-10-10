"use strict";

const RESOURCES = [
  { resource_id: "LIB-SEAT-001", type: "Study seat", name: "Study Seat 1", location: "Quiet Zone A", icon: "⌂" },
  { resource_id: "LIB-SEAT-002", type: "Study seat", name: "Study Seat 2", location: "Quiet Zone A", icon: "⌂" },
  { resource_id: "LAP-001", type: "Laptop", name: "Laptop 1", location: "Equipment Desk", icon: "▣" },
  { resource_id: "LAP-002", type: "Laptop", name: "Laptop 2", location: "Equipment Desk", icon: "▣" },
  { resource_id: "PROJ-001", type: "Projector", name: "Projector 1", location: "Workshop Room", icon: "▤" },
];
const STORAGE_KEY = "unsiet-library-bookings-v1";
const FIELDS = ["booking_id", "resource_id", "date", "start_time", "end_time", "user_id", "purpose", "status"];
let storageHealthy = true;
let bookings = loadBookings();
let cancelTarget = null;

function loadBookings() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return [];
    const parsed = JSON.parse(saved);
    if (!Array.isArray(parsed) || parsed.some((item) => !item || typeof item !== "object")) throw new Error("Invalid booking data");
    return parsed;
  } catch (error) {
    console.warn("Saved booking data could not be read.", error);
    storageHealthy = false;
    return [];
  }
}
function saveBookings() {
  if (!storageHealthy) {
    message("Saved browser data is invalid, so new changes are disabled to protect it. Review or clear this browser’s site data first.", true);
    return false;
  }
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(bookings));
    return true;
  } catch (error) {
    console.error("Could not save booking data.", error);
    message("Browser storage is unavailable. Please enable local storage and try again.", true);
    return false;
  }
}
function localDateString(date = new Date()) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
}
function message(text, isError = false) {
  const area = document.getElementById("form-message");
  area.textContent = text;
  area.classList.toggle("error", isError);
}
function overlaps(aStart, aEnd, bStart, bEnd) {
  // Treat time slots as [start, end), so back-to-back bookings are allowed.
  return aStart < bEnd && bStart < aEnd;
}
function resourceName(resourceId) {
  const found = RESOURCES.find((resource) => resource.resource_id === resourceId);
  return found ? found.name : resourceId;
}
function renderResources() {
  const select = document.getElementById("resource");
  select.innerHTML = RESOURCES.map((r) => `<option value="${r.resource_id}">${r.resource_id} — ${r.name}</option>`).join("");
  document.getElementById("resource-count").textContent = String(RESOURCES.length).padStart(2, "0");
  document.getElementById("catalogue-total").textContent = `${String(RESOURCES.length).padStart(2, "0")} ITEMS`;
  document.getElementById("resource-list").innerHTML = RESOURCES.map((r) => `<div class="resource-item"><span class="resource-icon" aria-hidden="true">${r.icon}</span><div><div class="resource-name">${r.name}</div><div class="resource-meta">${r.resource_id} · ${r.location}</div></div><span class="resource-status">Available</span></div>`).join("");
}
function renderSchedule() {
  const targetDate = document.getElementById("schedule-date").value;
  const rows = bookings.filter((b) => b.date === targetDate).sort((a, b) => a.resource_id.localeCompare(b.resource_id) || a.start_time.localeCompare(b.start_time));
  document.getElementById("schedule-body").innerHTML = rows.map((b) => `<tr><td>${escapeHtml(b.start_time)}–${escapeHtml(b.end_time)}</td><td>${escapeHtml(resourceName(b.resource_id))}<br><span class="muted">${escapeHtml(b.resource_id)}</span></td><td>${escapeHtml(b.booking_id)}</td><td>${escapeHtml(b.user_id)}</td><td>${escapeHtml(b.purpose)}</td><td><span class="status-pill${b.status === "Cancelled" ? " cancelled" : ""}">${escapeHtml(b.status)}</span></td><td>${b.status === "Active" ? `<button type="button" class="cancel-link" data-cancel="${escapeHtml(b.booking_id)}">Cancel</button>` : ""}</td></tr>`).join("");
  document.getElementById("empty-schedule").hidden = rows.length > 0;
  const total = bookings.length;
  document.getElementById("all-bookings").textContent = total ? `${total} saved booking${total === 1 ? "" : "s"} in this browser` : "";
  document.getElementById("active-count").textContent = String(bookings.filter((b) => b.status === "Active").length).padStart(2, "0");
}
function renderReports() {
  const counts = RESOURCES.map((r) => ({ ...r, count: bookings.filter((b) => b.resource_id === r.resource_id).length })).sort((a, b) => b.count - a.count || a.resource_id.localeCompare(b.resource_id));
  document.getElementById("usage-report").innerHTML = counts.map((r) => `<div class="report-line"><span>${escapeHtml(r.name)}</span><span class="muted">${escapeHtml(r.resource_id)}</span><strong>${r.count}</strong></div>`).join("");
  const cancelled = bookings.filter((b) => b.status === "Cancelled");
  document.getElementById("cancelled-total").textContent = `${String(cancelled.length).padStart(2, "0")} RECORD${cancelled.length === 1 ? "" : "S"}`;
  document.getElementById("cancelled-report").innerHTML = cancelled.length ? cancelled.map((b) => `<div class="report-line"><span>${escapeHtml(b.booking_id)}<br><span class="muted">${escapeHtml(b.resource_id)} · ${escapeHtml(b.date)}</span></span><span class="muted">${escapeHtml(b.user_id)} · ${escapeHtml(b.purpose)}</span><strong class="status-pill cancelled">Cancelled</strong></div>`).join("") : `<p class="report-empty">No cancellations to report.</p>`;
}
function render() { renderSchedule(); renderReports(); }
function showCancelDialog(bookingId) {
  cancelTarget = bookingId;
  document.getElementById("confirm-text").textContent = `Booking ${bookingId} will remain in your cancelled booking history.`;
  document.getElementById("confirm-dialog").showModal();
}
function downloadFile(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url; link.download = filename; link.click();
  URL.revokeObjectURL(url);
}
function csvCell(value) { return `"${String(value ?? "").replace(/"/g, '""')}"`; }

document.getElementById("booking-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const resourceId = document.getElementById("resource").value;
  const date = document.getElementById("date").value;
  const startTime = document.getElementById("start-time").value;
  const endTime = document.getElementById("end-time").value;
  const userId = document.getElementById("user-id").value.trim();
  const purpose = document.getElementById("purpose").value.trim();
  if (!resourceId || !date || !startTime || !endTime || !userId || !purpose) return message("Please complete every field.", true);
  const parsedDate = /^\d{4}-\d{2}-\d{2}$/.test(date) ? new Date(`${date}T00:00:00`) : null;
  if (!parsedDate || Number.isNaN(parsedDate.getTime()) || localDateString(parsedDate) !== date) return message("Enter a valid date.", true);
  if (endTime <= startTime) return message("End time must be later than start time.", true);
  const bookingId = `BKG-${Date.now().toString(36).toUpperCase()}`;
  if (bookings.some((b) => b.booking_id === bookingId)) return message("Could not create a unique booking ID. Please try again.", true);
  const conflict = bookings.some((b) => b.status === "Active" && b.resource_id === resourceId && b.date === date && overlaps(startTime, endTime, b.start_time, b.end_time));
  if (conflict) return message("That time overlaps an existing active booking. Try another time.", true);
  bookings.push({ booking_id: bookingId, resource_id: resourceId, date, start_time: startTime, end_time: endTime, user_id: userId, purpose, status: "Active" });
  if (!saveBookings()) { bookings.pop(); return; }
  event.target.reset();
  document.getElementById("date").value = localDateString();
  message(`Booking confirmed. Your booking ID is ${bookingId}.`);
  render();
});

document.getElementById("schedule-date").addEventListener("change", renderSchedule);
document.getElementById("schedule-body").addEventListener("click", (event) => {
  const button = event.target.closest("[data-cancel]");
  if (button) showCancelDialog(button.dataset.cancel);
});
document.getElementById("confirm-dialog").addEventListener("close", (event) => {
  if (event.target.returnValue === "cancel" && cancelTarget) {
    const booking = bookings.find((b) => b.booking_id === cancelTarget);
    if (booking && booking.status === "Active") { booking.status = "Cancelled"; saveBookings(); render(); }
  }
  cancelTarget = null;
});
document.getElementById("export-csv").addEventListener("click", () => {
  const date = document.getElementById("schedule-date").value;
  if (!date) return message("Choose a date before exporting.", true);
  const rows = bookings.filter((b) => b.date === date).sort((a, b) => a.resource_id.localeCompare(b.resource_id) || a.start_time.localeCompare(b.start_time));
  const csv = [FIELDS.map(csvCell).join(","), ...rows.map((row) => FIELDS.map((field) => csvCell(row[field])).join(","))].join("\r\n");
  downloadFile(`daily_schedule_${date}.csv`, csv, "text/csv;charset=utf-8");
  message(`CSV schedule downloaded for ${date}.`);
});
document.getElementById("export-json").addEventListener("click", () => {
  downloadFile("library_bookings.json", JSON.stringify(bookings, null, 2), "application/json;charset=utf-8");
  message("A JSON copy of this browser's bookings has been downloaded.");
});
document.getElementById("next-date").textContent = "Today";
document.getElementById("date").value = localDateString();
document.getElementById("schedule-date").value = localDateString();
renderResources();
render();
if (!storageHealthy) message("Saved browser data could not be read. It has been preserved; changes are disabled to protect it.", true);
