# 해답 — SEA THE ANSWER

**선내 문서의 근거와 운항 기록을 연결하는 선박 업무 지원 앱입니다.**

문서 검색에서 끝나지 않고, 근거 확인 → 운항 정보 조회 → 보고서 초안 → 관리자 검토·승인까지 하나의 업무 흐름으로 연결합니다.

**정호영 · Backend & AI Integration**  
`Python` `FastAPI` `PostgreSQL` `LLM API` `pytest` `Playwright` `Docker Compose`

[팀 코드·실행 안내](https://github.com/dudco/sea-the-answer) · [개인 PR 목록](https://github.com/dudco/sea-the-answer/pulls?q=is%3Apr+author%3Acxo-ca) · [시스템 구조](https://github.com/dudco/sea-the-answer/blob/main/docs/architecture.md)

> 이 저장소는 팀 프로젝트의 **개인 기여 안내용 포크**입니다. 이 저장소의 `main`에는 README만 있으며, 실행 가능한 최신 통합 코드는 [dudco/sea-the-answer](https://github.com/dudco/sea-the-answer)에서 관리합니다. 아래 기여는 제가 작성한 PR을 기준으로 정리했습니다.

## 핵심 기여

| 해결한 문제 | 구현과 결과 | 코드·검토 기록 |
|---|---|---|
| 검색·계산·보고서가 분리된 초기 서비스 흐름 | 문서 수집·검색, 근거 확인, 보고서 저장, 운항 계산 API와 화면을 연결한 초기 MVP를 구현했습니다. | [#1 · 병합](https://github.com/dudco/sea-the-answer/pull/1) |
| API·DB 전환과 데이터 변경의 안정성 | 기존 API를 FastAPI로 이전하고 PostgreSQL 초기 스키마·SQLite 이전 도구·`uv` 실행 환경을 구성했습니다. 백업·복구와 동시 수정 충돌 검사를 추가했습니다. | [#7 · 병합](https://github.com/dudco/sea-the-answer/pull/7) |
| 특정 모델 공급자에 고정된 호출 | OpenAI 호환 Chat Completions 설정과 공급자별 인증키 분리를 구현했습니다. JSON·원문 인용 검증과 실패 시 발췌 전환을 유지했습니다. | [#13 · 병합](https://github.com/dudco/sea-the-answer/pull/13) |
| 로그인 없는 업무 조회와 공용 관리자 계정 의존 | 선원·관리자 개인 로그인, 최초 비밀번호 변경, 세션 만료·회수와 서버 권한 검사를 구현했습니다. 자기 보고서 업무와 관리자 승인·계정 관리 권한을 구분했습니다. | [#18 · 병합](https://github.com/dudco/sea-the-answer/pull/18) |
| 모델 연결 성공과 답변 품질을 구분하기 어려움 | 한국어 고정 근거 **16사례**와 평가 CLI를 추가해 입력·코드 해시, 오류 유형, 소요 시간, 인용 일치를 기록했습니다. 의미적 정답성은 사람 검토로 남깁니다. | [#20 · 병합](https://github.com/dudco/sea-the-answer/pull/20) |
| 재로그인 직후 보고서 생성 실패 | 운항 정보 준비 전 Noon/MRV 버튼을 잠그고, 지연 응답 후 올바른 선박으로 초안이 생성되는 브라우저 회귀를 추가했습니다. | [#20 · 병합](https://github.com/dudco/sea-the-answer/pull/20) |

CI는 기능 PR과 분리해 [#14](https://github.com/dudco/sea-the-answer/pull/14)로 제안했습니다. **검토 중이며 팀 `main`에 병합되지 않았습니다.** PR 상태 확인: **2026-11-03**.

## 검증 근거

아래 수치는 이번 README 수정에서 새로 실행한 결과가 아니라, **PR #20의 2026-10-28~29 검증 기록**입니다.

| 범위 | 확인한 내용 |
|---|---|
| Backend / scripts | 최신 팀 코드 통합 후 실제 PostgreSQL의 격리 DB에서 **533 통과 · 4 건너뜀**. 제외 4건은 별도 해사 데이터셋이 필요한 기존 테스트입니다. |
| Frontend / Docker | frontend 단위 테스트 **20 통과**, Next.js Docker production 빌드 성공. |
| Compose / 브라우저 | **8건 통과**: 실제 브라우저 → API → PostgreSQL 업무 흐름 1건과 모의 API UI·지연 응답 회귀 7건. 이 실행에서는 모델을 비활성화했습니다. |
| 실제 로컬 모델 | 브라우저 → 인증 API → 실제 DB → Ollama에서 가상 한국어 단문 생성·원문 인용과 모델 오류 시 발췌 전환을 확인했습니다. 별도 컨테이너 → 호스트 Ollama 호출도 확인했습니다. |

일반 한국어 답변 품질 개선은 입증하지 못했습니다. 고정 근거 비교에서 시간 초과·응답 검증 실패와 의미 오류를 관측했으며, 인용 일치나 연결 성공을 정답률로 해석하지 않습니다. 자세한 환경·실패·미검증 범위는 [PR #20](https://github.com/dudco/sea-the-answer/pull/20)과 [변경 이력](https://github.com/dudco/sea-the-answer/blob/main/docs/changelog.md)에 있습니다.

## 현재 팀 앱의 범위

| 영역 | 현재 구현 |
|---|---|
| 화면·실행 | Next.js / React → FastAPI → PostgreSQL, Docker Compose로 실행 |
| 문서 검색 | 권한·활성 개정·선택 문서 범위 적용 후 한국어 형태소 분석(Kiwi)·한영 동의어 확장·BM25 검색 |
| 답변 | 기본 원문 발췌, 선택적 OpenAI 호환 LLM, JSON·근거 ID·원문 인용 검증 |
| 업무 | 문서·운항 조회, 계산, Noon/MRV 검토 초안, 편집·검토 요청·관리자 승인 |
| 운영 | 개인 계정·역할, 변경·질의 로그, 버전 충돌 검사, 백업·복구 |

이 표는 **팀 전체 구현 범위**이며 개인 기여 범위는 위 PR 표를 기준으로 확인할 수 있습니다. 벡터·하이브리드 RAG, 공식 CII 계산, 규정 적용 자동 판정, DOCX·PPT 등록은 아직 연결 전입니다. 최신 범위는 [팀 README](https://github.com/dudco/sea-the-answer#readme)를 따릅니다.

## 코드와 문서 살펴보기

| 확인할 내용 | 바로가기 |
|---|---|
| 설치·실행·개발·테스트 | [팀 README](https://github.com/dudco/sea-the-answer#readme) |
| 서비스 경계·요청 흐름 | [시스템 구조](https://github.com/dudco/sea-the-answer/blob/main/docs/architecture.md) |
| 계정·권한 설계 | [인증 명세](https://github.com/dudco/sea-the-answer/blob/main/docs/specs/authentication.md) · [ADR 0016](https://github.com/dudco/sea-the-answer/blob/main/docs/adr/0016-crew-admin-authentication.md) |
| 모델 공급자·인용 검증 계약 | [LLM 명세](https://github.com/dudco/sea-the-answer/blob/main/docs/specs/llm-provider.md) |
| 한국어 고정 근거 평가 | [평가 코드](https://github.com/dudco/sea-the-answer/blob/main/scripts/evaluate_llm.py) · [16사례](https://github.com/dudco/sea-the-answer/blob/main/scripts/fixtures/korean-llm-eval.json) |
| 전체 문서·검증 이력 | [문서 목록](https://github.com/dudco/sea-the-answer/blob/main/docs/README.md) · [변경 이력](https://github.com/dudco/sea-the-answer/blob/main/docs/changelog.md) |

실행하려면 **팀 저장소**를 내려받아 팀 README의 관리자 초기 설정과 Docker 실행 절차를 따르세요. 공개 기본 비밀번호는 없으며 개인 관리자 설정이 필요합니다.
