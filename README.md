# 해답 — SEA THE ANSWER

선내 문서의 근거와 운항 기록을 함께 보여 주는 선박 업무 지원 앱입니다. 팀의 최신 통합 코드는 **[dudco/sea-the-answer](https://github.com/dudco/sea-the-answer)**에서 관리합니다.

이 저장소의 `main`은 개인 작업과 팀 PR을 안내하는 페이지입니다. 앱을 실행하려면 팀 저장소를 사용하세요.

## 프로젝트

| 항목 | 내용 |
|---|---|
| 화면 | Next.js / React |
| API | Python / FastAPI |
| 데이터베이스 | PostgreSQL |
| 실행 환경 | Docker Compose, backend 패키지 관리 `uv` |
| 주요 흐름 | 통합 질문·문서 근거 확인, 운항 정보 조회·계산, 보고서 작성·승인 |

문서 검색은 현재 키워드 기반입니다. 벡터·하이브리드 RAG와 공식 CII 계산은 후속 통합 범위이며, 선택적 LLM 답변은 OpenAI 호환 Chat Completions로 연결합니다. 최신 구현·제한은 [팀 README](https://github.com/dudco/sea-the-answer#readme)를 기준으로 확인하세요.

## 개인 기여와 PR

| 작업 | 내용 | 상태 |
|---|---|---|
| [PR #1](https://github.com/dudco/sea-the-answer/pull/1) | 문서 검색·근거 확인·보고서·계산 도구를 연결한 초기 MVP | 병합 완료 |
| [PR #7](https://github.com/dudco/sea-the-answer/pull/7) | FastAPI 이전, PostgreSQL 초기 스키마·SQLite 이전 도구, uv, 백업·복구·동시 수정 처리 | 병합 완료 |
| [PR #13](https://github.com/dudco/sea-the-answer/pull/13) | OpenAI 호환 LLM 설정, 공급자별 인증키 분리, JSON·인용 검증과 실패 시 발췌 흐름 검증 | 병합 완료 |
| [PR #14](https://github.com/dudco/sea-the-answer/pull/14) | backend·frontend·Docker Compose e2e 검증 워크플로 분리 | 검토 중 |

상태 확인: **2026-10-18**. PR별 검증 기록과 실제 외부 모델 호출의 미검증 범위는 각 PR 본문에 있습니다.

## 실행·설계·검증 안내

- [팀 저장소의 실행 방법](https://github.com/dudco/sea-the-answer#실행하기-docker)
- [시스템 구조](https://github.com/dudco/sea-the-answer/blob/main/docs/architecture.md)
- [API 명세](https://github.com/dudco/sea-the-answer/blob/main/docs/specs/api.md)
- [LLM 공급자 계약](https://github.com/dudco/sea-the-answer/blob/main/docs/specs/llm-provider.md)
- [변경 이력·검증 기록](https://github.com/dudco/sea-the-answer/blob/main/docs/changelog.md)
