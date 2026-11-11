# FOLIO — Human Web Design 도입 기록

- 기준점: 2026-11-11 private main 0045386d9c32e5d7c44fb9667f6efffbdcf79a85.
- 작업: 정적 시안에 적용할 태블릿 디자인 Skill과 운영 문서만 추가. index.html, VERIFICATION.json, .nojekyll은 변경하지 않음.
- 적용: .agents/skills/human-web-design/SKILL.md.
- 승인 기준선: Dark Workspace v1.2, 차콜/딥 네이비, 가로 태블릿 화면 바깥 여백 최소화, 좌우 패널별 PDF/AI 설명/문제 선택 및 분할 비율 조절.
- 반(反) AI 템플릿 판단: 의미 없는 아이콘·팁·장식 제거, PDF 텍스트 우선, 기능별 정보 밀도, 실제 학습 동작과 관계된 조작만 강조.
- 기능·보안 보호: PDF 외부 업로드, 녹음/AI/STT, 인증/DB/유료 API 도입 없음. Private 유지, Pages/공개 배포 금지.
- QA: 현재 GitHub Actions 정의 없음. 이후 UI 변경 시 HTML/JS 문법, 요청/네트워크 점검, 768/1024/1366px 태블릿 레이아웃, 좌우 컨텐츠 선택/패널 크기 조절과 키보드 동작을 검사하고 증거 기록.
- 이번 PR은 문서만 추가했으므로 신규 런타임/기기 검증을 수행했다고 주장하지 않음.
- 다음 후보: 좌우 패널에서 PDF 표시 영역에 불필요한 안내·아이콘이 남아 있는지 시안의 실제 화면을 보고 단일 개선 제안.
