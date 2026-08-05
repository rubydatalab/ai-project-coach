# managed-login — 도구 설계(계약)

관리형 자동 로그인 오케스트레이터. **정책을 코드가 강제**하고, 비밀값은 만지지 않는다.
비개발자 셀러는 이 도구를 직접 부르지 않는다 — 코치(browser-operator)가 조용히 호출한다.

## 형태
- 플러그인 번들 CLI: `node plugins/ai-employee-coach/tools/managed-login/managed-login.mjs`
- 코치가 Bash로 호출, **stdout에 상태 코드 JSON만** 출력. (MCP 툴 형태도 가능하지만, 비개발자 제품에선 MCP 서버를 하나 더 붙이지 않고 CLI가 단순·안전.)

## 인터페이스
```
managed-login.mjs --service <name> --account <alias> --expected "<identity>" [--config <path>]
```
- `--config` 없으면 env `MANAGED_LOGIN_CONFIG`, 그것도 없으면 작업폴더 `./managed-login.json`.
- 비밀·아이디 **원문은 인자에 없음.** 별칭만.

## 반환(상태 코드, stdout JSON — 비밀값 없음)
`success` · `needs_user_verification` · `account_identity_mismatch` · `credentials_missing` ·
`domain_not_allowed` · `account_in_use` · `login_failed`
보조: `not_enabled` · `service_unknown` · `account_unknown` · `tool_unavailable` · `platform_policy_block`
```json
{ "status": "success", "service": "coupang-wing", "account": "main", "identityChecked": true }
```

## 비밀값 격리 (openchrome pilot 볼트에 위임 — 새로 안 만듦)
- 비밀은 `openchrome vault`(AES-256-GCM, `~/.openchrome/vault`)에만. 참조는 `vault://이름`.
- 우리 도구는 config의 `vault://이름` **문자열만** openchrome에 넘긴다. openchrome이 서버 내부에서 평문 해석 + 결과에서 `<vault:이름>` 토큰으로 **평문 마스킹**(소스 확인: `resolveFormVaultFields`).
- 우리 코드·인자·stdout·감사로그 어디에도 평문이 흐르지 않는다.

## 알고리즘 (정책 강제 순서)
1. config 로드. `enabled=true` 아니면 → `not_enabled`. 서비스/계정 없으면 → `service_unknown`/`account_unknown`.
2. openchrome·pilot·볼트 확인: `openchrome vault list`에 `passwordRef` 이름 있어야. 없거나 볼트 접근 불가 → `credentials_missing`. openchrome 자체 없음 → `tool_unavailable`.
3. **잠금 획득**(계정별 lockfile, `lockStaleMinutes` 지나면 stale 회수). 이미 사용 중 → `account_in_use`.
4. `openchrome run tabs_create --arg url=<loginUrl> --reuse` → tabId. 현재 URL 도메인이 `allowedDomains`에 없으면 → `domain_not_allowed`(중단).
5. **이미 로그인?** `run read_page` 텍스트에 `expectedIdentity` 있고 로그인폼 없으면 → `success`(그대로 진행).
6. `run oc_gate_inspect` → 게이트(캡차·2FA·본인확인·SSO)면 → `needs_user_verification`(중단).
7. `run fill_form`: `fields={usernameField: vault://usernameRef, passwordField: vault://passwordRef}`, `clear_first=true`(기존값 제거), `submit=<submit>`, `loginCheck=auto`, `intent="managed login"`.
   - **입력~제출 구간엔 스크린샷/DOM 덤프를 만들지 않는다**(도구가 이 구간을 원자적으로 처리 → 가드레일이 코드에 내재). 실패 감지되면 `maxLoginAttempts`까지만 재시도, 초과 → `login_failed`.
8. 제출 후: `run read_page`로 (a) 현재 도메인이 `allowedRedirects`에 있는지 — 미승인 도메인 이동이면 즉시 중단 → `account_identity_mismatch`(안전중단), (b) `run oc_gate_inspect` 재확인(2FA 뒤늦게 뜸) → `needs_user_verification`.
9. **신원검증**: 텍스트에 `expectedIdentity` 있으면 → `success`. 없으면 로그아웃 시도/안전중단 후 → `account_identity_mismatch`.
10. 잠금 해제. 상태만 출력. **감사로그**(`~/.openchrome/managed-login-audit.log` 등)엔 시각·서비스·계정별칭·도메인·상태만 — 비밀값 없음.

## 필수 보안 조건 매핑
- 원문 미노출: vault:// 위임 + openchrome 마스킹 + 우리 도구가 평문 미보유. ✅
- 입력 중 스크린샷/DOM 덤프 금지: 도구가 fill 구간 원자 처리, 코치 문서가 "로그인 중 화면 안 찍음" 명시. ✅
- 브라우저 저장비번/자동완성 미사용: 볼트만 소스. (프로필 비번관리자 사용 안 함.) ✅
- 폼 기존값 제거: `clear_first=true`. ✅
- 허용 도메인/승인 리디렉션만: 4·8단계 도메인 검사. 임의 URL·외부 프레임·새 미승인 도메인엔 입력 안 함. ✅
- 게이트 → `needs_user_verification`: 6·8단계. ✅
- 신원 불일치 → 로그아웃/중단 + `account_identity_mismatch`: 9단계. ✅
- 동시 사용 잠금 + 재시도 제한: 3·7단계. ✅
- 플랫폼 상위정책이 막으면 우회 안 하고 → `platform_policy_block`. ✅
- 미허용 프로젝트는 기존 수동 인계 유지(일괄 완화 금지): `enabled=false` 기본. ✅

## 안 되는/제약 (정직)
- **신원검증**은 서비스마다 계정명/업체명 위치가 달라, 텍스트 포함 검사(1차) + 필요 시 서비스별 셀렉터(2차)로 보강. 여기가 가장 깨지기 쉬움.
- pilot은 **옵트인**: 기본 번들은 pilot 미포함. 관리형 로그인 켠 프로젝트만 pilot 켠 openchrome 사용(전 셀러 도구표면 확대 방지).
- 실서비스 스모크는 **명시 승인 후만**. 자동 테스트는 가짜 로그인 페이지 + 가짜 볼트로.
