# 해답 — SEA THE ANSWER

**선내 문서의 근거와 운항 기록을 연결하는 선박 업무 지원 앱입니다.**

문서 검색에서 끝나지 않고, 근거 확인 → 운항 정보 조회 → 보고서 초안 → 관리자 검토·승인까지 하나의 업무 흐름으로 연결합니다.

**정호영 · Backend & AI Integration**  
`Python` `FastAPI` `PostgreSQL` `LLM API` `pytest` `Playwright` `Docker Compose`

[팀 코드·실행 안내](https://github.com/dudco/sea-the-answer) · [개인 PR 목록](https://github.com/dudco/sea-the-answer/pulls?q=is%3Apr+author%3Acxo-ca) · [시스템 구조](https://github.com/dudco/sea-the-answer/blob/main/docs/architecture.md)

> 이 저장소는 팀 프로젝트의 **개인 기여 안내용 포크**입니다. 이 저장소의 `main`에는 README만 있으며, 실행 가능한 최신 통합 코드는 [dudco/sea-the-answer](https://github.com/dudco/sea-the-answer)에서 관리합니다. 아래 기여는 제가 작성한 PR을 기준으로 정리했습니다. **PR 상태 확인: 2026-11-18.**

## 팀에 반영된 개인 기여

| 해결한 문제 | 구현과 결과 | 코드·검토 기록 |
|---|---|---|
| 검색·계산·보고서가 분리된 초기 서비스 흐름 | 문서 수집·검색, 근거 확인, 보고서 저장, 운항 계산 API와 화면을 연결한 초기 MVP를 구현했습니다. | [#1 · 병합](https://github.com/dudco/sea-the-answer/pull/1) |
| API·DB 전환과 데이터 변경의 안정성 | 기존 API를 FastAPI로 이전하고 PostgreSQL 초기 스키마·SQLite 이전 도구·`uv` 실행 환경을 구성했습니다. 백업·복구와 동시 수정 충돌 검사를 추가했습니다. | [#7 · 병합](https://github.com/dudco/sea-the-answer/pull/7) |
| 특정 모델 공급자에 고정된 호출 | OpenAI 호환 Chat Completions 설정과 공급자별 인증키 분리를 구현했습니다. JSON·원문 인용 검증과 실패 시 발췌 전환을 유지했습니다. | [#13 · 병합](https://github.com/dudco/sea-the-answer/pull/13) |
| 로그인 없는 업무 조회와 공용 관리자 계정 의존 | 선원·관리자 개인 로그인, 최초 비밀번호 변경, 세션 만료·회수와 서버 권한 검사를 구현했습니다. 자기 보고서 업무와 관리자 승인·계정 관리 권한을 구분했습니다. | [#18 · 병합](https://github.com/dudco/sea-the-answer/pull/18) |
| 모델 연결 성공과 답변 품질을 구분하기 어려움 | 한국어 고정 근거 **16사례**와 평가 CLI를 추가해 입력·코드 해시, 오류 유형, 소요 시간, 인용 일치를 기록했습니다. 재로그인 직후 보고서 생성 오류도 수정하고 지연 응답 회귀를 추가했습니다. | [#20 · 병합](https://github.com/dudco/sea-the-answer/pull/20) |
| 표·차트 요청이 문장으로만 표시되고 모델 입력량이 늘어남 | 행별 인용을 갖춘 문서 표와 DB에 저장된 운항 기록 차트를 API·화면에 연결했습니다. 입력·표시·호출 시간 제한, 입력량 평가와 저장된 답변의 사람 검토 CLI를 추가했습니다. | [#22 · 병합](https://github.com/dudco/sea-the-answer/pull/22) |
| 기능 변경마다 실행·검증 범위를 확인하기 어려움 | backend pytest, frontend 테스트·빌드, 격리된 Docker Compose 브라우저 검증을 GitHub Actions로 구성했습니다. **2026-11-04 팀 `main`에 병합되었습니다.** | [#14 · 병합](https://github.com/dudco/sea-the-answer/pull/14) |
| 운항 시나리오를 같은 조건으로 재현하기 어려움 | 인천–포트사이드 편도·왕복 시뮬레이터와 CSV/JSON 내보내기, 기존 관리자 API 게시 도구를 구현했습니다. 왕복 **60건**은 가상 기록이며 귀항 **32건**은 가상 예상으로 구분합니다. | [#26 · 병합](https://github.com/dudco/sea-the-answer/pull/26) |

### 검토 중인 후속 작업

[**#32 · 선박 약칭·과거 날짜 위치 조회·후속 질문 문맥**](https://github.com/dudco/sea-the-answer/pull/32)은 **열린 PR이며 팀 `main`에 아직 병합되지 않았습니다.** 질문에 지정한 날짜만 조회하고, 같은 소유 대화의 검증된 선박·기간을 이어받도록 보완했습니다. 해당 날짜의 기록이 없으면 다른 날짜의 좌표로 대신 답하지 않도록 했습니다.

## 검증 근거와 한계

아래는 **각 PR에 기록된 당시 결과**이며, 이번 README 수정에서 테스트를 새로 실행한 결과가 아닙니다. 서로 다른 커밋·환경·검사 범위의 수치를 합산하지 않습니다.

| 기준 | 기록된 검증 | 해석 범위 |
|---|---|---|
| [#20 · 2026-10-28~29](https://github.com/dudco/sea-the-answer/pull/20) | 실제 PostgreSQL 격리 DB의 backend/scripts **533 통과·4 건너뜀**, frontend **20 통과·production 빌드**, Compose/브라우저 **8 통과** | 브라우저 8건은 실제 API·DB 업무 흐름 1건과 모의 API UI 7건입니다. 이 실행에서는 모델을 비활성화했습니다. |
| [#22 · 팀 통합 CI](https://github.com/dudco/sea-the-answer/actions/runs/41779440709) | PostgreSQL의 backend/scripts **682 통과·4 건너뜀**, frontend **26 통과·production 빌드**, Docker e2e **12 통과** | e2e 12건은 실제 DB 업무 흐름 1건과 모의 API UI 11건입니다. DB 운항 기록의 차트 값·문서 표·인용 열람을 확인했습니다. 건너뛴 4건은 별도 해사 데이터셋이 필요한 검사입니다. |
| [#26 · 가상 운항 재현](https://github.com/dudco/sea-the-answer/pull/26) | 로컬 집중 테스트 **45 통과**, 왕복 60건 대조, UTC 날짜별 누적·CSV 반입 검사 | 실제 운항의 정확도나 미래 항로 예측 성능을 검증한 결과가 아닙니다. |
| [#32 · 2026-11-17 PR CI](https://github.com/dudco/sea-the-answer/actions/runs/44025874504) | 커밋 `973c3af`의 backend **1,321 통과·105 건너뜀**, frontend **40 통과·production 빌드**, Docker e2e **39 통과** | **미병합 PR의 결과**입니다. 모델 선택 fixture, 모델 미설정 경로와 모의 API UI를 포함하며 실제 LLM 정확도나 운영 배포 결과를 뜻하지 않습니다. 건너뜀에는 추가 데이터·검색 엔진 등 선택 환경 조건이 포함됩니다. |

실제 Ollama의 가상 한국어 단문 생성·원문 인용과 모델 오류 시 발췌 전환, 컨테이너 → 호스트 연결은 #20에서 확인했습니다. 그러나 **일반 한국어 답변 품질 개선은 입증하지 못했습니다.** #22의 `qwen2.5:3b` 입력량 시험 3건은 시간 초과 2건과 기술적 인용 통과 1건이었고, 인용을 통과한 답변에도 기대 사실 누락이 있었습니다. 실제 모델 생성 표의 성공도 확인하지 못했습니다. 연결·형식·인용 검사와 의미적 정답성은 구분하며, 의미 품질은 사람이 근거와 대조해 검토합니다.

자세한 환경·실패·미검증 범위는 각 PR과 [팀 변경 이력](https://github.com/dudco/sea-the-answer/blob/main/docs/changelog.md)에 기록되어 있습니다.

## 현재 팀 앱의 범위

아래는 **2026-11-18에 확인한 팀 README 기준의 전체 구현 범위**입니다. 제 개인 기여는 위 PR 표를 기준으로 확인할 수 있습니다.

| 영역 | 팀 문서에 정리된 현재 구현 |
|---|---|
| 화면·실행 | Next.js / React → FastAPI → PostgreSQL, Docker Compose로 실행 |
| 문서 검색 | 권한·활성 개정·선택 문서 범위를 확인하고 BM25와 로컬 E5 벡터 결과를 RRF로 결합. 키워드 검색은 OpenSearch/Nori 사용 |
| 답변·표시 | 원문 발췌와 선택적 OpenAI 호환 LLM, JSON·근거 ID·원문 인용 검증, 문서 근거 표·DB에 저장된 운항 기록 차트 |
| 업무 | 통합 질문·운항 조회·비교, 업무 스킬, Noon/MRV 검토 초안, 편집·검토 요청·관리자 승인 |
| 운영 | 개인 계정·역할, 변경·질의 로그, 버전 충돌 검사, 백업·복구, CI |

공식 CII 계산, 규정 적용 자동 판정, DOCX·PPT 등록은 아직 연결 전입니다. 선택적 항구·선석 참조 기능은 공개 수치와 지침의 부분 비교이며 실제 입항 승인을 산정하지 않습니다. 상세 설정과 최신 범위는 [팀 README](https://github.com/dudco/sea-the-answer#readme)를 따릅니다.

## 코드와 문서 살펴보기

| 확인할 내용 | 바로가기 |
|---|---|
| 설치·실행·개발·테스트 | [팀 README](https://github.com/dudco/sea-the-answer#readme) |
| 서비스 경계·요청 흐름 | [시스템 구조](https://github.com/dudco/sea-the-answer/blob/main/docs/architecture.md) |
| 계정·권한 설계 | [인증 명세](https://github.com/dudco/sea-the-answer/blob/main/docs/specs/authentication.md) · [ADR 0016](https://github.com/dudco/sea-the-answer/blob/main/docs/adr/0016-crew-admin-authentication.md) |
| 모델 공급자·인용 검증 계약 | [LLM 명세](https://github.com/dudco/sea-the-answer/blob/main/docs/specs/llm-provider.md) |
| 한국어 고정 근거 평가 | [평가 코드](https://github.com/dudco/sea-the-answer/blob/main/scripts/evaluate_llm.py) · [16사례](https://github.com/dudco/sea-the-answer/blob/main/scripts/fixtures/korean-llm-eval.json) |
| 표·차트와 입력량·의미 검토 | [표시 계약](https://github.com/dudco/sea-the-answer/blob/main/docs/specs/answer-presentation.md) · [입력량 평가](https://github.com/dudco/sea-the-answer/blob/main/scripts/evaluate_llm_load.py) · [사람 검토 CLI](https://github.com/dudco/sea-the-answer/blob/main/scripts/review_llm.py) |
| 가상 운항 재현 | [왕복 시뮬레이터](https://github.com/dudco/sea-the-answer/blob/main/scripts/simulate_round_trip.py) · [게시 도구](https://github.com/dudco/sea-the-answer/blob/main/scripts/publish_simulated_voyage.py) |
| 전체 문서·검증 이력 | [문서 목록](https://github.com/dudco/sea-the-answer/blob/main/docs/README.md) · [변경 이력](https://github.com/dudco/sea-the-answer/blob/main/docs/changelog.md) |

실행하려면 **팀 저장소**를 내려받아 팀 README의 관리자 초기 설정과 Docker 실행 절차를 따르세요. 공개 기본 비밀번호는 없으며 개인 관리자 설정이 필요합니다.
