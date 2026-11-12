# FOLIO Study Studio v2 — 실기기 PDF QA 체크리스트

> 2026-11-12 · Draft PR #3 전용 · **실기기 테스트 미수행 (NOT RUN)**  
> W01/W02 동결, W03 미승인. Private 저장소, 실사용 PDF 수집·외부 업로드·AI/STT/Supabase·과금·공개 Pages 배포 금지.

## 1. 검사 전 준비

- **대상 기기:** (A) iPhone + Safari, (B) iPad + Safari(세로/가로), (C) Galaxy Tab + Samsung Internet(세로/가로). 외부 키보드가 있는 기기에서만 키보드 항목을 수행하고 미연결이면 N/A로 남깁니다.
- **방문 주소:** 공개 Pages URL 사용 금지. 필요 시 개발 PC의 **신뢰 가능한 폐쇄형 로컬 네트워크**에서 정적 `index.html` 및 `styles/`을 임시 서빙합니다. 기기에서 HTTP 주소 접속 전 PC 방화벽/공유기 접근 범위를 확인합니다. Wi-Fi에 연결된 다른 사용자가 접근할 수 있는 환경은 피합니다. 실기기 접속 방법이 불확실하면 해당 항목 NOT RUN 유지.
- **검사 파일:** 개인정보·저작권 제약이 없는 **합성 PDF**를 기기에 미리 저장합니다. 테스트용 파일은 최소 3쪽, 한국어 텍스트, 컬러 도형, 가로로 긴 도표, 수식, 여러 페이지 레이아웃을 포함합니다. 파일명은 단순 영문, 크기는 20MB 이내.
- **개인정보:** 실강의/실사용 PDF를 선택하거나 GitHub Actions·이메일·공개 저장소로 전송하지 않습니다. 스크린샷은 합성 콘텐츠만 포함하고 네트워크/파일 경로/개인 식별정보를 노출하지 않습니다.
- **버전 기록:** 기기 모델/OS/브라우저 버전, 네트워크 경로, 브랜치 및 정확한 PR HEAD SHA, 검사 일시(Asia/Seoul), 테스트 파일 페이지 수·크기(내용 제외).

## 2. 공통 검증 항목

검사는 각 기기·방향마다 반복합니다. 모든 문항은 **PASS / FAIL / BLOCKED / NOT RUN / N/A** 중 하나로 기록합니다. 브라우저 내부 PDF 도구막대나 PDF 렌더링 기능은 우리 웹페이지가 통제할 수 없으므로 실제 동작을 관찰한 경우에만 PASS로 기록합니다.

| ID | 동작 | 통과 기준 | iPhone Safari | iPad Safari | Galaxy Tab Internet |
|---|---|---|---|---|---|
| PDF-01 | 기기 파일 선택 | 파일 선택기에서 합성 PDF를 고르면 외부 업로드 없이 파일명·PDF가 표시 | NOT RUN | NOT RUN | NOT RUN |
| PDF-02 | 브라우저 내장 보기 | iframe 내부 PDF가 표시되는지, 외부 보기로 전환되는지, 빈 화면인지 **실제 결과** 기록 (자동 통과 간주 금지) | NOT RUN | NOT RUN | NOT RUN |
| PDF-03 | 1→2→3→2쪽 이동 | 표시 페이지와 컨트롤의 숫자가 일치하며 페이지 이동 후 키보드/터치 조작 가능. 내장 뷰어가 페이지 해시를 무시하면 FAIL + 증거 | NOT RUN | NOT RUN | NOT RUN |
| PDF-04 | 확대 100→130→160% | 줌 표시가 바뀌고 내장 뷰어의 실제 문서 크기 변화가 관찰됨 (표시값만 변하면 FAIL) | NOT RUN | NOT RUN | NOT RUN |
| PDF-05 | 축소 160→100→70% | 실제 PDF 가독성·배율을 확인하고 70% 미만 감소하지 않음 | NOT RUN | NOT RUN | NOT RUN |
| PDF-06 | 맞춤 보기 | 선택 시 100%로 돌아오며 조작 버튼이 동작 | NOT RUN | NOT RUN | NOT RUN |
| PDF-07 | 원본/다크 색상 전환 | 색상이 바뀌고 기존 PDF 파일·페이지·줌 및 도구바가 유지됨 | NOT RUN | NOT RUN | NOT RUN |
| PDF-08 | 가로·세로 스크롤 | 확대 후 문서 상하와 **좌우 양 끝**을 실제로 읽을 수 있음. 내장 PDF 뷰어가 스크롤을 자체 처리하는지 함께 기록 | NOT RUN | NOT RUN | NOT RUN |
| PDF-09 | 핀치/두 손가락 제스처 | 화면 확대/스크롤과 문서 자체의 확대를 구분해 기록. PDF 조작을 막거나 화면 이탈하면 FAIL 또는 BLOCKED + 이유 | NOT RUN | NOT RUN | NOT RUN |
| PDF-10 | 작업 화면 전환 | PDF↔설명↔문제로 전환 후 PDF로 돌아올 수 있고, 탭 접근/터치 입력이 정상 | NOT RUN | NOT RUN | NOT RUN |
| PDF-11 | 방향 변경 | 회전해도 PDF 및 두 패널/단일 패널이 정상 노출되고 문서 밖 화면 가로 넘침 없음 | NOT RUN | NOT RUN | NOT RUN |
| PDF-12 | PDF 교체 | 다른 합성 PDF를 선택하면 이전 파일의 내용이 보이지 않고 새 PDF 첫 페이지가 열림 | NOT RUN | NOT RUN | NOT RUN |

## 3. 키보드·접근성 추가 확인

| ID | 검사 | 통과 기준 | 판정 |
|---|---|---|---|
| KBD-01 | 외부 키보드 Tab/Shift+Tab | PDF 파일 열기, 색상 전환, 맞춤 보기, 이전/다음 쪽, −/＋ 버튼에 접근 가능 | NOT RUN |
| KBD-02 | 색상 전환 Enter/Space | 키보드 초점이 버튼에 남고 토글 상태가 보조기술에 전달됨 | NOT RUN |
| KBD-03 | 페이지 이동 Enter/Space | 이동 후 도구 버튼 키보드 초점이 사라지지 않음 | NOT RUN |
| KBD-04 | 확대 70%/160% 경계 | 불가능한 방향의 줌 버튼이 실제 비활성화되고 반대 방향은 사용 가능 | NOT RUN |
| KBD-05 | 패널 분할 키보드 이동 | 태블릿 가로/세로 30~70% 제한과 스크린리더 분리선 설명이 일치 | NOT RUN |
| A11Y-01 | VoiceOver/TalkBack | 라벨, 현재 탭, 색상 전환 눌림 상태, PDF 뷰어 진입·탈출 안내와 포커스 순서 확인 | NOT RUN |

## 4. 기록 템플릿 / 종료 판정

```text
기기/OS/브라우저:
실기기 검사 시각(KST):
정확한 PR HEAD:
검사 파일 종류/쪽수/크기 (내용 업로드 금지):
ID / 결과(PASS|FAIL|BLOCKED|NOT RUN|N/A) / 재현 절차:
기대 동작:
실제 동작:
합성 데이터만 포함한 로컬 증거 위치:
브라우저 내장 PDF 제약 또는 네트워크 제약:
후속 조치/담당:
```

- **FAIL:** 재현 절차·증거·브라우저 버전 기록 후 별도 Draft PR 조치 여부 판단.
- **BLOCKED:** 테스트 환경 준비 불가, PDF가 내장 iframe에 열리지 않음 등 원인을 기록. 단순 테스트 미수행을 PASS로 바꾸지 않습니다.
- **기기 검증 완료 선언 금지:** 세 기기의 PDF-01~12 결과가 수집되지 않았고 키보드·접근성이 미검증이면 자동화 CI 성공과 별개로 **실기기 QA HOLD**.
- **자동화 범위:** Playwright Chromium/WebKit은 iframe DOM, URL fragment, 줌 컨트롤, 탭/키보드, 페이지 이동, 로컬-only 네트워크, synthetic demo 캡처를 검사할 뿐 iOS/Samsung 내장 PDF 동작을 보증하지 않습니다.
