#!/usr/bin/env node
/**
 * managed-login — 관리형 자동 로그인 오케스트레이터 (정책을 코드가 강제)
 *
 * 보안 불변식:
 *  - 이 프로세스는 비밀 원문(아이디/비번)을 절대 보유·출력·로깅하지 않는다.
 *    config에는 `vault://이름` 참조만 있고, 그 문자열을 그대로 openchrome에 넘긴다.
 *    평문 해석·마스킹은 openchrome pilot 볼트가 서버 내부에서 처리한다.
 *  - stdout에는 상태 코드 JSON만. openchrome의 원시 결과는 stdout으로 내보내지 않는다.
 *  - 감사 로그에는 시각·서비스·계정별칭·도메인·상태만 남긴다(비밀 없음).
 *
 * 사용: node managed-login.mjs --service <name> --account <alias> --expected "<identity>" [--config <path>]
 * 반환(stdout, 1줄 JSON): { status, service, account, identityChecked }
 *
 * 상태: success | needs_user_verification | account_identity_mismatch | credentials_missing |
 *       domain_not_allowed | account_in_use | login_failed |
 *       not_enabled | service_unknown | account_unknown | tool_unavailable | platform_policy_block | bad_request
 */

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const OC_HOME = process.env.OPENCHROME_HOME || path.join(os.homedir(), '.openchrome');
const LOCK_DIR = path.join(OC_HOME, 'managed-login.locks');
const AUDIT_LOG = path.join(OC_HOME, 'managed-login-audit.log');

// ---------- 인자 파싱 ----------
function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const val = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : 'true';
      out[key] = val;
    }
  }
  return out;
}
const args = parseArgs(process.argv.slice(2));

// ---------- 결과 출력 / 감사 (항상 lock 해제 후) ----------
let lockPath = null;
function releaseLock() {
  if (lockPath) { try { fs.unlinkSync(lockPath); } catch { /* 이미 없음 */ } lockPath = null; }
}
function audit(status, service, account, domain, attempts) {
  try {
    fs.mkdirSync(OC_HOME, { recursive: true, mode: 0o700 });
    const line = JSON.stringify({
      ts: new Date().toISOString(), service: service ?? null, account: account ?? null,
      domain: domain ?? null, status, attempts: attempts ?? 0,
    }) + '\n';
    fs.appendFileSync(AUDIT_LOG, line, { mode: 0o600 });
  } catch { /* 감사 실패는 흐름을 막지 않음 */ }
}
function finish(status, { service, account, domain, attempts, identityChecked = false } = {}) {
  releaseLock();
  audit(status, service, account, domain, attempts);
  process.stdout.write(JSON.stringify({ status, service: service ?? null, account: account ?? null, identityChecked }) + '\n');
  process.exit(status === 'success' ? 0 : 1);
}

// ---------- openchrome 어댑터 (결과 모양 파싱을 여기 한 곳에) ----------
// TODO(Phase3): 아래 추출 로직은 가짜 서버로 openchrome 실제 JSON 모양을 확정해 정밀화한다.
function ocSpawn(cliArgs) {
  const r = spawnSync('openchrome', cliArgs, { encoding: 'utf8', timeout: 60_000 });
  if (r.error) return { ok: false, unavailable: r.error.code === 'ENOENT', raw: null, text: '' };
  const stdout = r.stdout || '';
  let raw = null;
  try { raw = JSON.parse(stdout); } catch { /* 비-JSON */ }
  return { ok: r.status === 0, raw, text: stdout, code: r.status };
}
function toArgFlags(argMap) {
  const flags = [];
  for (const [k, v] of Object.entries(argMap)) {
    if (typeof v === 'string') flags.push('--arg', `${k}=${v}`);
    else flags.push('--arg', `${k}=json:${JSON.stringify(v)}`);
  }
  return flags;
}
// 실행 중 크롬(pilot 데몬)에 붙어 MCP 툴 원샷 실행
function ocRun(tool, argMap = {}) {
  return ocSpawn(['run', tool, ...toArgFlags(argMap), '--reuse', '--pilot', '--json']);
}
// 결과에서 사람이 볼 텍스트/구조화 필드를 방어적으로 뽑는다 (비밀은 openchrome가 이미 마스킹)
function resultText(res) {
  if (!res || !res.raw) return res?.text || '';
  const r = res.raw;
  if (Array.isArray(r.content)) return r.content.map((c) => (c && c.text) ? c.text : '').join('\n');
  if (typeof r.text === 'string') return r.text;
  return JSON.stringify(r);
}
function structured(res) {
  const r = res?.raw;
  return (r && (r.structuredContent || r.data)) || null;
}
function deepFind(obj, keys, depth = 0) {
  if (!obj || typeof obj !== 'object' || depth > 6) return null;
  for (const k of Object.keys(obj)) {
    if (keys.includes(k) && (typeof obj[k] === 'string' || typeof obj[k] === 'number')) return obj[k];
  }
  for (const k of Object.keys(obj)) {
    const v = deepFind(obj[k], keys, depth + 1);
    if (v != null) return v;
  }
  return null;
}
function hostOf(url) { try { return new URL(String(url)).host.toLowerCase(); } catch { return null; } }
function domainAllowed(host, allow) {
  if (!host) return false;
  return allow.some((d) => {
    d = String(d).toLowerCase();
    return host === d || host.endsWith('.' + d);
  });
}

// 각 툴 호출 래퍼
function tabsCreate(url) {
  const res = ocRun('tabs_create', { url });
  if (!res.ok && res.unavailable) return { unavailable: true };
  const tabId = deepFind(structured(res), ['tabId', 'targetId', 'id']) || deepFind(res.raw, ['tabId', 'targetId', 'id']);
  return { tabId: tabId != null ? String(tabId) : null };
}
function currentUrl(tabId) {
  const res = ocRun('tabs_context', {});
  const s = structured(res) || res.raw;
  // tabs 목록에서 tabId 매칭 → url. 못 찾으면 read_page url 시도.
  let url = null;
  try {
    const tabs = (s && (s.tabs || s.targets || s.pages)) || [];
    const hit = Array.isArray(tabs) ? tabs.find((t) => String(deepFind(t, ['tabId', 'id', 'targetId'])) === String(tabId)) : null;
    url = hit ? deepFind(hit, ['url']) : null;
  } catch { /* fallthrough */ }
  if (!url) { const rp = ocRun('read_page', { tabId, mode: 'ax' }); url = deepFind(structured(rp), ['url']) || deepFind(rp.raw, ['url']); }
  return url ? String(url) : null;
}
function pageText(tabId) {
  const res = ocRun('read_page', { tabId, mode: 'ax' });
  return resultText(res);
}
function gateStatus(tabId) {
  const res = ocRun('oc_gate_inspect', { tabId });
  const s = structured(res) || res.raw || {};
  const gated = deepFind(s, ['gated', 'isGated']) === true;
  const type = deepFind(s, ['gateType', 'type', 'kind']);
  // 텍스트 신호 보조 판단
  const t = resultText(res).toLowerCase();
  const signal = /captcha|2fa|two-factor|otp|verification|본인확인|인증번호|sso/.test(t);
  return { gated: gated || signal, type };
}
function looksLikeLoginForm(text) {
  return /password|비밀번호|로그인|sign in|log in/i.test(text || '');
}

// ---------- 잠금 ----------
function acquireLock(service, account, staleMinutes) {
  fs.mkdirSync(LOCK_DIR, { recursive: true, mode: 0o700 });
  const p = path.join(LOCK_DIR, `${service}.${account}.lock`.replace(/[^A-Za-z0-9._-]/g, '_'));
  const payload = JSON.stringify({ pid: process.pid, ts: Date.now() });
  try {
    fs.writeFileSync(p, payload, { flag: 'wx', mode: 0o600 });
    lockPath = p; return true;
  } catch (e) {
    if (e.code !== 'EEXIST') throw e;
    // 이미 있음 → stale 여부 확인
    try {
      const cur = JSON.parse(fs.readFileSync(p, 'utf8'));
      const ageMin = (Date.now() - (cur.ts || 0)) / 60000;
      if (ageMin > (staleMinutes || 5)) { fs.writeFileSync(p, payload, { mode: 0o600 }); lockPath = p; return true; }
    } catch { /* 손상된 락 → 회수 */ fs.writeFileSync(p, payload, { mode: 0o600 }); lockPath = p; return true; }
    return false; // 신선한 락 = 사용 중
  }
}

// ---------- 볼트 확인 (이름만, 비밀 안 봄) ----------
function vaultHasName(refName) {
  const res = ocSpawn(['vault', 'list', '--json']);
  if (!res.ok && res.unavailable) return { unavailable: true };
  const names = [];
  if (res.raw) {
    const arr = Array.isArray(res.raw) ? res.raw : (res.raw.names || res.raw.credentials || []);
    for (const n of arr) names.push(typeof n === 'string' ? n : deepFind(n, ['name']));
  } else {
    // 비-JSON 출력: 줄 단위 이름
    for (const line of res.text.split(/\r?\n/)) { const t = line.trim(); if (t) names.push(t); }
  }
  return { has: names.filter(Boolean).includes(refName) };
}
function vaultRefName(ref) {
  return typeof ref === 'string' && ref.startsWith('vault://') ? decodeURIComponent(ref.slice('vault://'.length)) : null;
}

// ========================= 메인 흐름 =========================
function main() {
  const service = args.service, account = args.account;
  if (!service || !account) finish('bad_request', {});

  // config 로드
  const cfgPath = args.config || process.env.MANAGED_LOGIN_CONFIG || path.resolve('managed-login.json');
  let cfg;
  try { cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8')); }
  catch { finish('not_enabled', { service, account }); }

  if (cfg.enabled !== true) finish('not_enabled', { service, account });
  const svc = cfg.services && cfg.services[service];
  if (!svc) finish('service_unknown', { service, account });
  const acc = svc.accounts && svc.accounts[account];
  if (!acc) finish('account_unknown', { service, account });

  const allowedDomains = svc.allowedDomains || [];
  const allowedRedirects = svc.allowedRedirects || allowedDomains;
  const expectedIdentity = acc.expectedIdentity;
  const maxAttempts = Number(cfg.maxLoginAttempts) > 0 ? Number(cfg.maxLoginAttempts) : 3;
  const staleMin = Number(cfg.lockStaleMinutes) > 0 ? Number(cfg.lockStaleMinutes) : 5;

  // AI가 넘긴 기대 신원과 승인된 config가 어긋나면 = 안전 중단
  if (args.expected && expectedIdentity && String(args.expected) !== String(expectedIdentity)) {
    finish('account_identity_mismatch', { service, account });
  }

  // 볼트에 비번 참조 이름이 있는가 (없으면 안전 실패)
  const pwName = vaultRefName(acc.passwordRef);
  if (!pwName) finish('credentials_missing', { service, account });
  const vres = vaultHasName(pwName);
  if (vres.unavailable) finish('tool_unavailable', { service, account });
  if (!vres.has) finish('credentials_missing', { service, account });

  // 잠금
  let locked;
  try { locked = acquireLock(service, account, staleMin); }
  catch { finish('tool_unavailable', { service, account }); }
  if (!locked) finish('account_in_use', { service, account });

  // 로그인 페이지 열기 (도메인은 우리가 통제 → 임의 URL 입력 방지)
  const created = tabsCreate(svc.loginUrl);
  if (created.unavailable) finish('tool_unavailable', { service, account });
  const tabId = created.tabId;
  if (!tabId) finish('tool_unavailable', { service, account });

  // 4단계: 현재 도메인 허용 확인
  let host = hostOf(currentUrl(tabId));
  if (!domainAllowed(host, allowedDomains)) finish('domain_not_allowed', { service, account, domain: host });

  // 5단계: 이미 로그인?
  let text = pageText(tabId);
  if (expectedIdentity && text.includes(expectedIdentity) && !looksLikeLoginForm(text)) {
    finish('success', { service, account, domain: host, identityChecked: true });
  }

  // 6단계: 게이트(캡차·2FA·본인확인)면 사용자 인계
  if (gateStatus(tabId).gated) finish('needs_user_verification', { service, account, domain: host });

  // 7단계: 입력·제출 (기존값 제거, vault:// 참조만 넘김). 입력~제출 구간엔 화면 캡처/덤프 안 함.
  const fields = {};
  if (acc.usernameField) fields[acc.usernameField] = acc.usernameRef; // vault://... (또는 미지정)
  if (acc.passwordField) fields[acc.passwordField] = acc.passwordRef; // vault://...
  let attempts = 0, loginOk = false;
  while (attempts < maxAttempts && !loginOk) {
    attempts++;
    const fres = ocRun('fill_form', {
      tabId, fields, clear_first: true, submit: acc.submit || '', loginCheck: 'auto', intent: 'managed login',
    });
    if (!fres.ok && fres.unavailable) finish('tool_unavailable', { service, account, domain: host, attempts });
    const ftext = resultText(fres).toLowerCase();
    const failed = fres.raw?.isError === true || /login.?fail|still.*password|failure/.test(ftext);
    if (!failed) loginOk = true;
  }
  if (!loginOk) finish('login_failed', { service, account, domain: host, attempts });

  // 8단계: 제출 후 도메인/게이트 재확인
  host = hostOf(currentUrl(tabId));
  if (!domainAllowed(host, allowedRedirects)) finish('account_identity_mismatch', { service, account, domain: host, attempts }); // 미승인 도메인 이동 = 안전 중단
  if (gateStatus(tabId).gated) finish('needs_user_verification', { service, account, domain: host, attempts }); // 2FA 뒤늦게

  // 9단계: 신원 검증
  text = pageText(tabId);
  if (expectedIdentity && text.includes(expectedIdentity)) {
    finish('success', { service, account, domain: host, attempts, identityChecked: true });
  }
  // 불일치 → 안전 중단(가능하면 로그아웃은 코치가 처리하게 상태만 반환)
  finish('account_identity_mismatch', { service, account, domain: host, attempts });
}

process.on('uncaughtException', () => finish('login_failed', { service: args.service, account: args.account }));
main();
