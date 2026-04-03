type User = {
  id: string;
  phone: string;
  email?: string | null;
  full_name?: string | null;
  county: string;
  soil_type?: string | null;
};

type CropPlan = {
  id: string;
  user_id: string;
  crop_type: string;
  acres: number;
  season_year: number;
};

type InputUsage = {
  id: string;
  item_name: string;
  category: string;
  cost_ksh: number;
  quantity?: number | null;
};

type HarvestRecord = {
  id: string;
  actual_yield_kg_total?: number | null;
  selling_price_per_kg?: number | null;
};

type DashboardData = {
  profit_loss_ksh: number;
  profit_per_acre_ksh: number;
  roi_percent: number;
  total_revenue_ksh: number;
  total_cost_ksh: number;
  crop_type?: string | null;
  acres: number;
  profit_history: number[];
  seasons: string[];
  avg_fert_used: number;
  recommended_fert: number;
  season_year?: string | null;
  over_under_fert_percent: number;
  fertilizer_comparison: {
    labels: string[];
    used_per_acre: number[];
    recommended_per_acre: number[];
  };
};

type AuthResponse = {
  access_token: string;
  token_type: string;
};

const storageKeys = {
  token: "agriprofit.authToken",
  userId: "agriprofit.activeUserId",
  cropPlanId: "agriprofit.activeCropPlanId",
} as const;

const state: {
  users: User[];
  cropPlans: CropPlan[];
  inputs: InputUsage[];
  harvests: HarvestRecord[];
} = {
  users: [],
  cropPlans: [],
  inputs: [],
  harvests: [],
};

const root = document.getElementById("app");

if (!root) {
  throw new Error("Missing #app root element");
}

root.innerHTML = `
  <main class="shell">
    <header class="masthead">
      <div class="brand">
        <div class="brand-mark"></div>
        <div>
          <div class="brand-name">AgriProfit</div>
          <div class="brand-note">Profit-first farm intelligence</div>
        </div>
      </div>
      <div class="status-pill">TypeScript frontend • live preview from <code>/analytics/dashboard</code></div>
    </header>

    <section class="hero">
      <div class="panel hero-copy">
        <div class="eyebrow">AgriProfit MVP</div>
        <h1>Farm intelligence with a local point of view.</h1>
        <p class="subtitle">
          The browser app now renders from TypeScript instead of hand-written page logic.
          The backend remains FastAPI, but the UI is driven from a typed frontend source.
        </p>
        <div class="actions">
          <a class="btn btn-primary" href="/docs">Open API Docs</a>
          <a class="btn btn-secondary" href="/analytics/dashboard">View Raw Dashboard</a>
          <a class="btn btn-secondary" href="/api">Raw API Status</a>
        </div>
      </div>

      <aside class="panel hero-side">
        <h2>Current Focus</h2>
        <div class="metric"><div class="metric-label">Live ROI</div><div class="metric-value" id="hero-roi">--</div></div>
        <div class="metric"><div class="metric-label">Tracked Revenue</div><div class="metric-value" id="hero-revenue">--</div></div>
        <div class="metric"><div class="metric-label">Fertilizer Signal</div><div class="metric-value" id="hero-fertilizer-signal">--</div></div>
        <div class="metric"><div class="metric-label">Active Season</div><div class="metric-value" id="hero-season">--</div></div>
      </aside>
    </section>

    <section class="dashboard">
      <article class="panel dashboard-panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Live Profit Canvas</h2>
            <div class="panel-kicker">Rendered from TypeScript and fed by your real stored records.</div>
          </div>
          <div class="signal" id="signal-box">Loading live field signal...</div>
        </div>

        <div class="stats">
          <div class="stat"><div class="stat-label">Profit / Loss</div><div class="stat-value" id="stat-profit">--</div></div>
          <div class="stat"><div class="stat-label">Per Acre</div><div class="stat-value" id="stat-per-acre">--</div></div>
          <div class="stat"><div class="stat-label">Total Cost</div><div class="stat-value" id="stat-cost">--</div></div>
          <div class="stat"><div class="stat-label">Crop / Acres</div><div class="stat-value" id="stat-crop">--</div></div>
        </div>

        <div class="chart-box">
          <svg id="trend-chart" viewBox="0 0 680 260" width="100%" height="260" aria-label="Profit trend chart">
            <defs>
              <linearGradient id="trendFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="rgba(47, 106, 62, 0.36)"></stop>
                <stop offset="100%" stop-color="rgba(47, 106, 62, 0.02)"></stop>
              </linearGradient>
            </defs>
            <rect x="0" y="0" width="680" height="260" rx="18" fill="rgba(255,255,255,0.25)"></rect>
            <g id="trend-grid"></g>
            <path id="trend-area" fill="url(#trendFill)" stroke="none"></path>
            <path id="trend-line" fill="none" stroke="#2f6a3e" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
            <g id="trend-dots"></g>
          </svg>
          <div class="chart-labels" id="trend-labels"></div>
        </div>
      </article>

      <article class="panel dashboard-panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Fertilizer Balance</h2>
            <div class="panel-kicker">Compare field usage against recommendation and spot over-application quickly.</div>
          </div>
        </div>
        <div class="bars" id="fert-bars"></div>
        <div class="legend">
          <span><i class="legend-used"></i> Used per acre</span>
          <span><i class="legend-recommended"></i> Recommended</span>
        </div>
      </article>
    </section>

    <section class="workspace">
      <article class="panel form-panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Secure Workspace</h2>
            <div class="panel-kicker">Login is required for create, edit, and delete actions.</div>
            <div class="active-badge" id="auth-status">Not logged in.</div>
          </div>
        </div>

        <form id="login-form" class="stack">
          <div class="field-grid">
            <label>Username<input name="username" value="admin" required /></label>
            <label>Password<input name="password" type="password" value="admin123" required /></label>
          </div>
          <div class="form-actions">
            <button class="button" type="submit">Login</button>
            <button class="button alt" type="button" id="logout-button">Logout</button>
          </div>
        </form>
      </article>

      <article class="panel form-panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Field Studio</h2>
            <div class="panel-kicker">Create and manage farmers, crop plans, inputs, and harvests directly from the browser.</div>
            <div class="active-badge" id="active-user-badge">No active farmer selected yet.</div>
          </div>
        </div>

        <div class="stack">
          <form id="user-form" class="stack">
            <div class="field-grid">
              <label>Farmer Name<input name="full_name" placeholder="Chris Kiplimo" required /></label>
              <label>Phone<input name="phone" placeholder="+254700000001" required /></label>
              <label>Email<input name="email" type="email" placeholder="farmer@example.com" /></label>
              <label>County<input name="county" value="Uasin Gishu" /></label>
              <label>Farm Size Acres<input name="farm_size_acres" type="number" step="0.01" placeholder="2.5" /></label>
              <label>Soil Type
                <select name="soil_type">
                  <option value="loam">Loam</option>
                  <option value="clay">Clay</option>
                  <option value="sand">Sand</option>
                  <option value="silt">Silt</option>
                  <option value="volcanic">Volcanic</option>
                </select>
              </label>
            </div>
            <div class="form-actions"><button class="button" type="submit">Create Farmer</button></div>
          </form>

          <form id="crop-plan-form" class="stack">
            <div class="field-grid">
              <label>Farmer<select id="crop-user-id" name="user_id" required></select></label>
              <label>Crop Type<input name="crop_type" placeholder="maize" required /></label>
              <label>Acres<input name="acres" type="number" step="0.01" placeholder="2" required /></label>
              <label>Season Year<input name="season_year" type="number" value="2026" required /></label>
              <label>Planting Date<input name="planting_date" type="date" /></label>
              <label>Expected Yield Kg/Acre<input name="expected_yield_kg_per_acre" type="number" placeholder="1800" /></label>
            </div>
            <div class="form-actions"><button class="button" type="submit">Create Crop Plan</button></div>
          </form>

          <form id="input-form" class="stack">
            <div class="field-grid">
              <label>Farmer<select id="input-user-id" name="user_id" required></select></label>
              <label>Crop Plan<select id="input-crop-plan-id" name="crop_plan_id" required></select></label>
              <label>Item Name<input name="item_name" placeholder="DAP" required /></label>
              <label>Category
                <select name="category">
                  <option value="fertilizer">Fertilizer</option>
                  <option value="seed">Seed</option>
                  <option value="equipment">Equipment</option>
                  <option value="pesticide">Pesticide</option>
                  <option value="herbicide">Herbicide</option>
                  <option value="labour">Labour</option>
                  <option value="transport">Transport</option>
                  <option value="other">Other</option>
                </select>
              </label>
              <label>Quantity<input name="quantity" type="number" step="0.01" placeholder="130" /></label>
              <label>Unit<input name="unit" placeholder="kg" /></label>
              <label>Cost KSh<input name="cost_ksh" type="number" step="0.01" placeholder="9500" required /></label>
              <label>Acres Applied<input name="acres_applied" type="number" step="0.01" placeholder="2" /></label>
            </div>
            <label>Notes<textarea name="notes" placeholder="Basal application at planting"></textarea></label>
            <div class="form-actions"><button class="button" type="submit">Add Input Record</button></div>
          </form>

          <form id="harvest-form" class="stack">
            <div class="field-grid">
              <label>Crop Plan<select id="harvest-crop-plan-id" name="crop_plan_id" required></select></label>
              <label>Actual Yield Kg<input name="actual_yield_kg_total" type="number" step="0.01" placeholder="3200" required /></label>
              <label>Selling Price / Kg<input name="selling_price_per_kg" type="number" step="0.01" placeholder="35" required /></label>
              <label>Other Costs KSh<input name="other_costs_ksh" type="number" step="0.01" value="0" /></label>
            </div>
            <div class="form-actions">
              <button class="button" type="submit">Record Harvest</button>
              <button class="button alt" type="button" id="refresh-preview">Refresh Preview</button>
            </div>
          </form>
        </div>
      </article>
    </section>

    <section class="workspace">
      <article class="panel form-panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Record Manager</h2>
            <div class="panel-kicker">Basic edit and delete controls for stored records.</div>
          </div>
        </div>
        <div class="manager-grid">
          <div><div class="manager-title">Farmers</div><div class="activity" id="users-list"></div></div>
          <div><div class="manager-title">Crop Plans</div><div class="activity" id="plans-list"></div></div>
          <div><div class="manager-title">Inputs</div><div class="activity" id="inputs-list"></div></div>
          <div><div class="manager-title">Harvests</div><div class="activity" id="harvests-list"></div></div>
        </div>
      </article>

      <article class="panel form-panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Recent Activity</h2>
            <div class="panel-kicker">Immediate feedback from the authenticated workspace.</div>
          </div>
        </div>
        <div class="activity" id="activity-log">
          <div class="activity-item">No actions yet.</div>
        </div>
      </article>
    </section>
  </main>
`;

const setText = (id: string, value: string) => {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
};

const token = (): string | null => localStorage.getItem(storageKeys.token);
const activeUserId = (): string | null => localStorage.getItem(storageKeys.userId);
const activeCropPlanId = (): string | null => localStorage.getItem(storageKeys.cropPlanId);
const setActiveUserId = (id: string | null) => id && localStorage.setItem(storageKeys.userId, id);
const setActiveCropPlanId = (id: string | null) => id && localStorage.setItem(storageKeys.cropPlanId, id);

const fmtMoney = (value: number | null | undefined) =>
  value == null ? "--" : `KSh ${Number(value).toLocaleString()}`;

const fmtSignedPercent = (value: number | null | undefined) => {
  if (value == null) return "--";
  const num = Number(value);
  return `${num > 0 ? "+" : ""}${num.toLocaleString()}%`;
};

const toPayload = (form: HTMLFormElement): Record<string, string | number> => {
  const data = new FormData(form);
  const result: Record<string, string | number> = {};
  data.forEach((value, key) => {
    const text = String(value);
    if (text === "") return;
    if (["farm_size_acres", "acres", "quantity", "cost_ksh", "acres_applied", "actual_yield_kg_total", "selling_price_per_kg", "other_costs_ksh"].includes(key)) {
      result[key] = Number(text);
      return;
    }
    if (["season_year", "expected_yield_kg_per_acre"].includes(key)) {
      result[key] = Number(text);
      return;
    }
    result[key] = text;
  });
  return result;
};

const authHeaders = (): HeadersInit =>
  token() ? { Authorization: `Bearer ${token()}` } : {};

const apiFetch = async <T>(url: string, options: RequestInit = {}): Promise<T> => {
  const headers = { ...(options.headers || {}), ...authHeaders() };
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) throw new Error(await response.text());
  if (response.status === 204) return null as T;
  return response.json() as Promise<T>;
};

const logActivity = (message: string) => {
  const log = document.getElementById("activity-log");
  if (!log) return;
  const entry = document.createElement("div");
  entry.className = "activity-item";
  entry.textContent = message;
  if (log.children.length === 1 && /No actions/.test(log.children[0].textContent || "")) {
    log.innerHTML = "";
  }
  log.prepend(entry);
};

const fillSelect = <T extends { id: string }>(
  id: string,
  items: T[],
  labeler: (item: T) => string,
  selected?: string | null,
) => {
  const select = document.getElementById(id) as HTMLSelectElement | null;
  if (!select) return;
  select.innerHTML = items
    .map((item) => `<option value="${item.id}" ${item.id === selected ? "selected" : ""}>${labeler(item)}</option>`)
    .join("");
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
      : "No active farmer selected yet.",
  );
};

const renderTrend = (labels: string[], values: number[]) => {
  const width = 680;
  const height = 260;
  const left = 42;
  const right = 22;
  const top = 22;
  const bottom = 40;
  const plotWidth = width - left - right;
  const plotHeight = height - top - bottom;
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = Math.max(max - min, 1);
  const xStep = values.length > 1 ? plotWidth / (values.length - 1) : 0;
  const points = values.map((value, index) => [left + index * xStep, top + ((max - value) / range) * plotHeight]);
  const line = points.length ? `M ${points.map(([x, y]) => `${x} ${y}`).join(" L ")}` : "";
  const grid = [0, 0.25, 0.5, 0.75, 1]
    .map((tick) => {
      const y = top + tick * plotHeight;
      return `<line x1="${left}" y1="${y}" x2="${width - right}" y2="${y}" stroke="rgba(29,43,31,0.10)" stroke-dasharray="4 8" />`;
    })
    .join("");
  const dots = points
    .map(
      ([x, y], index) => `<circle cx="${x}" cy="${y}" r="5" fill="#f7f4ec" stroke="#2f6a3e" stroke-width="3"></circle>
       <text x="${x}" y="${y - 14}" text-anchor="middle" fill="#203328" font-size="12">${Number(values[index]).toLocaleString()}</text>`,
    )
    .join("");
  const first = points[0] || [left, top + plotHeight];
  const last = points[points.length - 1] || [left, top + plotHeight];
  const area = `M ${first[0]} ${top + plotHeight} L ${points.map(([x, y]) => `${x} ${y}`).join(" L ")} L ${last[0]} ${top + plotHeight} Z`;
  const trendGrid = document.getElementById("trend-grid");
  const trendLine = document.getElementById("trend-line");
  const trendArea = document.getElementById("trend-area");
  const trendDots = document.getElementById("trend-dots");
  if (trendGrid) trendGrid.innerHTML = grid;
  if (trendLine) trendLine.setAttribute("d", line);
  if (trendArea) trendArea.setAttribute("d", area);
  if (trendDots) trendDots.innerHTML = dots;
  (document.getElementById("trend-labels") as HTMLDivElement).innerHTML = labels.map((label) => `<span>${label}</span>`).join("");
};

const renderBars = (labels: string[], used: number[], recommended: number[]) => {
  const container = document.getElementById("fert-bars");
  if (!container) return;
  const max = Math.max(...used, ...recommended, 1);
  container.innerHTML = labels
    .map(
      (label, index) => `
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
        </div>`,
    )
    .join("");
};

const renderRecordList = (id: string, markup: string) => {
  const container = document.getElementById(id);
  if (container) container.innerHTML = markup || `<div class="activity-item">No records yet.</div>`;
};

const actionButtons = (kind: string, id: string) => `
  <div class="record-actions">
    <button class="edit" data-kind="${kind}" data-id="${id}" data-action="edit" type="button">Edit</button>
    <button class="delete" data-kind="${kind}" data-id="${id}" data-action="delete" type="button">Delete</button>
  </div>`;

const loadUsers = async () => {
  state.users = await apiFetch<User[]>("/users/");
  const selected = activeUserId() || state.users[0]?.id || null;
  if (selected) setActiveUserId(selected);
  fillSelect("crop-user-id", state.users, (u) => `${u.full_name || "Farmer"} (${u.phone})`, selected);
  fillSelect("input-user-id", state.users, (u) => `${u.full_name || "Farmer"} (${u.phone})`, selected);
  updateActiveBadge();
  renderRecordList(
    "users-list",
    state.users
      .map(
        (u) => `<div class="activity-item"><strong>${u.full_name || u.phone}</strong><br>${u.county} • ${u.soil_type || "soil pending"}${actionButtons("user", u.id)}</div>`,
      )
      .join(""),
  );
};

const loadCropPlans = async () => {
  state.cropPlans = await apiFetch<CropPlan[]>("/crop-plans/");
  const selected = activeCropPlanId() || state.cropPlans[0]?.id || null;
  if (selected) setActiveCropPlanId(selected);
  fillSelect("input-crop-plan-id", state.cropPlans, (p) => `${p.crop_type} • ${p.season_year} • ${p.acres} ac`, selected);
  fillSelect("harvest-crop-plan-id", state.cropPlans, (p) => `${p.crop_type} • ${p.season_year} • ${p.acres} ac`, selected);
  renderRecordList(
    "plans-list",
    state.cropPlans
      .map(
        (p) => `<div class="activity-item"><strong>${p.crop_type}</strong><br>${p.season_year} • ${p.acres} ac${actionButtons("crop-plan", p.id)}</div>`,
      )
      .join(""),
  );
};

const loadInputs = async () => {
  state.inputs = await apiFetch<InputUsage[]>("/inputs/");
  renderRecordList(
    "inputs-list",
    state.inputs
      .map(
        (i) => `<div class="activity-item"><strong>${i.item_name}</strong><br>${i.category} • KSh ${Number(i.cost_ksh).toLocaleString()}${actionButtons("input", i.id)}</div>`,
      )
      .join(""),
  );
};

const loadHarvests = async () => {
  state.harvests = await apiFetch<HarvestRecord[]>("/harvests/");
  renderRecordList(
    "harvests-list",
    state.harvests
      .map(
        (h) => `<div class="activity-item"><strong>${Number(h.actual_yield_kg_total || 0).toLocaleString()} kg</strong><br>KSh ${Number(h.selling_price_per_kg || 0).toLocaleString()}/kg${actionButtons("harvest", h.id)}</div>`,
      )
      .join(""),
  );
};

const refreshDashboard = async () => {
  const url = activeUserId()
    ? `/analytics/dashboard?user_id=${encodeURIComponent(activeUserId() as string)}`
    : "/analytics/dashboard";
  const data = await apiFetch<DashboardData>(url);
  setText("hero-roi", fmtSignedPercent(data.roi_percent));
  setText("hero-revenue", fmtMoney(data.total_revenue_ksh));
  setText("hero-fertilizer-signal", fmtSignedPercent(data.over_under_fert_percent));
  setText("hero-season", String(data.season_year ?? "--"));
  setText("stat-profit", fmtMoney(data.profit_loss_ksh));
  setText("stat-per-acre", fmtMoney(data.profit_per_acre_ksh));
  setText("stat-cost", fmtMoney(data.total_cost_ksh));
  setText("stat-crop", `${(data.crop_type || "crop").toUpperCase()} / ${data.acres || 0} ac`);
  const signal = Number(data.over_under_fert_percent || 0);
  setText(
    "signal-box",
    signal > 0
      ? `Field signal: fertilizer usage is ${signal.toLocaleString()}% above recommendation.`
      : signal < 0
        ? `Field signal: fertilizer usage is ${Math.abs(signal).toLocaleString()}% below recommendation.`
        : "Field signal: fertilizer usage is aligned with recommendation.",
  );
  renderTrend(data.seasons?.length ? data.seasons : ["Current"], data.profit_history?.length ? data.profit_history : [0]);
  const fert = data.fertilizer_comparison || { labels: [], used_per_acre: [], recommended_per_acre: [] };
  renderBars(
    fert.labels.length ? fert.labels : [data.crop_type || "Crop"],
    fert.used_per_acre.length ? fert.used_per_acre : [data.avg_fert_used || 0],
    fert.recommended_per_acre.length ? fert.recommended_per_acre : [data.recommended_fert || 0],
  );
};

const refreshAll = async () => {
  await loadUsers();
  await loadCropPlans();
  await loadInputs();
  await loadHarvests();
  await refreshDashboard();
};

const postJSON = <T>(url: string, payload: unknown) =>
  apiFetch<T>(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

const patchJSON = <T>(url: string, payload: unknown) =>
  apiFetch<T>(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

const deleteJSON = <T>(url: string) =>
  apiFetch<T>(url, { method: "DELETE" });

(document.getElementById("login-form") as HTMLFormElement).addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = await postJSON<AuthResponse>("/auth/login", toPayload(event.currentTarget as HTMLFormElement));
  localStorage.setItem(storageKeys.token, result.access_token);
  updateAuthStatus();
  logActivity("Logged in successfully.");
});

(document.getElementById("logout-button") as HTMLButtonElement).addEventListener("click", () => {
  localStorage.removeItem(storageKeys.token);
  updateAuthStatus();
  logActivity("Logged out.");
});

(document.getElementById("user-form") as HTMLFormElement).addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget as HTMLFormElement;
  const created = await postJSON<User>("/users/", toPayload(form));
  setActiveUserId(created.id);
  form.reset();
  (form.elements.namedItem("county") as HTMLInputElement).value = "Uasin Gishu";
  (form.elements.namedItem("soil_type") as HTMLSelectElement).value = "loam";
  await refreshAll();
  logActivity(`Created farmer ${created.full_name || created.phone}.`);
});

(document.getElementById("crop-plan-form") as HTMLFormElement).addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget as HTMLFormElement;
  const payload = toPayload(form);
  payload.user_id = (document.getElementById("crop-user-id") as HTMLSelectElement).value;
  const created = await postJSON<CropPlan>("/crop-plans/", payload);
  setActiveUserId(String(payload.user_id));
  setActiveCropPlanId(created.id);
  form.reset();
  (form.elements.namedItem("season_year") as HTMLInputElement).value = "2026";
  await refreshAll();
  logActivity(`Created crop plan for ${created.crop_type}.`);
});

(document.getElementById("input-form") as HTMLFormElement).addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget as HTMLFormElement;
  const payload = toPayload(form);
  payload.user_id = (document.getElementById("input-user-id") as HTMLSelectElement).value;
  payload.crop_plan_id = (document.getElementById("input-crop-plan-id") as HTMLSelectElement).value;
  const created = await postJSON<InputUsage>("/inputs/", payload);
  setActiveUserId(String(payload.user_id));
  setActiveCropPlanId(String(payload.crop_plan_id));
  form.reset();
  await refreshAll();
  logActivity(`Added input ${created.item_name}.`);
});

(document.getElementById("harvest-form") as HTMLFormElement).addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget as HTMLFormElement;
  const payload = toPayload(form);
  payload.crop_plan_id = (document.getElementById("harvest-crop-plan-id") as HTMLSelectElement).value;
  const created = await postJSON<HarvestRecord>("/harvests/", payload);
  setActiveCropPlanId(String(payload.crop_plan_id));
  form.reset();
  (form.elements.namedItem("other_costs_ksh") as HTMLInputElement).value = "0";
  await refreshAll();
  logActivity(`Recorded harvest ${created.actual_yield_kg_total || 0} kg.`);
});

(document.getElementById("refresh-preview") as HTMLButtonElement).addEventListener("click", () => {
  void refreshDashboard();
});

document.addEventListener("click", async (event) => {
  const target = (event.target as HTMLElement).closest("button[data-action]") as HTMLButtonElement | null;
  if (!target) return;
  const { kind, id, action } = target.dataset;
  if (!kind || !id || !action) return;

  if (action === "delete") {
    if (!window.confirm(`Delete this ${kind}?`)) return;
    const endpoint =
      kind === "user"
        ? `/users/${id}`
        : kind === "crop-plan"
          ? `/crop-plans/${id}`
          : kind === "input"
            ? `/inputs/${id}`
            : `/harvests/${id}`;
    await deleteJSON<{ status: string }>(endpoint);
    await refreshAll();
    logActivity(`Deleted ${kind}.`);
    return;
  }

  if (action === "edit") {
    const record =
      kind === "user"
        ? state.users.find((item) => item.id === id)
        : kind === "crop-plan"
          ? state.cropPlans.find((item) => item.id === id)
          : kind === "input"
            ? state.inputs.find((item) => item.id === id)
            : state.harvests.find((item) => item.id === id);
    if (!record) return;
    if (kind === "user") {
      const user = record as User;
      const full_name = window.prompt("Farmer name", user.full_name || "");
      const county = window.prompt("County", user.county || "");
      if (full_name !== null && county !== null) await patchJSON<User>(`/users/${id}`, { full_name, county });
    } else if (kind === "crop-plan") {
      const plan = record as CropPlan;
      const crop_type = window.prompt("Crop type", plan.crop_type);
      const acres = window.prompt("Acres", String(plan.acres));
      if (crop_type !== null && acres !== null) await patchJSON<CropPlan>(`/crop-plans/${id}`, { crop_type, acres: Number(acres) });
    } else if (kind === "input") {
      const input = record as InputUsage;
      const cost_ksh = window.prompt("Cost KSh", String(input.cost_ksh));
      const quantity = window.prompt("Quantity", String(input.quantity ?? ""));
      if (cost_ksh !== null) {
        await patchJSON<InputUsage>(`/inputs/${id}`, {
          cost_ksh: Number(cost_ksh),
          quantity: quantity === "" ? null : Number(quantity),
        });
      }
    } else {
      const harvest = record as HarvestRecord;
      const selling_price_per_kg = window.prompt("Selling price per kg", String(harvest.selling_price_per_kg ?? ""));
      const actual_yield_kg_total = window.prompt("Actual yield kg total", String(harvest.actual_yield_kg_total ?? ""));
      if (selling_price_per_kg !== null) {
        await patchJSON<HarvestRecord>(`/harvests/${id}`, {
          selling_price_per_kg: Number(selling_price_per_kg),
          actual_yield_kg_total: Number(actual_yield_kg_total),
        });
      }
    }
    await refreshAll();
    logActivity(`Updated ${kind}.`);
  }
});

updateAuthStatus();
void refreshAll().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : "Unknown startup issue";
  logActivity(`Startup issue: ${message}`);
  setText("signal-box", "Live dashboard preview is temporarily unavailable.");
});
