---
title: >-
    facet task
category: concepts
tags: [facet, index]
sources: ["url:https://arena.ai/blog/arena-category/", "url:https://arena.ai/blog/leaderboard-changelog", "url:https://arena.ai/blog/re-introducing-vision-arena-categories/", "url:https://themodelgap.com/data/benchmarks.json", "url:https://huggingface.co/api/datasets?filter=benchmark:official"]
summary: >-
    작업 유형. LMArena 카테고리 이름을 기본 어휘로 쓰고, Arena에 없는 에이전트 작업 유형은 The Model Gap 벤치마크로 채운다.
base_confidence: 0.6
lifecycle: draft
lifecycle_changed: 2026-10-17
tier: supporting
created: 2026-10-17T00:00:00Z
updated: 2026-10-17T00:00:00Z
---
# facet task

작업 유형. LMArena 카테고리 이름을 기본 어휘로 쓰고, Arena에 없는 에이전트 작업 유형은 The Model Gap 벤치마크로 채운다.

`detect`: `rule:*`는 라우터가 결정적으로 판정(0 토큰), `self`는 Orchestrator가 task JSON `facets`에 직접 태그. `evidence`: official(1차 출처 원문) | dataset(데이터셋 카드) | name_only(이름 외 정의 미확인).

## Index

```toml
[[facet]]
id = "general"
desc = "범용 대화·질의 전반"
detect = "rule:always"
evidence = "official"

[[facet]]
id = "coding"
desc = "코드 이해·생성·디버깅"
detect = "rule:code_block_or_code_ext"
arena_rule = "휴리스틱: 코드 블록, 언어 이름·키워드, 코드 명령"
evidence = "official"

[[facet]]
id = "math"
desc = "수학적 추론·문제 풀이를 실제로 요구"
detect = "self"
evidence = "official"

[[facet]]
id = "creative_writing"
desc = "독창적·상상력·정서적 울림이 있는 글쓰기"
detect = "self"
arena_rule = "LLM 분류기 + 체크리스트"
evidence = "official"

[[facet]]
id = "instruction_following"
desc = "주어진 지시를 정확히 따르기"
detect = "self"
evidence = "official"

[[facet]]
id = "webdev_html"
desc = "단일 문서 범위의 독립 HTML/CSS/JS 생성"
detect = "rule:ext(.html,.css)"
evidence = "official"

[[facet]]
id = "webdev_react"
desc = "컴포넌트 구조·라우팅을 포함한 다중 파일 React 앱 생성"
detect = "rule:ext(.jsx,.tsx)"
evidence = "official"

[[facet]]
id = "image_to_webdev"
desc = "이미지(시안·스크린샷)를 웹 페이지로 구현"
detect = "self"
evidence = "official"

[[facet]]
id = "document"
desc = "사용자가 올린 PDF에 대한 문서 추론"
detect = "rule:ext(.pdf)"
evidence = "official"

[[facet]]
id = "search"
desc = "웹 검색이 필요한 질의"
detect = "self"
evidence = "official"

[[facet]]
id = "vision"
desc = "이미지 입력 질의 (설명·개체 인식·유머 등 하위 카테고리 포함)"
detect = "rule:ext(.png,.jpg,.jpeg,.webp)"
evidence = "official"

[[facet]]
id = "vision_ocr"
desc = "이미지 속 텍스트에서 정보를 묻는 질의"
detect = "self"
evidence = "official"

[[facet]]
id = "vision_diagram"
desc = "그래프·차트·도표의 기술 정보 인식·이해"
detect = "self"
evidence = "official"

[[facet]]
id = "vision_homework"
desc = "과제 사진을 보고 문제 이해·풀이"
detect = "self"
evidence = "official"

[[facet]]
id = "repo_coding"
desc = "기존 저장소의 이슈를 읽고 코드 패치로 해결"
detect = "self"
evidence = "official"

[[facet]]
id = "terminal_ops"
desc = "셸에서 빌드·설치·디버깅·운영 등 다단계 터미널 작업"
detect = "rule:kw(bash,shell,CI,docker,빌드)"
evidence = "official"

[[facet]]
id = "multi_tool"
desc = "여러 실제 소프트웨어 도구를 오가는 긴 작업"
detect = "self"
evidence = "official"

[[facet]]
id = "computer_use"
desc = "데스크톱 GUI 앱을 조작하는 긴 워크플로"
detect = "self"
evidence = "official"

[[facet]]
id = "data_analysis"
desc = "스프레드시트·문서 폴더에서 정량 질문에 답하기"
detect = "rule:ext(.csv,.xlsx,.ipynb)"
evidence = "official"

[[facet]]
id = "professional_work"
desc = "영상 편집·CAD 등 전문 업무를 끝까지 수행"
detect = "self"
evidence = "official"

[[facet]]
id = "science_reasoning"
desc = "전문가 수준 과학·학술 질문"
detect = "self"
evidence = "official"

[[facet]]
id = "abstract_reasoning"
desc = "예시 몇 개에서 숨은 규칙을 추론해 적용"
detect = "self"
evidence = "official"

[[facet]]
id = "legal"
desc = "법률 추론·계약 검토·협상"
detect = "self"
evidence = "dataset"

[[facet]]
id = "gui_grounding"
desc = "고해상도 전문 소프트웨어 화면에서 UI 요소 위치 찾기"
detect = "self"
evidence = "dataset"

[[facet]]
id = "retrieval"
desc = "추론이 필요한 문서 검색"
detect = "self"
evidence = "dataset"

[[facet]]
id = "ocr_parse"
desc = "PDF·스캔·사진 문서를 구조화된 텍스트·JSON으로 변환"
detect = "rule:ext(.pdf)"
evidence = "dataset"
```

## Sources

- [[references/sources/arena-category]] — <https://arena.ai/blog/arena-category/>
- [[references/sources/arena-leaderboard-changelog]] — <https://arena.ai/blog/leaderboard-changelog>
- [[references/sources/arena-vision-categories]] — <https://arena.ai/blog/re-introducing-vision-arena-categories/>
- [[references/sources/themodelgap-data]] — <https://themodelgap.com/data/benchmarks.json>
- [[references/sources/hf-official-benchmarks]] — <https://huggingface.co/api/datasets?filter=benchmark:official>
