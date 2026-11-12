# FOLIO — Draft PR #2 / #3 스택 동기화 검토안 (승인 전 READ-ONLY)

> 작성 2026-11-12 · **현재 상태 분석 및 향후 승인 절차만 정리**  
> 무단 `rebase`, `merge`, `cherry-pick`, `force-push`, PR base 변경, main 병합, Pages 배포 금지.

## 1. 현재 확인 상태

| 대상 | 사실 |
|---|---|
| 저장소 | `jkd04255/FOLIO`, Private |
| main | `1d314fc33527ebf8c52e3ce1b7cc9e09fe317568` |
| Draft PR #2 | `fix/w03-01-mobile-cross-pane-navigation-20261111`; HEAD `0985afb033d4efe0cd5bfe3028d092183cfaaea2`, base main, **미병합** |
| Draft PR #3 | `design/folio-study-studio-v2-20261111`, base PR #2 브랜치, **미병합** |
| 공통 조상 | `77ecb3aeeb7188cd52157bf2568c4539ce1342d5` |
| 알려진 분기 | PR #2 기준 PR #3은 **ahead 20 / behind 1** (2026-11-12 오전 확인 시점; 후속 커밋에 따라 ahead 수는 변동) |
| 기존 중복 수정 | `$$('.pane').forEach` / `$$('.phone-side').forEach` 교차 패널 전환 JS 버그픽스가 **양쪽 브랜치에 독립된 커밋**으로 반영되어 있으므로 단순 병합에서 patch conflict/중복 이력 위험이 있음 |

## 2. 변경 금지 범위

- `main`과 PR #2 브랜치는 변경하지 않음.
- PR #3은 승인된 **디자인·브라우저 QA용 Draft**로 유지; 새로운 기능 Gate인 W03 승인과 혼동하지 않음.
- 원래 Dark Workspace v1.2는 main의 승인 기준점으로 보존. W01/W02 동결, W03 미승인.
- 브랜치 자체를 정상화한다는 이유로 PR 병합·base 변경·이력 재작성·Pages 배포 실행 금지.

## 3. 후속 **별도 승인** 후 수행할 안전 절차

1. **사전 스냅샷:** 세 ref의 40자리 HEAD SHA, PR Draft/mergeable, Actions 상태, 변경 파일과 각 파일 SHA를 다시 읽고 인수인계서에 저장.
2. **내용 비교:** `PR #2 latest HEAD...PR #3 latest HEAD`의 실제 diff와 두 브랜치의 모바일 스위치 함수, `aria-current`, selector 루프, viewport/키보드 테스트를 대조. 패치가 내용상 같다는 증거 없이 자동 반영 금지.
3. **충돌 리허설(비파괴):** 보호된 본 브랜치에서 강제 리베이스하지 않고 임시 복제·오프라인 merge-tree 또는 읽기 전용 diff로 차이를 검증. 임시 remote branch 생성조차 별도 승인 필요.
4. **안전한 적용안 의사결정:** PR #2의 W03-01 수정이 실제 main에 들어갈 별도 승인을 받을 때까지 PR #3 base를 건드리지 않는 **현행 유지(A안)** 우선. 추후 PR #2 병합이 별도로 승인되고 main이 새로 확인되면, PR #3을 최신 main 기준으로 재구성할지/독립 Draft로 새 PR을 만들지 **별도 승인** 후 결정. 중복 패치가 있으면 cherry-pick 시 중복 제외/충돌 해결 검토.
5. **검증 게이트:** 승인된 변경 후 정확한 HEAD의 Chromium/WebKit **전항목 PASS**, 비공개 캡처/업로드 PASS, 외부 네트워크 요청 0, GitHub 원격 PR diff 및 main 불변 조건 재확인.
6. **실기기 검증:** `docs/REAL_DEVICE_PDF_QA.md`의 iPhone Safari/iPad Safari/Galaxy Tab Samsung Internet 항목을 **별도로 수행**하기 전까지 실기기 Gate HOLD.

## 4. 현재 판단

- **결론:** 사용자 승인 없이 안전한 브랜치 동기화를 실행하는 방법은 없음. 현재는 코드 보존 여부를 검사하고 비교 기록만 남겨야 함.
- **다음 액션:** PR #2 병합 승인 여부와 별도로 PR #3 스택을 어떻게 처리할지 승인된 이후에만 Git 이력 변경을 실행.
- 별도 승인 전에는 PR #3에 한정된 소규모 UI·테스트·문서 커밋은 가능하지만 본 브랜치 병합/리베이스는 불가.
