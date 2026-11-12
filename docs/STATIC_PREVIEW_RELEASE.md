# FOLIO Study Studio v2 — one-time static preview release decision

Date: 2026-11-12 KST  
Authorizing request: "다음 작업 이어서 하고 메인에도 올리고 깃으로 배포해서 시연 링크 줘"

## Approved scope

- Bring the previously verified, synthetic-only Study Studio v2 prototype into `main` after exact-SHA Chromium and WebKit full regression checks pass.
- Attempt to deploy a **publicly viewable static demonstration** through GitHub Pages, while preserving the **private source repository**. Public viewers can download the **published static HTML/CSS/JS**; do not treat the browser prototype as confidential.
- Include no real AI, speech transcription, database/storage, authentication, actual lecture materials, payment, credentials or user-data export.
- Host only `index.html`, `styles/studio-v2.css`, `.nojekyll`, and `robots.txt` in the Pages artifact. The private QA documentation, GitHub repo and browser artifacts remain private; the public bundle contains only synthetic learning examples and a local-only PDF input.
- Retain W01/W02 frozen and W03 integration Gate **NOT APPROVED**. Merging an already tested **visual prototype** to main does not approve service connections or real data handling.
- Existing Draft PR #2 and #3 are review artifacts and are not merged/rebased by this release. Instead use a new non-Draft, main-targeted release PR based on an exact copy of verified PR #3 HEAD. This does not rewrite history and avoids forcing a merge with the diverged PR #2 tip.

## Guard rails

1. Require the release PR's exact HEAD to pass full Chromium/WebKit regression and private screenshot QA.
2. Merge the release PR only after verifying the latest `main` and release HEAD match the inspected SHA and the PR is mergeable.
3. The publishing workflow also reruns all browser tests on merged `main` and deploys only after successful checks.
4. GitHub Pages in private repositories may require an eligible GitHub plan and the owner to enable **Settings → Pages → Source: GitHub Actions**. The normal `GITHUB_TOKEN` does not grant creation/enablement of Pages. A workflow failure caused by missing Pages settings is **not a successful deployment**; never fabricate a public URL.
5. Until an actual successful Pages Actions deployment and HTTP-accessible URL are checked, label deployment **HOLD**. If owner action is required, provide precise steps rather than change repository visibility or paid plan.
6. Hardware QA remains **NOT RUN**, including iPhone/iPad Safari, Galaxy Tab Samsung Internet and assistive technology.

## Follow-on

- Validate whether native mobile PDF viewer supports URL fragment paging/zoom with real devices separately.
- No hidden paid hosting, GitHub plan changes, repo public switch, secret provisioning, real PDF uploads or external AI/STT/Supabase integration.
