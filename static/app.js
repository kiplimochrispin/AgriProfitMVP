const storageKeys = {
  token: "agriprofit.authToken",
  userId: "agriprofit.activeUserId",
  cropPlanId: "agriprofit.activeCropPlanId",
};

const state = { users: [], cropPlans: [], inputs: [], harvests: [] };

const fmtMoney = (value) => value == null ? "--" : "KSh " + Number(value).toLocaleString();
const fmtSignedPercent = (value) => {
  if (value == null) return "--";
  const num = Number(value);
  return (num > 0 ? "+" : "") + num.toLocaleString() + "%";
};

const setText = (id, value) => {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
};

const token = () => localStorage.getItem(storageKeys.token);
const activeUserId = () => localStorage.getItem(storageKeys.userId);
const activeCropPlanId = () => localStorage.getItem(storageKeys.cropPlanId);
const setActiveUserId = (id) => id && localStorage.setItem(storageKeys.userId, id);
const setActiveCropPlanId = (id) => id && localStorage.setItem(storageKeys.cropPlanId, id);

const toPayload = (form) =>
  Object.fromEntries(
    Object.entries(Object.fromEntries(new FormData(form).entries()))
      .filter(([, value]) => value !== "")
      .map(([key, value]) => {
        if (["farm_size_acres", "acres", "quantity", "cost_ksh", "acres_applied", "actual_yield_kg_total", "selling_price_per_kg", "other_costs_ksh"].includes(key)) {
          return [key, Number(value)];
        }
        if (["season_year", "expected_yield_kg_per_acre"].includes(key)) {
          return [key, Number(value)];
        }
        return [key, value];
      })
  );

const logActivity = (message) => {
  const log = document.getElementById("activity-log");
  const entry = document.createElement("div");
  entry.className = "activity-item";
  entry.textContent = message;
  if (log.children.length === 1 && /No actions/.test(log.children[0].textContent)) log.innerHTML = "";
  log.prepend(entry);
};

const authHeaders = () => token() ? { Authorization: `Bearer ${token()}` } : {};

const apiFetch = async (url, options = {}) => {
  const headers = { ...(options.headers || {}), ...authHeaders() };
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) throw new Error(await response.text());
  if (response.status === 204) return null;
  return response.json();
};

const fillSelect = (id, items, labeler, selected) => {
  const select = document.getElementById(id);
  if (!select) return;
  select.innerHTML = items.map((item) =>
    `<option value="${item.id}" ${item.id === selected ? "selected" : ""}>${labeler(item)}</option>`
  ).join("");
};

const updateAuthStatus = () => {
  setText("auth-status", token() ? "Authenticated workspace ready." : "Not logged in.");
};

const updateActiveBadge = () => {
  const active = state.users.find((user) => user.id === activeUserId()) || state.users[0];
  if (active && !activeUserId()) setActiveUserId(active.id);
  setText(
    "active-user-badge",
    active
      ? `Active farmer: ${active.full_name || active.phone} • ${active.county} • ${active.soil_type || "soil pending"}`
      : "No active farmer selected yet."
  );
};

const renderTrend = (labels, values) => {
  const width = 680, height = 260, left = 42, right = 22, top = 22, bottom = 40;
  const plotWidth = width - left - right, plotHeight = height - top - bottom;
  const max = Math.max(...values, 1), min = Math.min(...values, 0), range = Math.max(max - min, 1);
  const xStep = values.length > 1 ? plotWidth / (values.length - 1) : 0;
  const points = values.map((value, index) => [left + index * xStep, top + ((max - value) / range) * plotHeight]);
  const line = points.length ? "M " + points.map(([x, y]) => `${x} ${y}`).join(" L ") : "";
  const grid = [0, 0.25, 0.5, 0.75, 1].map((tick) => {
    const y = top + tick * plotHeight;
    return `<line x1="${left}" y1="${y}" x2="${width - right}" y2="${y}" stroke="rgba(29,43,31,0.10)" stroke-dasharray="4 8" />`;
  }).join("");
  const dots = points.map(([x, y], index) =>
    `<circle cx="${x}" cy="${y}" r="5" fill="#f7f4ec" stroke="#2f6a3e" stroke-width="3"></circle>
     <text x="${x}" y="${y - 14}" text-anchor="middle" fill="#203328" font-size="12">${Number(values[index]).toLocaleString()}</text>`
  ).join("");
  const first = points[0] || [left, top + plotHeight];
  const last = points[points.length - 1] || [left, top + plotHeight];
  const area = `M ${first[0]} ${top + plotHeight} L ${points.map(([x, y]) => `${x} ${y}`).join(" L ")} L ${last[0]} ${top + plotHeight} Z`;
  document.getElementById("trend-grid").innerHTML = grid;
  document.getElementById("trend-line").setAttribute("d", line);
  document.getElementById("trend-area").setAttribute("d", area);
  document.getElementById("trend-dots").innerHTML = dots;
  document.getElementById("trend-labels").innerHTML = labels.map((label) => `<span>${label}</span>`).join("");
};

const renderBars = (labels, used, recommended) => {
  const container = document.getElementById("fert-bars");
  const max = Math.max(...used, ...recommended, 1);
  container.innerHTML = labels.map((label, index) => `
    <div class="bar-row">
      <div class="bar-name">${label}</div>
      <div class="bar-stack">
        <div class="bar-track"><div class="bar bar-used" style="width:${Math.max((Number(used[index] || 0) / max) * 100, 3)}%"></div></div>
        <div class="bar-track"><div class="bar bar-recommended" style="width:${Math.max((Number(recommended[index] || 0) / max) * 100, 3)}%"></div></div>
        <div class="bar-meta">
          <span>Used: ${Number(used[index] || 0).toLocaleString()} kg</span>
          <span>Recommended: ${Number(recommended[index] || 0).toLocaleString()} kg</span>
        </div>
      </div>
    </div>`).join("");
};

const refreshDashboard = async () => {
  const url = activeUserId() ? `/analytics/dashboard?user_id=${encodeURIComponent(activeUserId())}` : "/analytics/dashboard";
  const data = await apiFetch(url);
  setText("hero-roi", fmtSignedPercent(data.roi_percent));
  setText("hero-revenue", fmtMoney(data.total_revenue_ksh));
  setText("hero-fertilizer-signal", fmtSignedPercent(data.over_under_fert_percent));
  setText("hero-season", String(data.season_year ?? "--"));
  setText("stat-profit", fmtMoney(data.profit_loss_ksh));
  setText("stat-per-acre", fmtMoney(data.profit_per_acre_ksh));
  setText("stat-cost", fmtMoney(data.total_cost_ksh));
  setText("stat-crop", `${(data.crop_type || "crop").toUpperCase()} / ${data.acres || 0} ac`);
  const signal = Number(data.over_under_fert_percent || 0);
  setText("signal-box", signal > 0 ? `Field signal: fertilizer usage is ${signal.toLocaleString()}% above recommendation.` :
    signal < 0 ? `Field signal: fertilizer usage is ${Math.abs(signal).toLocaleString()}% below recommendation.` :
    "Field signal: fertilizer usage is aligned with recommendation.");
  const seasons = data.seasons?.length ? data.seasons : ["Current"];
  const history = data.profit_history?.length ? data.profit_history.map(Number) : [0];
  renderTrend(seasons, history);
  const fert = data.fertilizer_comparison || {};
  renderBars(
    fert.labels?.length ? fert.labels : [data.crop_type || "Crop"],
    fert.used_per_acre?.length ? fert.used_per_acre.map(Number) : [Number(data.avg_fert_used || 0)],
    fert.recommended_per_acre?.length ? fert.recommended_per_acre.map(Number) : [Number(data.recommended_fert || 0)],
  );
};

const renderRecordList = (id, items, renderer) => {
  const container = document.getElementById(id);
  container.innerHTML = items.length ? items.map(renderer).join("") : `<div class="activity-item">No records yet.</div>`;
};

const actionButtons = (kind, id) => `
  <div class="record-actions">
    <button class="edit" data-kind="${kind}" data-id="${id}" data-action="edit" type="button">Edit</button>
    <button class="delete" data-kind="${kind}" data-id="${id}" data-action="delete" type="button">Delete</button>
  </div>`;

const loadUsers = async () => {
  state.users = await apiFetch("/users/");
  const selected = activeUserId() || state.users[0]?.id;
  if (selected) setActiveUserId(selected);
  fillSelect("crop-user-id", state.users, (u) => `${u.full_name || "Farmer"} (${u.phone})`, selected);
  fillSelect("input-user-id", state.users, (u) => `${u.full_name || "Farmer"} (${u.phone})`, selected);
  updateActiveBadge();
  renderRecordList("users-list", state.users, (u) => `<div class="activity-item"><strong>${u.full_name || u.phone}</strong><br>${u.county} • ${u.soil_type || "soil pending"}${actionButtons("user", u.id)}</div>`);
};

const loadCropPlans = async () => {
  state.cropPlans = await apiFetch("/crop-plans/");
  const selected = activeCropPlanId() || state.cropPlans[0]?.id;
  if (selected) setActiveCropPlanId(selected);
  fillSelect("input-crop-plan-id", state.cropPlans, (p) => `${p.crop_type} • ${p.season_year} • ${p.acres} ac`, selected);
  fillSelect("harvest-crop-plan-id", state.cropPlans, (p) => `${p.crop_type} • ${p.season_year} • ${p.acres} ac`, selected);
  renderRecordList("plans-list", state.cropPlans, (p) => `<div class="activity-item"><strong>${p.crop_type}</strong><br>${p.season_year} • ${p.acres} ac${actionButtons("crop-plan", p.id)}</div>`);
};

const loadInputs = async () => {
  state.inputs = await apiFetch("/inputs/");
  renderRecordList("inputs-list", state.inputs, (i) => `<div class="activity-item"><strong>${i.item_name}</strong><br>${i.category} • KSh ${Number(i.cost_ksh).toLocaleString()}${actionButtons("input", i.id)}</div>`);
};

const loadHarvests = async () => {
  state.harvests = await apiFetch("/harvests/");
  renderRecordList("harvests-list", state.harvests, (h) => `<div class="activity-item"><strong>${Number(h.actual_yield_kg_total || 0).toLocaleString()} kg</strong><br>KSh ${Number(h.selling_price_per_kg || 0).toLocaleString()}/kg${actionButtons("harvest", h.id)}</div>`);
};

const refreshAll = async () => {
  await loadUsers();
  await loadCropPlans();
  await loadInputs();
  await loadHarvests();
  await refreshDashboard();
};

const postJSON = (url, payload) => apiFetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
const patchJSON = (url, payload) => apiFetch(url, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
const deleteJSON = (url) => apiFetch(url, { method: "DELETE" });

document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = await postJSON("/auth/login", toPayload(event.currentTarget));
  localStorage.setItem(storageKeys.token, result.access_token);
  updateAuthStatus();
  logActivity("Logged in successfully.");
});

document.getElementById("logout-button").addEventListener("click", () => {
  localStorage.removeItem(storageKeys.token);
  updateAuthStatus();
  logActivity("Logged out.");
});

document.getElementById("user-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const created = await postJSON("/users/", toPayload(event.currentTarget));
  setActiveUserId(created.id);
  event.currentTarget.reset();
  event.currentTarget.county.value = "Uasin Gishu";
  event.currentTarget.soil_type.value = "loam";
  await refreshAll();
  logActivity(`Created farmer ${created.full_name || created.phone}.`);
});

document.getElementById("crop-plan-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = toPayload(event.currentTarget);
  payload.user_id = document.getElementById("crop-user-id").value;
  const created = await postJSON("/crop-plans/", payload);
  setActiveUserId(payload.user_id);
  setActiveCropPlanId(created.id);
  event.currentTarget.reset();
  event.currentTarget.season_year.value = "2026";
  await refreshAll();
  logActivity(`Created crop plan for ${created.crop_type}.`);
});

document.getElementById("input-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = toPayload(event.currentTarget);
  payload.user_id = document.getElementById("input-user-id").value;
  payload.crop_plan_id = document.getElementById("input-crop-plan-id").value;
  const created = await postJSON("/inputs/", payload);
  setActiveUserId(payload.user_id);
  setActiveCropPlanId(payload.crop_plan_id);
  event.currentTarget.reset();
  await refreshAll();
  logActivity(`Added input ${created.item_name}.`);
});

document.getElementById("harvest-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = toPayload(event.currentTarget);
  payload.crop_plan_id = document.getElementById("harvest-crop-plan-id").value;
  const created = await postJSON("/harvests/", payload);
  setActiveCropPlanId(payload.crop_plan_id);
  event.currentTarget.reset();
  event.currentTarget.other_costs_ksh.value = "0";
  await refreshAll();
  logActivity(`Recorded harvest ${created.actual_yield_kg_total} kg.`);
});

document.getElementById("refresh-preview").addEventListener("click", refreshDashboard);

document.addEventListener("click", async (event) => {
  const target = event.target.closest("button[data-action]");
  if (!target) return;
  const { kind, id, action } = target.dataset;
  if (action === "delete") {
    if (!confirm(`Delete this ${kind}?`)) return;
    const endpoint = kind === "user" ? `/users/${id}` : kind === "crop-plan" ? `/crop-plans/${id}` : kind === "input" ? `/inputs/${id}` : `/harvests/${id}`;
    await deleteJSON(endpoint);
    await refreshAll();
    logActivity(`Deleted ${kind}.`);
    return;
  }
  if (action === "edit") {
    const record = kind === "user" ? state.users.find((item) => item.id === id)
      : kind === "crop-plan" ? state.cropPlans.find((item) => item.id === id)
      : kind === "input" ? state.inputs.find((item) => item.id === id)
      : state.harvests.find((item) => item.id === id);
    if (!record) return;
    if (kind === "user") {
      const full_name = prompt("Farmer name", record.full_name || "");
      const county = prompt("County", record.county || "");
      if (full_name !== null && county !== null) await patchJSON(`/users/${id}`, { full_name, county });
    } else if (kind === "crop-plan") {
      const crop_type = prompt("Crop type", record.crop_type);
      const acres = prompt("Acres", record.acres);
      if (crop_type !== null && acres !== null) await patchJSON(`/crop-plans/${id}`, { crop_type, acres: Number(acres) });
    } else if (kind === "input") {
      const cost_ksh = prompt("Cost KSh", record.cost_ksh);
      const quantity = prompt("Quantity", record.quantity ?? "");
      if (cost_ksh !== null) await patchJSON(`/inputs/${id}`, { cost_ksh: Number(cost_ksh), quantity: quantity === "" ? null : Number(quantity) });
    } else {
      const selling_price_per_kg = prompt("Selling price per kg", record.selling_price_per_kg);
      const actual_yield_kg_total = prompt("Actual yield kg total", record.actual_yield_kg_total);
      if (selling_price_per_kg !== null) await patchJSON(`/harvests/${id}`, { selling_price_per_kg: Number(selling_price_per_kg), actual_yield_kg_total: Number(actual_yield_kg_total) });
    }
    await refreshAll();
    logActivity(`Updated ${kind}.`);
  }
});

updateAuthStatus();
refreshAll().catch((error) => {
  logActivity(`Startup issue: ${error.message}`);
  setText("signal-box", "Live dashboard preview is temporarily unavailable.");
});
