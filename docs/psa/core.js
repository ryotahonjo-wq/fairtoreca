// PSA centering core (pure JS, works on RGBA arrays)
const CW = 630, CH = 880;
function boxBlur(src, w, h, r) {
  const out = new Float32Array(w * h * 3), tmp = new Float32Array(w * h * 3);
  for (let y = 0; y < h; y++) for (let c = 0; c < 3; c++) {
    let s = 0; const row = y * w;
    for (let x = -r; x <= r; x++) s += src[(row + Math.min(w - 1, Math.max(0, x))) * 4 + c];
    for (let x = 0; x < w; x++) {
      tmp[(row + x) * 3 + c] = s / (2 * r + 1);
      s += src[(row + Math.min(w - 1, x + r + 1)) * 4 + c] - src[(row + Math.max(0, x - r)) * 4 + c];
    }
  }
  for (let x = 0; x < w; x++) for (let c = 0; c < 3; c++) {
    let s = 0;
    for (let y = -r; y <= r; y++) s += tmp[(Math.min(h - 1, Math.max(0, y)) * w + x) * 3 + c];
    for (let y = 0; y < h; y++) {
      out[(y * w + x) * 3 + c] = s / (2 * r + 1);
      s += tmp[(Math.min(h - 1, y + r + 1) * w + x) * 3 + c] - tmp[(Math.max(0, y - r) * w + x) * 3 + c];
    }
  }
  return out;
}
function median(a) { const s = Array.from(a).sort((p, q) => p - q); return s[s.length >> 1]; }
function longestRun(v) {
  let best = [0, 0], start = -1;
  for (let i = 0; i <= v.length; i++) {
    const x = i < v.length && v[i];
    if (x && start < 0) start = i;
    else if (!x && start >= 0) { if (i - start > best[1] - best[0]) best = [start, i]; start = -1; }
  }
  return best;
}
function fitLine(pts, xOfY) { // least squares: if xOfY, x = a*y+b else y = a*x+b
  let n = pts.length, su = 0, sv = 0, suu = 0, suv = 0;
  for (const [x, y] of pts) { const u = xOfY ? y : x, v = xOfY ? x : y; su += u; sv += v; suu += u * u; suv += u * v; }
  const a = (n * suv - su * sv) / (n * suu - su * su || 1), b = (sv - a * su) / n;
  return { a, b, xOfY };
}
function intersect(L, T) { // L: x=a1*y+b1, T: y=a2*x+b2
  const x = (L.a * T.b + L.b) / (1 - L.a * T.a); return [x, T.a * x + T.b];
}
function findCard(rgba, w, h) {
  const r = Math.max(3, Math.round(Math.min(w, h) / 120));
  const bl = boxBlur(rgba, w, h, r);
  const k = Math.max(10, Math.floor(Math.min(w, h) / 20));
  const bg = [0, 1, 2].map(c => {
    const vals = [];
    for (const [x0, y0] of [[0, 0], [w - k, 0], [0, h - k], [w - k, h - k]])
      for (let y = y0; y < y0 + k; y += 2) for (let x = x0; x < x0 + k; x += 2) vals.push(bl[(y * w + x) * 3 + c]);
    return median(vals);
  });
  const m = new Uint8Array(w * h);
  for (let i = 0; i < w * h; i++) {
    const d = Math.hypot(bl[i * 3] - bg[0], bl[i * 3 + 1] - bg[1], bl[i * 3 + 2] - bg[2]);
    m[i] = d > 50 ? 1 : 0;
  }
  let r0 = h / 3 | 0, r1 = 2 * h / 3 | 0, c0 = w / 3 | 0, c1 = 2 * w / 3 | 0;
  for (let it = 0; it < 2; it++) {
    const cf = new Array(w).fill(0); for (let y = r0; y < r1; y++) for (let x = 0; x < w; x++) cf[x] += m[y * w + x];
    [c0, c1] = longestRun(cf.map(v => v / (r1 - r0) > 0.6));
    const rf = new Array(h).fill(0); for (let y = 0; y < h; y++) for (let x = c0; x < c1; x++) rf[y] += m[y * w + x];
    [r0, r1] = longestRun(rf.map(v => v / Math.max(1, c1 - c0) > 0.6));
    const pr = (r1 - r0) / 6 | 0, pc = (c1 - c0) / 6 | 0; r0 += pr; r1 -= pr; c0 += pc; c1 -= pc;
  }
  if (c1 - c0 < w * 0.15 || r1 - r0 < h * 0.15) return null;
  const run = Math.max(8, Math.round(Math.min(w, h) / 50));
  const firstSolid = get => { // get(i) -> 0/1 along a line from outside
    let s = 0;
    for (let i = 0; i < run; i++) s += get(i);
    for (let i = 0; ; i++) { if (s >= run * 0.95) return i; const nx = get(i + run); if (nx < 0) return null; s += nx - get(i); }
  };
  const step = Math.max(2, Math.round(h / 300));
  const sides = {};
  const collect = (name, pts, xOfY) => {
    if (pts.length < 10) return false;
    const med = median(pts.map(p => xOfY ? p[0] : p[1]));
    const good = pts.filter(p => Math.abs((xOfY ? p[0] : p[1]) - med) < Math.max(6, w / 80));
    sides[name] = fitLine(good, xOfY); return true;
  };
  const L = [], R = [], T = [], B = [];
  for (let y = r0; y < r1; y += step) {
    const a = firstSolid(i => i < w ? m[y * w + i] : -1); if (a != null) L.push([a, y]);
    const b = firstSolid(i => i < w ? m[y * w + (w - 1 - i)] : -1); if (b != null) R.push([w - 1 - b, y]);
  }
  for (let x = c0; x < c1; x += step) {
    const a = firstSolid(i => i < h ? m[i * w + x] : -1); if (a != null) T.push([x, a]);
    const b = firstSolid(i => i < h ? m[(h - 1 - i) * w + x] : -1); if (b != null) B.push([x, h - 1 - b]);
  }
  if (!collect("L", L, true) || !collect("R", R, true) || !collect("T", T, false) || !collect("B", B, false)) return null;
  const q = [intersect(sides.L, sides.T), intersect(sides.R, sides.T), intersect(sides.R, sides.B), intersect(sides.L, sides.B)];
  const d = (p, q2) => Math.hypot(p[0] - q2[0], p[1] - q2[1]);
  const s = [d(q[0], q[1]), d(q[1], q[2]), d(q[2], q[3]), d(q[3], q[0])];
  const cw = (s[0] + s[2]) / 2, ch = (s[1] + s[3]) / 2;
  let ratio = Math.min(cw, ch) / Math.max(cw, ch);
  const score = Math.abs(ratio - 63 / 88) + Math.abs(s[0] - s[2]) / cw + Math.abs(s[1] - s[3]) / ch;
  if (score > 0.08) return null;
  if (cw > ch) q.push(q.shift()); // landscape -> rotate order
  return q;
}
function solve(A, b) { // gaussian elimination
  const n = b.length; A = A.map((r, i) => [...r, b[i]]);
  for (let i = 0; i < n; i++) {
    let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(A[j][i]) > Math.abs(A[p][i])) p = j;
    [A[i], A[p]] = [A[p], A[i]];
    for (let j = i + 1; j < n; j++) { const f = A[j][i] / A[i][i]; for (let k = i; k <= n; k++) A[j][k] -= f * A[i][k]; }
  }
  const x = new Array(n);
  for (let i = n - 1; i >= 0; i--) { let s = A[i][n]; for (let k = i + 1; k < n; k++) s -= A[i][k] * x[k]; x[i] = s / A[i][i]; }
  return x;
}
function warp(rgba, w, h, quad) { // map card rect (CW x CH) -> source quad
  const dst = [[0, 0], [CW, 0], [CW, CH], [0, CH]], A = [], b = [];
  for (let i = 0; i < 4; i++) {
    const [u, v] = dst[i], [x, y] = quad[i];
    A.push([u, v, 1, 0, 0, 0, -u * x, -v * x]); b.push(x);
    A.push([0, 0, 0, u, v, 1, -u * y, -v * y]); b.push(y);
  }
  const H = solve(A, b), out = new Uint8ClampedArray(CW * CH * 4);
  for (let v = 0; v < CH; v++) for (let u = 0; u < CW; u++) {
    const z = H[6] * u + H[7] * v + 1, x = (H[0] * u + H[1] * v + H[2]) / z, y = (H[3] * u + H[4] * v + H[5]) / z;
    const x0 = Math.max(0, Math.min(w - 2, Math.floor(x))), y0 = Math.max(0, Math.min(h - 2, Math.floor(y))), fx = x - x0, fy = y - y0;
    const o = (v * CW + u) * 4;
    for (let c = 0; c < 3; c++) {
      const p = (yy, xx) => rgba[(yy * w + xx) * 4 + c];
      out[o + c] = (p(y0, x0) * (1 - fx) + p(y0, x0 + 1) * fx) * (1 - fy) + (p(y0 + 1, x0) * (1 - fx) + p(y0 + 1, x0 + 1) * fx) * fy;
    }
    out[o + 3] = 255;
  }
  return out;
}
function toLab(r, g, b) {
  const f = c => { c /= 255; return c > 0.04045 ? Math.pow((c + 0.055) / 1.055, 2.4) : c / 12.92; };
  const R = f(r), G = f(g), B = f(b);
  let X = (R * 0.4124 + G * 0.3576 + B * 0.1805) / 0.95047, Y = R * 0.2126 + G * 0.7152 + B * 0.0722, Z = (R * 0.0193 + G * 0.1192 + B * 0.9505) / 1.08883;
  const t = v => v > 0.008856 ? Math.cbrt(v) : 7.787 * v + 16 / 116;
  X = t(X); Y = t(Y); Z = t(Z);
  return [116 * Y - 16, 500 * (X - Y), 200 * (Y - Z)];
}
function borders(card) {
  const lab = new Float32Array(CW * CH * 3);
  for (let i = 0; i < CW * CH; i++) { const l = toLab(card[i * 4], card[i * 4 + 1], card[i * 4 + 2]); lab.set(l, i * 3); }
  // OpenCV-style 8-bit Lab scale: L*255/100, a+128, b+128 -> distances comparable to Python version
  const px = (x, y) => { const o = (y * CW + x) * 3; return [lab[o] * 2.55, lab[o + 1], lab[o + 2]]; };
  const res = {};
  for (const side of ["left", "right", "top", "bottom"]) {
    const horiz = side === "left" || side === "right";
    const len = horiz ? CH : CW, depth = horiz ? CW : CH;
    const get = (along, inward) => {
      if (side === "left") return px(inward, along);
      if (side === "right") return px(CW - 1 - inward, along);
      if (side === "top") return px(along, inward);
      return px(along, CH - 1 - inward);
    };
    const a0 = Math.floor(len * 0.3), a1 = Math.floor(len * 0.7);
    const ref = [0, 1, 2].map(c => { const v = []; for (let a = a0; a < a1; a += 2) for (let i = 6; i < 14; i++) v.push(get(a, i)[c]); return median(v); });
    const frac = [];
    for (let i = 0; i < depth / 3; i++) {
      let n = 0, cnt = 0;
      for (let a = a0; a < a1; a += 2) { const p = get(a, i); if (Math.hypot(p[0] - ref[0], p[1] - ref[1], p[2] - ref[2]) > 25) n++; cnt++; }
      frac.push(n / cnt);
    }
    res[side] = null;
    for (let i = 12; i < frac.length - 4; i++) if (Math.min(frac[i], frac[i + 1], frac[i + 2], frac[i + 3]) > 0.6) { res[side] = i; break; }
  }
  return res;
}
function measure(rgba, w, h) {
  const quad = findCard(rgba, w, h);
  if (!quad) return { error: "カードの外枠が見つかりませんでした。黒っぽい背景の上で、真上からカード全体と周りの余白まで入れて撮ってください。" };
  const card = warp(rgba, w, h, quad), b = borders(card);
  if (Object.values(b).some(v => v == null)) return { error: "内側の枠の境目が見つかりませんでした。スリーブやステッカーを外して撮り直してください。", card };
  const lr = 100 * b.left / (b.left + b.right), tb = 100 * b.top / (b.top + b.bottom);
  const worst = Math.max(Math.abs(lr - 50), Math.abs(tb - 50)) + 50;
  return { card, quad, b, lr, tb, worst };
}
if (typeof module !== "undefined") module.exports = { measure, findCard, CW, CH };
