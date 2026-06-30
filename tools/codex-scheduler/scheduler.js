#!/usr/bin/env node
/*
 * Codex 예약 도구 (codex-scheduler)
 * --------------------------------
 * Codex CLI에는 Claude Code 같은 내장 cron이 없다. 이 작은 도구가 그 빈자리를 채운다.
 * 켜져 있는 동안, 예약표(schedule.json)의 5필드 cron을 보고 시각이 되면 `codex exec`를 깨운다.
 *
 * 핵심 원칙:
 *  - 무인 실행이므로 사람이 확인할 수 없다 → 모든 프롬프트 앞에 "안전 가드레일"을 붙인다.
 *    (읽기·요약·초안·파일정리만. 결제·발송·삭제·등록·대량변경 등 되돌리기 어려운 행동 금지.)
 *  - 실행 결과는 사람이 읽을 수 있는 기록 파일(md)로 남긴다.
 *  - 외부 npm 패키지에 의존하지 않는다(node 내장만). 셀러 환경을 더럽히지 않기 위해서.
 *
 * 사용:  node scheduler.js --file <예약표.json>
 */

'use strict';
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// ---- 인자 ----
function argOf(name, def) {
  const i = process.argv.indexOf(name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : def;
}
const SCHEDULE_FILE = path.resolve(argOf('--file', 'schedule.json'));
const TICK_MS = parseInt(argOf('--tick', '20000'), 10); // 점검 주기(기본 20초)

// 무인 실행이라 사람이 위험행동을 막을 수 없다 → 프롬프트마다 강제로 앞에 붙인다.
const SAFETY_GUARD =
  '[무인 예약 실행 — 사람이 지켜보지 않음] 읽기·정리·요약·초안 작성·파일 저장만 한다. ' +
  '결제·주문확정·발송·삭제·등록·대량변경 등 되돌리기 어려운 행동은 절대 하지 않는다. ' +
  '그런 게 필요하면 실행하지 말고 "사장님 확인 필요"라고 기록만 남긴다.\n\n실제 지시:\n';

function log(msg) {
  const t = new Date().toISOString().replace('T', ' ').slice(0, 19);
  console.log(`[${t}] ${msg}`);
}

function readSchedule() {
  const raw = fs.readFileSync(SCHEDULE_FILE, 'utf8');
  return JSON.parse(raw);
}

function writeSchedule(sched) {
  fs.writeFileSync(SCHEDULE_FILE, JSON.stringify(sched, null, 2), 'utf8');
}

// ---- 5필드 cron 매칭 (분 시 일 월 요일). *, n, */n, a-b, a,b 지원 ----
function fieldMatches(spec, value, min, max) {
  for (const part of String(spec).split(',')) {
    if (part === '*') return true;
    let step = 1, range = part;
    if (part.includes('/')) { const [r, s] = part.split('/'); range = r; step = parseInt(s, 10) || 1; }
    let lo, hi;
    if (range === '*') { lo = min; hi = max; }
    else if (range.includes('-')) { const [a, b] = range.split('-'); lo = parseInt(a, 10); hi = parseInt(b, 10); }
    else { lo = hi = parseInt(range, 10); }
    if (Number.isNaN(lo) || Number.isNaN(hi)) continue;
    for (let v = lo; v <= hi; v += step) if (v === value) return true;
  }
  return false;
}

function cronMatches(cron, now) {
  const f = cron.trim().split(/\s+/);
  if (f.length !== 5) { log(`잘못된 cron(5필드 아님): "${cron}"`); return false; }
  return (
    fieldMatches(f[0], now.getMinutes(), 0, 59) &&
    fieldMatches(f[1], now.getHours(), 0, 23) &&
    fieldMatches(f[2], now.getDate(), 1, 31) &&
    fieldMatches(f[3], now.getMonth() + 1, 1, 12) &&
    fieldMatches(f[4], now.getDay(), 0, 6) // 0=일요일
  );
}

// ---- 한 작업 실행: codex exec 호출 ----
function runJob(job, sched) {
  return new Promise((resolve) => {
    const cwd = job.cwd ? path.resolve(job.cwd) : process.cwd();
    const lastMsgFile = path.join(cwd, '.codex-scheduler-last.txt');
    const fullPrompt = SAFETY_GUARD + job.prompt;

    // Windows 포함 모든 환경에서 무인 쓰기가 되는 유일한 모드(샌드박스가 OS기능에 의존해
    // Windows에선 workspace-write가 읽기전용으로 떨어짐). 셀러 자기 PC에서만 돌린다는 전제.
    //
    // 프롬프트는 인자가 아니라 stdin으로 넘긴다. 긴 한글 프롬프트를 인자로 주면 shell이
    // 공백마다 쪼개 깨지기 때문(codex는 인자가 없으면 stdin에서 지시를 읽는다). 경로만 따옴표로 감싼다.
    const cmd =
      `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox ` +
      `-C "${cwd}" -o "${lastMsgFile}"`;

    log(`실행 시작: "${job.id}" (cwd=${cwd})`);
    const child = spawn(cmd, { cwd, shell: true });
    child.stdin.write(fullPrompt);
    child.stdin.end();
    let stderr = '';
    child.stderr.on('data', (d) => { stderr += d.toString(); });
    child.on('error', (e) => { finish(false, `codex 실행 실패: ${e.message}`); });
    child.on('close', (code) => {
      let last = '';
      try { last = fs.readFileSync(lastMsgFile, 'utf8').trim(); } catch (_) {}
      finish(code === 0, last || (code === 0 ? '(결과 메시지 없음)' : `종료코드 ${code} ${stderr.slice(-300)}`));
    });

    function finish(ok, summary) {
      log(`실행 끝: "${job.id}" — ${ok ? '성공' : '실패'}`);
      appendRecord(sched, job, ok, summary);
      try { fs.unlinkSync(lastMsgFile); } catch (_) {}
      resolve(ok);
    }
  });
}

// ---- 사람이 읽는 실행 기록(md) ----
function appendRecord(sched, job, ok, summary) {
  const recPath = path.resolve(sched.logFile || '실행기록.md');
  const t = new Date().toISOString().replace('T', ' ').slice(0, 16);
  const head = fs.existsSync(recPath) ? '' : '# 예약 실행 기록\n\n';
  const line = `- ${t} — **${job.id}** ${ok ? '✅ 실행함' : '⚠️ 실패'}\n  - ${String(summary).replace(/\n+/g, ' ').slice(0, 400)}\n`;
  fs.appendFileSync(recPath, head + line, 'utf8');
}

// ---- 메인 루프 ----
let busy = false;            // codex 실행은 길 수 있으니 동시에 하나만
const firedThisMinute = {};  // 같은 분에 중복 발동 방지: { jobId: 'YYYY-MM-DDTHH:MM' }

async function tick() {
  if (busy) return;
  let sched;
  try { sched = readSchedule(); }
  catch (e) { log(`예약표 읽기 실패(${SCHEDULE_FILE}): ${e.message}`); return; }

  const jobs = sched.jobs || [];
  if (jobs.length === 0) { log('남은 예약이 없어 종료합니다.'); process.exit(0); }

  const now = new Date();
  const minuteKey = now.toISOString().slice(0, 16);

  for (const job of jobs) {
    if (!job.cron || !job.prompt) continue;
    if (firedThisMinute[job.id] === minuteKey) continue;
    if (!cronMatches(job.cron, now)) continue;

    firedThisMinute[job.id] = minuteKey;
    busy = true;
    await runJob(job, sched);
    busy = false;

    // 일회성(recurring:false)이면 발동 후 예약표에서 제거(durable)
    if (job.recurring === false) {
      try {
        const cur = readSchedule();
        cur.jobs = (cur.jobs || []).filter((j) => j.id !== job.id);
        writeSchedule(cur);
        log(`일회성 작업 "${job.id}" 완료 — 예약표에서 제거.`);
      } catch (e) { log(`예약표 갱신 실패: ${e.message}`); }
    }
    break; // 한 틱에 하나만
  }
}

log(`예약 도구 시작. 예약표=${SCHEDULE_FILE}, 점검주기=${TICK_MS}ms`);
tick();
setInterval(tick, TICK_MS);
