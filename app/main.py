from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.database import init_db
from app.routers.analytics import router as analytics_router
from app.routers.crop_plans import router as crop_plans_router
from app.routers.harvests import router as harvests_router
from app.routers.inputs import router as inputs_router
from app.routers.users import router as users_router

app = FastAPI(title="AgriProfit MVP - Uasin Gishu", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>AgriProfit MVP</title>
        <style>
          :root {
            --bg: #f5f1e8;
            --ink: #1d2b1f;
            --muted: #5f6f61;
            --card: rgba(255, 251, 243, 0.82);
            --line: rgba(29, 43, 31, 0.12);
            --primary: #2f6a3e;
            --accent: #d58a2a;
            --deep: #203328;
            --rose: #b44b34;
            --sky: #dbe8e0;
          }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            font-family: Georgia, "Times New Roman", serif;
            color: var(--ink);
            background:
              radial-gradient(circle at top left, rgba(213, 138, 42, 0.28), transparent 28%),
              radial-gradient(circle at 85% 18%, rgba(47, 106, 62, 0.18), transparent 24%),
              linear-gradient(135deg, #f7f4ec 0%, #ebe1ce 48%, #d9e0d0 100%);
            min-height: 100vh;
          }
          .shell {
            max-width: 1180px;
            margin: 0 auto;
            padding: 32px 20px 56px;
          }
          .masthead {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
          }
          .brand {
            display: flex;
            align-items: center;
            gap: 12px;
          }
          .brand-mark {
            width: 44px;
            height: 44px;
            border-radius: 14px;
            background:
              linear-gradient(135deg, rgba(47, 106, 62, 0.95), rgba(213, 138, 42, 0.92));
            position: relative;
            box-shadow: 0 10px 24px rgba(47, 106, 62, 0.24);
          }
          .brand-mark::before,
          .brand-mark::after {
            content: "";
            position: absolute;
            background: rgba(255, 251, 243, 0.92);
            border-radius: 999px;
          }
          .brand-mark::before {
            width: 20px;
            height: 20px;
            left: 12px;
            top: 8px;
            clip-path: ellipse(50% 65% at 50% 50%);
            transform: rotate(-28deg);
          }
          .brand-mark::after {
            width: 2px;
            height: 18px;
            left: 21px;
            top: 18px;
          }
          .brand-name {
            font-size: 1.02rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--deep);
          }
          .brand-note {
            font-size: 0.85rem;
            color: var(--muted);
          }
          .status-pill {
            font-size: 0.85rem;
            border-radius: 999px;
            padding: 10px 14px;
            border: 1px solid rgba(32, 51, 40, 0.12);
            background: rgba(255,255,255,0.56);
            color: var(--deep);
          }
          .hero {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 22px;
            align-items: stretch;
          }
          .panel {
            background: var(--card);
            border: 1px solid var(--line);
            backdrop-filter: blur(12px);
            border-radius: 28px;
            box-shadow: 0 24px 60px rgba(43, 54, 35, 0.10);
          }
          .hero-copy {
            padding: 34px;
          }
          .eyebrow {
            display: inline-block;
            font-size: 12px;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--primary);
            background: rgba(47, 106, 62, 0.08);
            border: 1px solid rgba(47, 106, 62, 0.14);
            border-radius: 999px;
            padding: 8px 12px;
            margin-bottom: 18px;
          }
          h1 {
            margin: 0;
            font-size: clamp(2.5rem, 5vw, 5.2rem);
            line-height: 0.92;
            font-weight: 700;
            max-width: 9ch;
          }
          .subtitle {
            margin: 18px 0 28px;
            max-width: 58ch;
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.7;
          }
          .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
          }
          .btn {
            text-decoration: none;
            border-radius: 999px;
            padding: 14px 18px;
            font-size: 0.96rem;
            transition: transform 160ms ease, box-shadow 160ms ease;
          }
          .btn:hover { transform: translateY(-1px); }
          .btn-primary {
            background: var(--deep);
            color: #f7f4ec;
            box-shadow: 0 14px 28px rgba(32, 51, 40, 0.20);
          }
          .btn-secondary {
            color: var(--deep);
            border: 1px solid rgba(32, 51, 40, 0.18);
            background: rgba(255,255,255,0.52);
          }
          .hero-side {
            padding: 22px;
            display: grid;
            gap: 14px;
            background:
              linear-gradient(180deg, rgba(32, 51, 40, 0.94), rgba(47, 106, 62, 0.88)),
              var(--deep);
            color: #f7f4ec;
          }
          .hero-side h2 {
            margin: 0;
            font-size: 1.1rem;
            letter-spacing: 0.02em;
          }
          .metric {
            display: flex;
            justify-content: space-between;
            align-items: end;
            padding: 14px 0;
            border-bottom: 1px solid rgba(255,255,255,0.12);
          }
          .metric:last-child { border-bottom: 0; }
          .metric-label {
            font-size: 0.9rem;
            color: rgba(247, 244, 236, 0.74);
          }
          .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
          }
          .dashboard {
            margin-top: 22px;
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 18px;
          }
          .dashboard-panel {
            padding: 24px;
          }
          .panel-head {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: start;
            margin-bottom: 18px;
          }
          .panel-title {
            margin: 0;
            font-size: 1.25rem;
          }
          .panel-kicker {
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.55;
          }
          .stats {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 18px;
          }
          .stat {
            border-radius: 20px;
            padding: 16px;
            background: rgba(255,255,255,0.48);
            border: 1px solid rgba(29, 43, 31, 0.08);
          }
          .stat-label {
            color: var(--muted);
            font-size: 0.82rem;
            margin-bottom: 8px;
          }
          .stat-value {
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--deep);
          }
          .chart-box {
            padding: 14px 14px 10px;
            border-radius: 24px;
            background: linear-gradient(180deg, rgba(255,255,255,0.62), rgba(235, 241, 232, 0.82));
            border: 1px solid rgba(29, 43, 31, 0.08);
          }
          .chart-labels {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin-top: 10px;
            color: var(--muted);
            font-size: 0.82rem;
          }
          .bars {
            display: grid;
            gap: 14px;
          }
          .bar-row {
            display: grid;
            grid-template-columns: 92px 1fr;
            gap: 12px;
            align-items: center;
          }
          .bar-name {
            font-size: 0.9rem;
            color: var(--deep);
          }
          .bar-stack {
            display: grid;
            gap: 8px;
          }
          .bar-track {
            position: relative;
            height: 16px;
            border-radius: 999px;
            background: rgba(32, 51, 40, 0.08);
            overflow: hidden;
          }
          .bar {
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            border-radius: 999px;
          }
          .bar-used { background: linear-gradient(90deg, var(--accent), #e5a650); }
          .bar-recommended { background: linear-gradient(90deg, var(--primary), #5f946b); }
          .bar-meta {
            display: flex;
            gap: 14px;
            font-size: 0.8rem;
            color: var(--muted);
          }
          .legend {
            display: flex;
            gap: 16px;
            margin-top: 14px;
            font-size: 0.82rem;
            color: var(--muted);
          }
          .legend span {
            display: inline-flex;
            align-items: center;
            gap: 8px;
          }
          .legend i {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 999px;
          }
          .signal {
            font-size: 0.92rem;
            padding: 10px 12px;
            border-radius: 14px;
            background: rgba(180, 75, 52, 0.08);
            border: 1px solid rgba(180, 75, 52, 0.14);
            color: var(--rose);
          }
          .workspace {
            margin-top: 22px;
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 18px;
          }
          .form-panel {
            padding: 24px;
          }
          .stack {
            display: grid;
            gap: 12px;
          }
          .field-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
          }
          label {
            display: grid;
            gap: 6px;
            font-size: 0.9rem;
            color: var(--deep);
          }
          input, select, textarea {
            width: 100%;
            border-radius: 14px;
            border: 1px solid rgba(29, 43, 31, 0.12);
            background: rgba(255,255,255,0.72);
            padding: 12px 13px;
            font: inherit;
            color: var(--deep);
          }
          textarea { min-height: 96px; resize: vertical; }
          .form-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
          }
          .button {
            border: 0;
            border-radius: 999px;
            background: var(--primary);
            color: #f7f4ec;
            padding: 12px 16px;
            font: inherit;
            cursor: pointer;
          }
          .button.alt {
            background: rgba(32, 51, 40, 0.1);
            color: var(--deep);
          }
          .helper {
            color: var(--muted);
            font-size: 0.85rem;
            line-height: 1.5;
          }
          .activity {
            display: grid;
            gap: 10px;
          }
          .activity-item {
            padding: 12px 14px;
            border-radius: 16px;
            border: 1px solid rgba(29, 43, 31, 0.08);
            background: rgba(255,255,255,0.5);
            color: var(--deep);
            font-size: 0.9rem;
          }
          .active-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
            border-radius: 999px;
            padding: 10px 12px;
            background: rgba(47, 106, 62, 0.1);
            color: var(--primary);
            font-size: 0.85rem;
          }
          .grid {
            margin-top: 22px;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
          }
          .card {
            padding: 22px;
          }
          .card h3 {
            margin: 0 0 10px;
            font-size: 1.1rem;
          }
          .card p {
            margin: 0;
            color: var(--muted);
            line-height: 1.65;
          }
          .callout {
            margin-top: 22px;
            padding: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
          }
          .callout strong {
            display: block;
            font-size: 1.3rem;
            margin-bottom: 6px;
          }
          .callout span {
            color: var(--muted);
            line-height: 1.6;
          }
          .mini {
            border-radius: 20px;
            background: rgba(213, 138, 42, 0.10);
            border: 1px solid rgba(213, 138, 42, 0.18);
            padding: 16px 18px;
            min-width: 220px;
          }
          .mini code {
            font-size: 0.92rem;
            color: var(--deep);
          }
          @media (max-width: 920px) {
            .hero, .grid, .dashboard, .workspace { grid-template-columns: 1fr; }
            .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .callout { flex-direction: column; align-items: flex-start; }
          }
          @media (max-width: 640px) {
            .masthead { flex-direction: column; align-items: flex-start; gap: 10px; }
            .stats { grid-template-columns: 1fr; }
            .bar-row { grid-template-columns: 1fr; }
            .field-grid { grid-template-columns: 1fr; }
          }
        </style>
      </head>
      <body>
        <main class="shell">
          <header class="masthead">
            <div class="brand">
              <div class="brand-mark"></div>
              <div>
                <div class="brand-name">AgriProfit</div>
                <div class="brand-note">Profit-first farm intelligence</div>
              </div>
            </div>
            <div class="status-pill">Live preview from <code>/analytics/dashboard</code></div>
          </header>

          <section class="hero">
            <div class="panel hero-copy">
              <div class="eyebrow">AgriProfit MVP</div>
              <h1>Farm intelligence with a local point of view.</h1>
              <p class="subtitle">
                This is not a generic backend stub anymore. AgriProfit now has a clear identity:
                a decision engine for crop planning, fertilizer guidance, and profit tracking
                built around real farm records and Uasin Gishu-oriented recommendations.
              </p>
              <div class="actions">
                <a class="btn btn-primary" href="/docs">Open API Docs</a>
                <a class="btn btn-secondary" href="/analytics/dashboard">View Raw Dashboard</a>
                <a class="btn btn-secondary" href="/api">Raw API Status</a>
              </div>
            </div>

            <aside class="panel hero-side">
              <h2>Current Focus</h2>
              <div class="metric">
                <div class="metric-label">Live ROI</div>
                <div class="metric-value" id="hero-roi">--</div>
              </div>
              <div class="metric">
                <div class="metric-label">Tracked Revenue</div>
                <div class="metric-value" id="hero-revenue">--</div>
              </div>
              <div class="metric">
                <div class="metric-label">Fertilizer Signal</div>
                <div class="metric-value" id="hero-fertilizer-signal">--</div>
              </div>
              <div class="metric">
                <div class="metric-label">Active Season</div>
                <div class="metric-value" id="hero-season">--</div>
              </div>
            </aside>
          </section>

          <section class="dashboard">
            <article class="panel dashboard-panel">
              <div class="panel-head">
                <div>
                  <h2 class="panel-title">Live Profit Canvas</h2>
                  <div class="panel-kicker">
                    A browser preview wired directly to your current dashboard endpoint.
                  </div>
                </div>
                <div class="signal" id="signal-box">Loading live field signal...</div>
              </div>

              <div class="stats">
                <div class="stat">
                  <div class="stat-label">Profit / Loss</div>
                  <div class="stat-value" id="stat-profit">--</div>
                </div>
                <div class="stat">
                  <div class="stat-label">Per Acre</div>
                  <div class="stat-value" id="stat-per-acre">--</div>
                </div>
                <div class="stat">
                  <div class="stat-label">Total Cost</div>
                  <div class="stat-value" id="stat-cost">--</div>
                </div>
                <div class="stat">
                  <div class="stat-label">Crop / Acres</div>
                  <div class="stat-value" id="stat-crop">--</div>
                </div>
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
                  <div class="panel-kicker">
                    Compare field usage against recommendation and spot over-application quickly.
                  </div>
                </div>
              </div>
              <div class="bars" id="fert-bars"></div>
              <div class="legend">
                <span><i style="background: var(--accent)"></i> Used per acre</span>
                <span><i style="background: var(--primary)"></i> Recommended</span>
              </div>
            </article>
          </section>

          <section class="workspace">
            <article class="panel form-panel">
              <div class="panel-head">
                <div>
                  <h2 class="panel-title">Field Studio</h2>
                  <div class="panel-kicker">
                    Create real records directly here. SQLite is now the default local store.
                  </div>
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
                  <div class="form-actions">
                    <button class="button" type="submit">Create Farmer</button>
                    <span class="helper">This farmer becomes the active dashboard context.</span>
                  </div>
                </form>

                <form id="crop-plan-form" class="stack">
                  <div class="field-grid">
                    <label>Farmer
                      <select id="crop-user-id" name="user_id" required></select>
                    </label>
                    <label>Crop Type<input name="crop_type" placeholder="maize" required /></label>
                    <label>Acres<input name="acres" type="number" step="0.01" placeholder="2" required /></label>
                    <label>Season Year<input name="season_year" type="number" value="2026" required /></label>
                    <label>Planting Date<input name="planting_date" type="date" /></label>
                    <label>Expected Yield Kg/Acre<input name="expected_yield_kg_per_acre" type="number" placeholder="1800" /></label>
                  </div>
                  <div class="form-actions">
                    <button class="button" type="submit">Create Crop Plan</button>
                  </div>
                </form>
              </div>
            </article>

            <article class="panel form-panel">
              <div class="panel-head">
                <div>
                  <h2 class="panel-title">Season Operations</h2>
                  <div class="panel-kicker">
                    Add inputs and harvests, then watch the live dashboard shift.
                  </div>
                </div>
              </div>

              <div class="stack">
                <form id="input-form" class="stack">
                  <div class="field-grid">
                    <label>Farmer
                      <select id="input-user-id" name="user_id" required></select>
                    </label>
                    <label>Crop Plan
                      <select id="input-crop-plan-id" name="crop_plan_id" required></select>
                    </label>
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
                  <div class="form-actions">
                    <button class="button" type="submit">Add Input Record</button>
                  </div>
                </form>

                <form id="harvest-form" class="stack">
                  <div class="field-grid">
                    <label>Crop Plan
                      <select id="harvest-crop-plan-id" name="crop_plan_id" required></select>
                    </label>
                    <label>Actual Yield Kg<input name="actual_yield_kg_total" type="number" step="0.01" placeholder="3200" required /></label>
                    <label>Selling Price / Kg<input name="selling_price_per_kg" type="number" step="0.01" placeholder="35" required /></label>
                    <label>Other Costs KSh<input name="other_costs_ksh" type="number" step="0.01" value="0" /></label>
                  </div>
                  <div class="form-actions">
                    <button class="button" type="submit">Record Harvest</button>
                    <button class="button alt" type="button" id="refresh-preview">Refresh Preview</button>
                  </div>
                </form>

                <div>
                  <div class="helper">Recent activity</div>
                  <div class="activity" id="activity-log">
                    <div class="activity-item">No records created from the page yet.</div>
                  </div>
                </div>
              </div>
            </article>
          </section>

          <section class="grid">
            <article class="panel card">
              <h3>Profit Story</h3>
              <p>
                Track what each season actually produced after input spend, transport,
                and harvest costs instead of stopping at yield alone.
              </p>
            </article>
            <article class="panel card">
              <h3>Fertilizer Logic</h3>
              <p>
                Move beyond generic recommendations with crop, soil, acreage, and county-aware
                fertilizer guidance that can later be tied to persisted records.
              </p>
            </article>
            <article class="panel card">
              <h3>Structured Farm Data</h3>
              <p>
                Users, crop plans, input usage, harvests, and recommendations now sit in a
                coherent schema ready for SQLite or PostgreSQL.
              </p>
            </article>
          </section>

          <section class="panel callout">
            <div>
              <strong>Built for a real product, not just a demo endpoint.</strong>
              <span>
                You can keep evolving this into a full app later, but the browser experience now
                already feels like AgriProfit instead of a blank JSON response.
              </span>
            </div>
            <div class="mini">
              <code>GET /analytics/fertilizer-recommendation</code><br />
              <code>GET /analytics/dashboard</code><br />
              <code>POST /crop-plans/</code>
            </div>
          </section>
        </main>
        <script>
          const storageKeys = {
            userId: "agriprofit.activeUserId",
            cropPlanId: "agriprofit.activeCropPlanId",
          };
          let state = {
            users: [],
            cropPlans: [],
          };

          const fmtMoney = (value) => {
            if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
            return "KSh " + Number(value).toLocaleString();
          };

          const fmtSignedPercent = (value) => {
            if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
            const num = Number(value);
            return (num > 0 ? "+" : "") + num.toLocaleString() + "%";
          };

          const setText = (id, value) => {
            const node = document.getElementById(id);
            if (node) node.textContent = value;
          };

          const logActivity = (message) => {
            const log = document.getElementById("activity-log");
            const entry = document.createElement("div");
            entry.className = "activity-item";
            entry.textContent = message;
            if (log.children.length === 1 && /No records/.test(log.children[0].textContent)) {
              log.innerHTML = "";
            }
            log.prepend(entry);
          };

          const getActiveUserId = () => localStorage.getItem(storageKeys.userId);
          const setActiveUserId = (value) => {
            if (value) {
              localStorage.setItem(storageKeys.userId, value);
            }
          };
          const getActiveCropPlanId = () => localStorage.getItem(storageKeys.cropPlanId);
          const setActiveCropPlanId = (value) => {
            if (value) {
              localStorage.setItem(storageKeys.cropPlanId, value);
            }
          };

          const toPayload = (form) => {
            const raw = Object.fromEntries(new FormData(form).entries());
            return Object.fromEntries(
              Object.entries(raw)
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
          };

          const fillSelect = (id, items, makeLabel, activeId) => {
            const select = document.getElementById(id);
            if (!select) return;
            const currentValue = activeId || select.value;
            select.innerHTML = items.map((item) => {
              const selected = item.id === currentValue ? "selected" : "";
              return `<option value="${item.id}" ${selected}>${makeLabel(item)}</option>`;
            }).join("");
          };

          const updateActiveBadge = () => {
            const activeUser = state.users.find((user) => user.id === getActiveUserId()) || state.users[0];
            if (activeUser && !getActiveUserId()) {
              setActiveUserId(activeUser.id);
            }
            const badge = document.getElementById("active-user-badge");
            if (!badge) return;
            if (!activeUser) {
              badge.textContent = "No active farmer selected yet.";
              return;
            }
            badge.textContent = `Active farmer: ${(activeUser.full_name || activeUser.phone)} • ${activeUser.county} • ${activeUser.soil_type || "soil pending"}`;
          };

          const loadUsers = async () => {
            const response = await fetch("/users/");
            state.users = await response.json();
            const activeId = getActiveUserId() || (state.users[0] && state.users[0].id);
            if (activeId) setActiveUserId(activeId);
            fillSelect("crop-user-id", state.users, (user) => `${user.full_name || "Farmer"} (${user.phone})`, activeId);
            fillSelect("input-user-id", state.users, (user) => `${user.full_name || "Farmer"} (${user.phone})`, activeId);
            updateActiveBadge();
          };

          const loadCropPlans = async () => {
            const response = await fetch("/crop-plans/");
            state.cropPlans = await response.json();
            const activeId = getActiveCropPlanId() || (state.cropPlans[0] && state.cropPlans[0].id);
            if (activeId) setActiveCropPlanId(activeId);
            fillSelect(
              "input-crop-plan-id",
              state.cropPlans,
              (plan) => `${plan.crop_type} • ${plan.season_year} • ${plan.acres} ac`,
              activeId
            );
            fillSelect(
              "harvest-crop-plan-id",
              state.cropPlans,
              (plan) => `${plan.crop_type} • ${plan.season_year} • ${plan.acres} ac`,
              activeId
            );
          };

          const renderTrend = (labels, values) => {
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

            const points = values.map((value, index) => {
              const x = left + index * xStep;
              const y = top + ((max - value) / range) * plotHeight;
              return [x, y];
            });

            const line = points.length
              ? "M " + points.map(([x, y]) => x + " " + y).join(" L ")
              : "";
            const grid = [0, 0.25, 0.5, 0.75, 1].map((tick) => {
              const y = top + tick * plotHeight;
              return '<line x1="' + left + '" y1="' + y + '" x2="' + (width - right) + '" y2="' + y + '" stroke="rgba(29,43,31,0.10)" stroke-dasharray="4 8" />';
            }).join("");

            const dots = points.map(([x, y], index) => (
              '<circle cx="' + x + '" cy="' + y + '" r="5" fill="#f7f4ec" stroke="#2f6a3e" stroke-width="3"></circle>' +
              '<text x="' + x + '" y="' + (y - 14) + '" text-anchor="middle" fill="#203328" font-size="12">' +
              Number(values[index]).toLocaleString() +
              "</text>"
            )).join("");

            const firstPoint = points[0] || [left, top + plotHeight];
            const lastPoint = points[points.length - 1] || [left, top + plotHeight];
            const area = "M " + firstPoint[0] + " " + (top + plotHeight) + " L " +
              points.map(([x, y]) => x + " " + y).join(" L ") +
              " L " + lastPoint[0] + " " + (top + plotHeight) + " Z";

            document.getElementById("trend-grid").innerHTML = grid;
            document.getElementById("trend-line").setAttribute("d", line);
            document.getElementById("trend-area").setAttribute("d", area);
            document.getElementById("trend-dots").innerHTML = dots;
            document.getElementById("trend-labels").innerHTML = labels.map((label) => "<span>" + label + "</span>").join("");
          };

          const renderBars = (labels, used, recommended) => {
            const container = document.getElementById("fert-bars");
            const max = Math.max(...used, ...recommended, 1);
            container.innerHTML = labels.map((label, index) => {
              const usedWidth = Math.max((Number(used[index] || 0) / max) * 100, 3);
              const recWidth = Math.max((Number(recommended[index] || 0) / max) * 100, 3);
              return `
                <div class="bar-row">
                  <div class="bar-name">${label}</div>
                  <div class="bar-stack">
                    <div class="bar-track"><div class="bar bar-used" style="width:${usedWidth}%"></div></div>
                    <div class="bar-track"><div class="bar bar-recommended" style="width:${recWidth}%"></div></div>
                    <div class="bar-meta">
                      <span>Used: ${Number(used[index] || 0).toLocaleString()} kg</span>
                      <span>Recommended: ${Number(recommended[index] || 0).toLocaleString()} kg</span>
                    </div>
                  </div>
                </div>
              `;
            }).join("");
          };

          const refreshDashboard = async () => {
            const activeUserId = getActiveUserId();
            const url = activeUserId ? `/analytics/dashboard?user_id=${encodeURIComponent(activeUserId)}` : "/analytics/dashboard";
            return fetch(url)
            .then((response) => response.json())
            .then((data) => {
              setText("hero-roi", fmtSignedPercent(data.roi_percent));
              setText("hero-revenue", fmtMoney(data.total_revenue_ksh));
              setText("hero-fertilizer-signal", fmtSignedPercent(data.over_under_fert_percent));
              setText("hero-season", String(data.season_year ?? "--"));

              setText("stat-profit", fmtMoney(data.profit_loss_ksh));
              setText("stat-per-acre", fmtMoney(data.profit_per_acre_ksh));
              setText("stat-cost", fmtMoney(data.total_cost_ksh));
              setText("stat-crop", ((data.crop_type || "Crop") + " / " + (data.acres || 0) + " ac").toUpperCase());

              const signal = Number(data.over_under_fert_percent || 0);
              const signalText = signal > 0
                ? "Field signal: fertilizer usage is " + signal.toLocaleString() + "% above recommendation."
                : signal < 0
                  ? "Field signal: fertilizer usage is " + Math.abs(signal).toLocaleString() + "% below recommendation."
                  : "Field signal: fertilizer usage is aligned with recommendation.";
              setText("signal-box", signalText);

              const seasons = Array.isArray(data.seasons) && data.seasons.length ? data.seasons : ["Current"];
              const history = Array.isArray(data.profit_history) && data.profit_history.length ? data.profit_history : [0];
              renderTrend(seasons, history.map(Number));

              const fert = data.fertilizer_comparison || {};
              const labels = Array.isArray(fert.labels) && fert.labels.length ? fert.labels : [data.crop_type || "Crop"];
              const used = Array.isArray(fert.used_per_acre) && fert.used_per_acre.length ? fert.used_per_acre : [data.avg_fert_used || 0];
              const recommended = Array.isArray(fert.recommended_per_acre) && fert.recommended_per_acre.length ? fert.recommended_per_acre : [data.recommended_fert || 0];
              renderBars(labels, used.map(Number), recommended.map(Number));
            })
            .catch(() => {
              setText("signal-box", "Live dashboard preview is temporarily unavailable.");
            });
          };

          const postJSON = async (url, payload) => {
            const response = await fetch(url, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
            });
            if (!response.ok) {
              const detail = await response.text();
              throw new Error(detail || "Request failed");
            }
            return response.json();
          };

          document.getElementById("user-form").addEventListener("submit", async (event) => {
            event.preventDefault();
            const payload = toPayload(event.currentTarget);
            const created = await postJSON("/users/", payload);
            setActiveUserId(created.id);
            event.currentTarget.reset();
            event.currentTarget.county.value = "Uasin Gishu";
            event.currentTarget.soil_type.value = "loam";
            await loadUsers();
            await refreshDashboard();
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
            await loadCropPlans();
            await refreshDashboard();
            logActivity(`Created crop plan for ${created.crop_type} in ${created.season_year}.`);
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
            await refreshDashboard();
            logActivity(`Added input ${created.item_name} (${created.category}).`);
          });

          document.getElementById("harvest-form").addEventListener("submit", async (event) => {
            event.preventDefault();
            const payload = toPayload(event.currentTarget);
            payload.crop_plan_id = document.getElementById("harvest-crop-plan-id").value;
            const created = await postJSON("/harvests/", payload);
            setActiveCropPlanId(payload.crop_plan_id);
            event.currentTarget.reset();
            event.currentTarget.other_costs_ksh.value = "0";
            await refreshDashboard();
            logActivity(`Recorded harvest ${created.actual_yield_kg_total} kg at KSh ${created.selling_price_per_kg}/kg.`);
          });

          document.getElementById("refresh-preview").addEventListener("click", refreshDashboard);

          Promise.resolve()
            .then(loadUsers)
            .then(loadCropPlans)
            .then(refreshDashboard);
        </script>
      </body>
    </html>
    """


@app.get("/api")
def api_status():
    return {
        "message": "AgriProfit Python API is running.",
        "docs": "/docs",
        "dashboard": "/analytics/dashboard",
    }


app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(crop_plans_router, prefix="/crop-plans", tags=["crop-plans"])
app.include_router(inputs_router, prefix="/inputs", tags=["inputs"])
app.include_router(harvests_router, prefix="/harvests", tags=["harvests"])
