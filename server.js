// server.js
import express from "express";
import dotenv from "dotenv";
import YahooFantasy from "yahoo-fantasy";
import cors from "cors";

dotenv.config();
const app = express();
app.set("json spaces", 2); // pretty JSON in dev

// Allow your local Next app + (optionally) any origin during dev
app.use(cors({
  origin: [
    "http://localhost:3000",         // Next dev
    "https://localhost:3000",        // alt
    "https://132287592b77.ngrok-free.app" // optional
  ],
  methods: ["GET", "POST", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization"],
  //credentials: false,
}));

const {
  Y_CLIENT_ID,
  Y_CLIENT_SECRET,
  REDIRECT_URI,
  TARGET_LEAGUE_ID,
  PORT = 3001,
  FRONTEND_BASE = "http://localhost:3000",
} = process.env;

// In-memory token store (MVP). Move to DB later.
let TOKENS = { access_token: null, refresh_token: null, expires_at: 0 };

// ---- OAuth: build consent URL (HTTPS redirect via ngrok / reverse proxy) ----
const authURL = new URL("https://api.login.yahoo.com/oauth2/request_auth");
authURL.searchParams.set("client_id", Y_CLIENT_ID || "");
authURL.searchParams.set("redirect_uri", REDIRECT_URI || "");
authURL.searchParams.set("response_type", "code");
authURL.searchParams.set("language", "en-us");


// ---- Yahoo raw GET helper (uses your bearer access token) ----
async function yGet(path) {
  if (!TOKENS.access_token) throw new Error("No access token");
  const base = "https://fantasysports.yahooapis.com/fantasy/v2/";
  const url = `${base}${path}${path.includes("?") ? "&" : "?"}format=json`;
  const r = await fetch(url, {
    headers: { Authorization: `Bearer ${TOKENS.access_token}` },
  });
  const data = await r.json();
  if (!r.ok) {
    const err = new Error("Yahoo API error");
    err.data = data;
    throw err;
  }
  return data;
}

// ---- tiny deep finder to pull nested values from Yahoo's arrayish JSON ----
function findDeep(obj, key) {
  if (!obj || typeof obj !== "object") return undefined;
  if (Object.prototype.hasOwnProperty.call(obj, key)) return obj[key];
  for (const k of Object.keys(obj)) {
    const v = findDeep(obj[k], key);
    if (v !== undefined) return v;
  }
  return undefined;
}

// Pull league players for a given status (FA = free agents, W = waivers) with paging
async function fetchLeaguePlayersByStatus(leagueKey, status) {
  const pageSize = 25; // Yahoo paginates in 25s
  let start = 0;
  const out = [];

  while (true) {
    const path = `league/${encodeURIComponent(leagueKey)}/players;status=${status};start=${start};count=${pageSize};out=ownership,stats`;
    const data = await yGet(path);

    // Yahoo's array-like objects: players live at fantasy_content.league[1].players
    const leagueRoot = data?.fantasy_content?.league;
    const playersObj = leagueRoot?.[1]?.players || leagueRoot?.["1"]?.players || null;
    const count = Number(playersObj?.count ?? 0);
    if (!count) break;

    // Collect players in this page
    for (let i = 0; i < count; i++) {
      const pNode = playersObj?.[String(i)]?.player;
      if (!pNode) continue;
      out.push(pNode);
    }

    if (count < pageSize) break; // last page
    start += pageSize;
  }

  return out;
}

// Deep find the first property with a given key in any nested object/array
function deepFind(obj, key) {
  if (obj == null) return undefined;
  if (typeof obj !== "object") return undefined;
  if (Object.prototype.hasOwnProperty.call(obj, key)) return obj[key];

  if (Array.isArray(obj)) {
    for (const item of obj) {
      const v = deepFind(item, key);
      if (v !== undefined) return v;
    }
  } else {
    for (const k of Object.keys(obj)) {
      const v = deepFind(obj[k], key);
      if (v !== undefined) return v;
    }
  }
  return undefined;
}

// Take the Yahoo "player" node (array-like) and pull out reliable fields
function normalizePlayerNode(playerNode) {
  const player_id =
    deepFind(playerNode, "player_id") ||
    deepFind(playerNode, "player_key") ||
    "";

  const nameObj = deepFind(playerNode, "name");
  const name =
    (nameObj && (nameObj.full || nameObj.name || nameObj.first + " " + nameObj.last)) || "";

  const editorial_team_abbr = deepFind(playerNode, "editorial_team_abbr") || "";

  // eligible_positions can be an array of {position:"PG"} or ["PG","SG"]
  const elig = deepFind(playerNode, "eligible_positions");
  const positions = Array.isArray(elig)
    ? elig
        .map((e) => (typeof e === "string" ? e : e?.position))
        .filter(Boolean)
    : [];

  const ownership = deepFind(playerNode, "ownership") || {};
  const is_owned =
    Number(ownership?.is_owned) === 1 || ownership?.is_owned === 1 || ownership?.ownership_type === "team";
  const ownership_type = ownership?.ownership_type || (is_owned ? "team" : "freeagents");

  const player_stats = deepFind(playerNode, "player_stats") || null;

  return {
    player_id: String(player_id || ""),
    name: String(name || ""),
    team: String(editorial_team_abbr || ""),
    positions,
    ownership: { is_owned: !!is_owned, ownership_type },
    stats: player_stats, // raw for now (current season might be "-" before tip-off)
  };
}

// Helper: convert our normalized players into Yahoo player_keys if present, else fall back to player_id
function toPlayerKey(p) {
  // Prefer an explicit player_key if we have one
  const pk =
    p?.raw?.player_key ||
    p?.player_key ||
    null;

  if (pk) return pk;

  // Otherwise build from {game_key}.p.{player_id}
  const id = p?.player_id && String(p.player_id).trim();
  const gk =
    (global.GAME_KEY && String(global.GAME_KEY).trim()) ||
    (global.LEAGUE_KEY && String(global.LEAGUE_KEY).split(".")[0]) || // e.g., "466"
    null;

  if (!id || !gk) return null;

  return `${gk}.p.${id}`;
}


// Batch fetch stats for a list of player keys for a given season
async function fetchSeasonStatsForPlayerKeys(playerKeys, season) {
  if (!playerKeys.length) return [];
  const chunkSize = 24; // safe batch size
  const out = [];

  for (let i = 0; i < playerKeys.length; i += chunkSize) {
    const chunk = playerKeys.slice(i, i + chunkSize);
    const keysParam = chunk.map(encodeURIComponent).join(",");
    // players;player_keys=<k1>,<k2>,.../stats;type=season;season=YYYY
    const path = `players;player_keys=${keysParam}/stats;type=season;season=${season}`;
    const data = await yGet(path);

    const pc = data?.fantasy_content?.players;
    const count = Number(pc?.count ?? 0);
    for (let j = 0; j < count; j++) {
      const node = pc?.[String(j)]?.player;
      if (!node) continue;
      const pid = String(deepFind(node, "player_id") || "");
      const statsBlock = deepFind(node, "player_stats") || null;
      out.push({ player_id: pid, season_stats: statsBlock });
    }
  }
  return out;
}

// Map Yahoo stat_id -> our 9-cat keys, using league settings when available,
// and falling back to known NBA ids if settings are sparse.
// Map Yahoo stat_id -> our 9-cat keys, prefer league/game settings, fall back to known-good NBA ids.
async function getLeagueStatMap(leagueKey) {
  // Try league settings (keep your existing league parsing if you already have it)
  let leagueIds = {};
  try {
    const data = await yGet(`league/${encodeURIComponent(leagueKey)}/settings`);
    const cats = data?.fantasy_content?.league?.[1]?.settings?.[0]?.stat_categories?.stats;
    const count = Number(cats?.count ?? cats?.["count"] ?? 0);
    const rows = [];
    for (let i = 0; i < count; i++) {
      const sc = cats?.[String(i)]?.stat;
      if (!sc) continue;
      rows.push({
        id: String(sc.stat_id),
        name: String(sc.name || ""),
        display: String(sc.display_name || sc.name || ""),
      });
    }
    const byDisplay = new Map(rows.map(s => [s.display.toLowerCase(), s]));
    const byName = new Map(rows.map(s => [s.name.toLowerCase(), s]));
    const pick = (...labels) => {
      for (const L of labels) {
        const k = L.toLowerCase();
        if (byDisplay.has(k)) return byDisplay.get(k).id;
        if (byName.has(k)) return byName.get(k).id;
      }
      return null;
    };
    leagueIds = {
      gp:  pick("GP","Games Played"),
      fg_pct: pick("FG%","Field Goal %"),
      ft_pct: pick("FT%","Free Throw %"),
      tpm: pick("3PTM","3PM","3-Pointers Made"),
      pts: pick("PTS","Points"),
      reb: pick("REB","Rebounds","Total Rebounds"),
      ast: pick("AST","Assists"),
      stl: pick("ST","STL","Steals"),
      blk: pick("BLK","Blocks"),
      tov: pick("TO","TOV","Turnovers"),
    };
  } catch {}

  // Corrected fallback (matches your sample):
  const FALLBACK = {
    gp:  "0",
    fg_pct: "5",
    ft_pct: "8",
    tpm: "10", // 3PM total
    pts: "12",
    reb: "14", // ✅ total rebounds
    ast: "15", // ✅ assists
    stl: "16",
    blk: "17",
    tov: "18",
  };

  const ids = {
    gp:  leagueIds.gp  || FALLBACK.gp,
    fg_pct: leagueIds.fg_pct || FALLBACK.fg_pct,
    ft_pct: leagueIds.ft_pct || FALLBACK.ft_pct,
    tpm: leagueIds.tpm || FALLBACK.tpm,
    pts: leagueIds.pts || FALLBACK.pts,
    reb: leagueIds.reb || FALLBACK.reb,
    ast: leagueIds.ast || FALLBACK.ast,
    stl: leagueIds.stl || FALLBACK.stl,
    blk: leagueIds.blk || FALLBACK.blk,
    tov: leagueIds.tov || FALLBACK.tov,
  };

  return { ids, meta: [] };
}


// ---- Token helper: refresh only when we actually can/need to ----
async function ensureToken() {
  // No access token yet → nothing to refresh (user must visit / then “Connect Yahoo”)
  if (!TOKENS.access_token) return;
  // Still valid
  if (Date.now() < TOKENS.expires_at) return;
  // No refresh token → cannot refresh
  if (!TOKENS.refresh_token) return;

  const basic = Buffer.from(`${Y_CLIENT_ID}:${Y_CLIENT_SECRET}`).toString("base64");
  const r = await fetch("https://api.login.yahoo.com/oauth2/get_token", {
    method: "POST",
    headers: {
      Authorization: `Basic ${basic}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: TOKENS.refresh_token,
      redirect_uri: REDIRECT_URI,
    }),
  });

  const data = await r.json();
  if (!r.ok) {
    console.error("REFRESH_ERROR:", data);
    throw new Error("Failed to refresh Yahoo token");
  }

  TOKENS.access_token = data.access_token;
  TOKENS.expires_at = Date.now() + data.expires_in * 1000 - 60_000;
}

// --- Convert Yahoo season stats block into our 9-cat per-game stats ---
function to9CatPerGame(season_stats, statIds) {
  if (!season_stats) return null;
  const list = season_stats?.stats || season_stats?.["stats"];
  if (!Array.isArray(list)) return null;

  const map = new Map();
  for (const row of list) {
    const s = row?.stat;
    if (!s) continue;
    map.set(String(s.stat_id), String(s.value));
  }

  const num = (id, def = 0) => {
    const v = map.get(String(id));
    if (v == null || v === "-" || v === "-/-") return def;
    const n = Number(v);
    return Number.isFinite(n) ? n : def;
  };

  const gp      = num(statIds.gp, 0);
  const fg_pct  = num(statIds.fg_pct, 0);
  const ft_pct  = num(statIds.ft_pct, 0);
  const tpm_tot = num(statIds.tpm, 0);
  const pts_tot = num(statIds.pts, 0);
  const reb_tot = num(statIds.reb, 0);
  const ast_tot = num(statIds.ast, 0);
  const stl_tot = num(statIds.stl, 0);
  const blk_tot = num(statIds.blk, 0);
  const tov_tot = num(statIds.tov, 0);

  const pg = (tot) => (gp > 0 ? tot / gp : 0);

  return {
    gp,
    fg_pct,
    ft_pct,
    tpm_pg: pg(tpm_tot),
    pts_pg: pg(pts_tot),
    reb_pg: pg(reb_tot),
    ast_pg: pg(ast_tot),
    stl_pg: pg(stl_tot),
    blk_pg: pg(blk_tot),
    tov_pg: pg(tov_tot),
  };
}


// --- Compute Z-scores and total score for a list of players with per-game cats ---
function computeZScores(rows, opts = {}) {
  // rows: [{ player, cats: {...} }]
  const weights = Object.assign({
    fg_pct: 1, ft_pct: 1, tpm_pg: 1, pts_pg: 1, reb_pg: 1, ast_pg: 1, stl_pg: 1, blk_pg: 1, tov_pg: 1,
  }, opts.weights || {});

  // Apply punts by zeroing the weight
  if (opts.punt && Array.isArray(opts.punt)) {
    for (const k of opts.punt) {
      if (k in weights) weights[k] = 0;
    }
  }

  // Build arrays for mean/sd
  const keys = Object.keys(weights).filter(k => (weights[k] || 0) !== 0);
  const stats = {};
  for (const k of keys) {
    const vals = rows.map(r => {
      const v = r.cats?.[k];
      return Number.isFinite(v) ? v : 0;
    });
    const mean = vals.reduce((a,b)=>a+b,0) / Math.max(1, vals.length);
    const sd = Math.sqrt(vals.reduce((a,b)=>a+(b-mean)**2,0) / Math.max(1, vals.length-1)) || 1;
    stats[k] = { mean, sd };
  }

  // score each player
  for (const r of rows) {
    let score = 0;
    for (const k of keys) {
      const { mean, sd } = stats[k];
      const val = Number.isFinite(r.cats?.[k]) ? r.cats[k] : 0;
      let z = (val - mean) / sd;
      if (k === "tov_pg" || k === "tov") z = -z; // turnovers negative
      score += (weights[k] || 0) * z;
    }
    r.score = score;
  }

  // sort desc by score
  return rows.sort((a,b)=> b.score - a.score);
}


// --- Roster settings → demand per base position (PG, SG, SF, PF, C) ---
async function getLeagueRosterModel(leagueKey) {
  const data = await yGet(`league/${encodeURIComponent(leagueKey)}/settings`);
  const positions = data?.fantasy_content?.league?.[1]?.settings?.[0]?.roster_positions;
  const count = Number(positions?.count ?? positions?.["count"] ?? 0);
  const rows = [];
  for (let i = 0; i < count; i++) {
    const pos = positions?.[String(i)]?.roster_position;
    if (!pos) continue;
    rows.push({ position: String(pos?.position || ""), count: Number(pos?.count || 0) });
  }

  // Map combined slots to our five base positions
  const base = { PG:0, SG:0, SF:0, PF:0, C:0 };
  const add = (k, v) => { if (base[k] != null) base[k] += v; };

  for (const r of rows) {
    const p = r.position.toUpperCase();
    const n = r.count || 0;
    if (!n) continue;

    if (["PG","SG","SF","PF","C"].includes(p)) add(p, n);
    else if (p === "G")  { add("PG", n/2); add("SG", n/2); }
    else if (p === "F")  { add("SF", n/2); add("PF", n/2); }
    else if (p === "UTIL" || p === "UTIL+") {
      // distribute UTIL evenly across all five base positions
      const share = n/5;
      add("PG", share); add("SG", share); add("SF", share); add("PF", share); add("C", share);
    } // ignore IL/IL+ for scarcity
  }

  return base; // fractional is fine
}

// --- Supply from available players → how many can play each base position ---
function computeSupplyFromPlayers(players) {
  const supply = { PG:0, SG:0, SF:0, PF:0, C:0 };
  const toBase = (posArr=[]) => posArr
    .map(p => String(p).toUpperCase())
    .filter(p => ["PG","SG","SF","PF","C"].includes(p));
  for (const p of players) {
    const bases = toBase(p.positions);
    const uniq = Array.from(new Set(bases));
    for (const b of uniq) supply[b] += 1;
  }
  return supply;
}

// --- Convert (demand, supply) into a per-position scarcity factor in [0.9 .. 1.3] ---
function buildScarcityFactors(demand, supply, alpha = 0.25) {
  // alpha controls intensity (0.15–0.30 recommended)
  const basePos = ["PG","SG","SF","PF","C"];
  const factors = {};
  // Avoid divide-by-zero; smooth with +1
  const ratios = basePos.map(k => (demand[k] + 0.0001) / (supply[k] + 1));
  const mean = ratios.reduce((a,b)=>a+b,0) / ratios.length || 1;

  for (const k of basePos) {
    const r = (demand[k] + 0.0001) / (supply[k] + 1);
    const rel = (r - mean) / (mean || 1); // relative scarcity vs mean
    // Map relative scarcity → multiplier around 1.0
    // cap to keep sane bounds
    const mult = Math.max(0.9, Math.min(1.3, 1 + alpha * rel));
    factors[k] = mult;
  }
  return factors;
}

// --- Given a player's eligible positions, compute a single scarcity bonus ---
function scarcityBonusForPlayer(positions, factors, bonusScale = 0.35) {
  const bases = (positions||[]).map(p => String(p).toUpperCase())
    .filter(p => ["PG","SG","SF","PF","C"].includes(p));
  if (!bases.length) return 0;
  // take the best (most scarce) multiplier they can fill
  const bestMult = Math.max(...bases.map(b => factors[b] ?? 1));
  // Translate multiplier to an additive bonus (centered around 0)
  // e.g., mult 1.10 → +0.10 * bonusScale
  return (bestMult - 1) * bonusScale;
}

// Pull stat_id -> names from the current NBA game (more reliable than league)
async function getGameStatMap(gameKey) {
  const data = await yGet(`game/${encodeURIComponent(gameKey)}/stat_categories`);
  const statsRoot = data?.fantasy_content?.game?.[1]?.stat_categories?.stats;
  const count = Number(statsRoot?.count ?? statsRoot?.["count"] ?? 0);
  const out = [];
  for (let i = 0; i < count; i++) {
    const sc = statsRoot?.[String(i)]?.stat;
    if (!sc) continue;
    out.push({
      id: String(sc.stat_id),
      name: String(sc.name || ""),
      display: String(sc.display_name || sc.name || ""),
    });
  }
  const byId = new Map(out.map(s => [s.id, s]));
  const byDisplay = new Map(out.map(s => [s.display.toLowerCase(), s]));
  const byName = new Map(out.map(s => [s.name.toLowerCase(), s]));
  const pick = (...labels) => {
    for (const L of labels) {
      const k = L.toLowerCase();
      if (byDisplay.has(k)) return byDisplay.get(k).id;
      if (byName.has(k)) return byName.get(k).id;
    }
    return null;
  };

  return {
    list: out,
    ids: {
      gp:  pick("GP","Games Played") || "0",
      fg_pct: pick("FG%","Field Goal %"),
      ft_pct: pick("FT%","Free Throw %"),
      tpm: pick("3PTM","3PM","3-Pointers Made"),
      pts: pick("PTS","Points"),
      reb: pick("REB","Rebounds","Total Rebounds"),
      ast: pick("AST","Assists"),
      stl: pick("ST","STL","Steals"),
      blk: pick("BLK","Blocks"),
      tov: pick("TO","TOV","Turnovers"),
    },
  };
}



// ---- Routes ----
app.get("/", (_req, res) => {
  res.send(`<a href="${authURL.toString()}">Connect Yahoo</a>`);
});

// app.get("/callback", async (req, res) => {
//   try {
//     const code = req.query.code;
//     if (!code) return res.status(400).send("Missing OAuth code");

//     const basic = Buffer.from(`${Y_CLIENT_ID}:${Y_CLIENT_SECRET}`).toString("base64");
//     const r = await fetch("https://api.login.yahoo.com/oauth2/get_token", {
//       method: "POST",
//       headers: {
//         Authorization: `Basic ${basic}`,
//         "Content-Type": "application/x-www-form-urlencoded",
//       },
//       body: new URLSearchParams({
//         grant_type: "authorization_code",
//         redirect_uri: REDIRECT_URI,
//         code,
//       }),
//     });

//     const data = await r.json();
//     if (!r.ok) {
//       return res.status(400).json({ error: "OAuth exchange failed", yahoo: data });
//     }

//     TOKENS = {
//       access_token: data.access_token,
//       refresh_token: data.refresh_token,
//       expires_at: Date.now() + data.expires_in * 1000 - 60_000, // refresh 60s early
//     };

//     res.send("Yahoo connected. Go to /setup to find leagueKey.");
//   } catch (err) {
//     console.error("CALLBACK_ERROR:", err);
//     res.status(500).json({ error: "Callback error", detail: err?.message || String(err) });
//   }
// });

app.get("/callback", async (req, res) => {
  try {
    const code = req.query.code;
    if (!code) return res.redirect(`${FRONTEND_BASE}/oauth/error?reason=missing_code`);

    const basic = Buffer.from(`${Y_CLIENT_ID}:${Y_CLIENT_SECRET}`).toString("base64");
    const r = await fetch("https://api.login.yahoo.com/oauth2/get_token", {
      method: "POST",
      headers: {
        Authorization: `Basic ${basic}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        redirect_uri: REDIRECT_URI,
        code,
      }),
    });

    const data = await r.json();
    if (!r.ok || !data?.access_token) {
      // send the yahoo error payload to the UI for display
      return res.redirect(`${FRONTEND_BASE}/oauth/error?reason=exchange_failed`);
    }

    TOKENS = {
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      expires_at: Date.now() + data.expires_in * 1000 - 60_000,
    };

    // ✅ instead of showing a backend “connected” page, hop back to the UI
    return res.redirect(`${FRONTEND_BASE}/oauth/success`);
  } catch (err) {
    return res.redirect(`${FRONTEND_BASE}/oauth/error?reason=exception`);
  }
});


// ---- Debug: see token state quickly ----
app.get("/debug/tokens", (_req, res) => {
  res.json({
    has_access_token: !!TOKENS.access_token,
    has_refresh_token: !!TOKENS.refresh_token,
    expires_at: TOKENS.expires_at,
    expires_in_ms: TOKENS.expires_at ? TOKENS.expires_at - Date.now() : null,
  });
});

// ---- Setup: discover league_key from numeric TARGET_LEAGUE_ID ----
app.get("/setup", async (_req, res) => {
  try {
    await ensureToken();
    if (!TOKENS.access_token) {
      return res.status(401).json({ error: "No access token. Visit / and Connect Yahoo first." });
    }

    // 1) Get the current NBA game_key (e.g., "466")
    const gameResp = await yGet("game/nba");
    // Try multiple shapes to be safe
    const game_key =
      gameResp?.fantasy_content?.game?.[0]?.game_key ||
      gameResp?.fantasy_content?.game?.["0"]?.game_key ||
      gameResp?.fantasy_content?.game?.game_key;
    if (!game_key) {
      return res.status(404).json({ error: "Could not determine NBA game_key", gameResp });
    }

    // 2) Get your leagues for that game_key
    const leaguesResp = await yGet(`users;use_login=1/games;game_keys=${game_key}/leagues`);
    const fc = leaguesResp?.fantasy_content;

    // Yahoo uses "numeric-object" arrays: users["0"].user, games["0"].game, leagues["0"].league
    const usersRoot = fc?.users;
    const userNode = usersRoot?.["0"]?.user || usersRoot?.[0]?.user || usersRoot?.user;
    const gamesNode = userNode?.[1]?.games;

    const gameList =
      gamesNode?.["0"]?.game || gamesNode?.[0]?.game || gamesNode?.game || [];

    const gamesArr = Array.isArray(gameList) ? gameList : (gameList ? [gameList] : []);

    // In this structure, gamesArr[0] is game meta, gamesArr[1] is leagues
    // but we’ll just search for the one that has 'leagues'
    const leaguesContainer =
      (gamesArr.find((g) => g && g.leagues)?.leagues) ||
      gamesArr?.[1]?.leagues ||
      null;

    const leagueList =
      leaguesContainer?.["0"]?.league ||
      leaguesContainer?.[0]?.league ||
      leaguesContainer?.league ||
      [];

    const leaguesArr = Array.isArray(leagueList) ? leagueList : (leagueList ? [leagueList] : []);

    const leagues = leaguesArr.map((l) => {
      // Sometimes fields are directly on the object; sometimes under [0]
      const lk = l.league_key || l?.[0]?.league_key;
      const lid = l.league_id || l?.[0]?.league_id;
      const name = l.name || l?.[0]?.name;
      return { league_key: lk, league_id: String(lid || ""), name: String(name || "") };
    }).filter(x => x.league_key && x.league_id);

    if (!leagues.length) {
      return res.status(404).json({
        error: "No leagues found for this account in the current NBA game",
        game_key,
        raw: leaguesResp,
      });
    }

    // 3) Match the numeric league id (59555)
    const league = leagues.find((l) => l.league_id === String(TARGET_LEAGUE_ID));
    if (!league) {
      return res.status(404).json({
        error: `League ${TARGET_LEAGUE_ID} not found for this Yahoo account`,
        game_key,
        leagues_found: leagues,
      });
    }

    // 4) Save and return
    global.LEAGUE_KEY = league.league_key; // e.g., "466.l.59555"
    global.GAME_KEY = game_key;
    return res.json({ league_key: league.league_key, name: league.name, game_key });
  } catch (err) {
    const detail = {
      message: err?.message || String(err),
      name: err?.name,
      stack: err?.stack,
      response: err?.response?.data || err?.data || null,
    };
    console.error("SETUP_ERROR:", detail);
    return res.status(500).json({ error: "Internal error in /setup", detail });
  }
});


// ---- Draft: list available players (free agents) ----
app.get("/draft/available", async (req, res) => {
  try {
    await ensureToken();
    if (!global.LEAGUE_KEY) {
      return res.status(400).json({ error: "Run /setup first to populate league_key" });
    }

    const status = (req.query.status || "FA,W").toString(); // free agents + waivers by default
    const limit = Math.max(1, Math.min(300, Number(req.query.limit) || 150));

    const statuses = status.split(",").map((s) => s.trim()).filter(Boolean);

    const pages = await Promise.all(
      statuses.map((s) => fetchLeaguePlayersByStatus(global.LEAGUE_KEY, s))
    );

    // Normalize, de-dup by player_id, and filter out unnamed/blank entries
    const combinedRaw = [].concat(...pages);
    const normalized = combinedRaw.map(normalizePlayerNode)
      .filter(p => p.player_id && p.name); // keep only valid rows

    // de-dup
    const byId = new Map();
    for (const p of normalized) {
      if (!byId.has(p.player_id)) byId.set(p.player_id, p);
    }
    const unique = Array.from(byId.values());

    // take first N
    const sliced = unique.slice(0, limit);

    return res.json({
      league_key: global.LEAGUE_KEY,
      status: statuses,
      count: unique.length,
      shown: sliced.length,
      players: sliced
    });
  } catch (err) {
    const detail = {
      message: err?.message || String(err),
      name: err?.name,
      stack: err?.stack,
      response: err?.response?.data || err?.data || null,
    };
    console.error("AVAILABLE_ERROR:", detail);
    return res.status(500).json({ error: "Internal error in /draft/available", detail });
  }
});


app.get("/draft/stats", async (req, res) => {
  try {
    await ensureToken();
    if (!global.LEAGUE_KEY) {
      return res.status(400).json({ error: "Run /setup first to populate league_key" });
    }
    const season = (req.query.season || "2024").toString(); // last season until games start
    const limit = Math.max(1, Math.min(300, Number(req.query.limit) || 150));
    const status = (req.query.status || "FA,W").toString();

    // 1) get available players (trimmed list)
    const baseUrl = new URL(`${req.protocol}://${req.get("host")}${req.baseUrl || ""}/draft/available`);
    baseUrl.searchParams.set("limit", String(limit));
    baseUrl.searchParams.set("status", status);

    // call our own route in-process would be ideal, but to avoid HTTP recursion, reproduce the core:
    const statuses = status.split(",").map((s) => s.trim()).filter(Boolean);
    const pages = await Promise.all(
      statuses.map((s) => fetchLeaguePlayersByStatus(global.LEAGUE_KEY, s))
    );
    const combinedRaw = [].concat(...pages);
    const normalized = combinedRaw.map(normalizePlayerNode)
      .filter(p => p.player_id && p.name);

    // de-dup and slice
    const byId = new Map();
    for (const p of normalized) if (!byId.has(p.player_id)) byId.set(p.player_id, p);
    const players = Array.from(byId.values()).slice(0, limit);

    // 2) build player_keys and fetch season stats in batches
    const keys = players.map(toPlayerKey).filter(Boolean);
    const stats = await fetchSeasonStatsForPlayerKeys(keys, season);

    // 3) join back by player_id
    const statsById = new Map(stats.map(s => [s.player_id, s.season_stats]));
    const enriched = players.map(p => ({
      ...p,
      season,
      season_stats: statsById.get(p.player_id) || null
    }));

    return res.json({
      league_key: global.LEAGUE_KEY,
      season,
      count: enriched.length,
      players: enriched
    });
  } catch (err) {
    const detail = {
      message: err?.message || String(err),
      name: err?.name,
      stack: err?.stack,
      response: err?.response?.data || err?.data || null,
    };
    console.error("DRAFT_STATS_ERROR:", detail);
    return res.status(500).json({ error: "Internal error in /draft/stats", detail });
  }
});

// Compute draft recommendations using last season (or chosen season) stats
app.get("/draft/recommend", async (req, res) => {
  try {
    await ensureToken();
    if (!global.LEAGUE_KEY) {
      return res.status(400).json({ error: "Run /setup first to populate league_key" });
    }

    const season = (req.query.season || "2024").toString();
    const limit = Math.max(1, Math.min(300, Number(req.query.limit) || 150));
    const punt = (req.query.punt || "").toString()
      .split(",")
      .map(s => s.trim().toLowerCase())
      .filter(Boolean);

    // 1) stat id mapping for this league
    const { ids } = await getLeagueStatMap(global.LEAGUE_KEY);

    // 2) get available players (FA+W), lighten to first N
    const statuses = ["FA","W"];
    const pages = await Promise.all(statuses.map(s => fetchLeaguePlayersByStatus(global.LEAGUE_KEY, s)));
    const combinedRaw = [].concat(...pages).map(normalizePlayerNode).filter(p => p.player_id && p.name);

    const byId = new Map();
    for (const p of combinedRaw) if (!byId.has(p.player_id)) byId.set(p.player_id, p);
    const avail = Array.from(byId.values()).slice(0, limit);

    // 3) fetch last-season stats for those players
    const keys = avail.map(toPlayerKey).filter(Boolean);
    const seasonStats = await fetchSeasonStatsForPlayerKeys(keys, season);
    const statsById = new Map(seasonStats.map(s => [s.player_id, s.season_stats]));

    // 3.5) SCARCITY: demand from roster settings + supply from available players
    const demand = await getLeagueRosterModel(global.LEAGUE_KEY);
    const supply = computeSupplyFromPlayers(avail);
    const scarcity = buildScarcityFactors(demand, supply, /* alpha */ 0.25);

    // 4) build per-game 9-cat rows
    const rows = [];
    for (const p of avail) {
      const line = to9CatPerGame(statsById.get(p.player_id), ids);
      if (!line) continue;
      const pos_bonus = scarcityBonusForPlayer(p.positions, scarcity, /* bonusScale */ 0.35);
      rows.push({
        player: { id: p.player_id, key: p.player_key || toPlayerKey(p), name: p.name, team: p.team, pos: p.positions },
        cats: line,
        pos_bonus,
      });
    }
    if (!rows.length) {
      return res.status(200).json({ league_key: global.LEAGUE_KEY, season, punt, top: [] });
    }

    // 5) z-scores (+ punts)
    const ranked = computeZScores(rows, { punt });

    // apply position scarcity bonus
    for (const r of ranked) r.score = (r.score ?? 0) + (r.pos_bonus ?? 0);

    // 6) respond with Top 25 (or requested limit)
    const topN = Math.min(25, ranked.length);
    return res.json({
      league_key: global.LEAGUE_KEY,
      season,
      punt,
      count: ranked.length,
      top: ranked.slice(0, Math.min(25, ranked.length)).map(r => ({
        player: r.player,
        score: r.score,
        pos_bonus: r.pos_bonus ?? 0,
        cats: r.cats,
      })),
    });

  } catch (err) {
    const detail = {
      message: err?.message || String(err),
      name: err?.name,
      stack: err?.stack,
      response: err?.response?.data || err?.data || null,
    };
    console.error("RECOMMEND_ERROR:", detail);
    return res.status(500).json({ error: "Internal error in /draft/recommend", detail });
  }
});

app.get("/auth/start", (_req, res) => {
  // optional: include a simple state value
  const url = new URL("https://api.login.yahoo.com/oauth2/request_auth");
  url.searchParams.set("client_id", Y_CLIENT_ID || "");
  url.searchParams.set("redirect_uri", REDIRECT_URI || "");
  url.searchParams.set("response_type", "code");
  url.searchParams.set("language", "en-us");
  // e.g., pass a state you can verify later if you want
  url.searchParams.set("state", "ok");
  res.redirect(url.toString());
});

app.get("/debug/statmap", async (_req, res) => {
  try {
    const league = global.LEAGUE_KEY;
    if (!league) return res.status(400).json({ error: "run /setup first" });
    const { ids, meta } = await getLeagueStatMap(league);
    res.json({ league, game_key: global.GAME_KEY, ids, sample: meta.slice(0, 20) });
  } catch (e) {
    res.status(500).json({ error: String(e?.message || e) });
  }
});


app.listen(PORT, () => console.log(`Running on http://localhost:${PORT}`));
