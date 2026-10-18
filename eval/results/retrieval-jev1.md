# 태깅·토큰 채점 · jev1 · labeled case 60

| tagger | th | P | R | F1 | 환각률 | 누락률 | exact | Jaccard(반복) | in tok | out tok | 추정/실측 in | 토큰/F1점 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rule-only | - | 0.983 | 0.435 | 0.532 | 0.017 | 0.565 | 8/60 | 1 | 0 | 0 | - | 0 |
| llm_all | 0.3 | 0.448 | 0.992 | 0.601 | 0.552 | 0.008 | 3/180 | 0.964 | 2359 | 963 | 1.00 | 55.2 |
| llm_all | 0.4 | 0.505 | 0.975 | 0.648 | 0.495 | 0.025 | 6/180 | 0.984 | 2359 | 963 | 1.00 | 51.2 |
| llm_all | 0.5 | 0.542 | 0.964 | 0.679 | 0.458 | 0.036 | 6/180 | 0.978 | 2359 | 963 | 1.00 | 48.9 |
| llm_all | 0.6 | 0.595 | 0.953 | 0.717 | 0.405 | 0.047 | 11/180 | 0.974 | 2359 | 963 | 1.00 | 46.3 |
| llm_all | 0.7 | 0.648 | 0.933 | 0.751 | 0.352 | 0.067 | 16/180 | 0.986 | 2359 | 963 | 1.00 | 44.2 |
| llm_all | 0.8 | 0.691 | 0.914 | 0.774 | 0.309 | 0.086 | 21/180 | 0.985 | 2359 | 963 | 1.00 | 42.9 |
| rule_llm | 0.3 | 0.446 | 0.992 | 0.600 | 0.554 | 0.008 | 2/180 | 0.961 | 2318 | 944 | 1.00 | 54.4 |
| rule_llm | 0.4 | 0.505 | 0.978 | 0.650 | 0.495 | 0.022 | 6/180 | 0.970 | 2318 | 944 | 1.00 | 50.2 |
| rule_llm | 0.5 | 0.539 | 0.966 | 0.677 | 0.461 | 0.034 | 6/180 | 0.975 | 2318 | 944 | 1.00 | 48.1 |
| rule_llm | 0.6 | 0.596 | 0.958 | 0.720 | 0.404 | 0.042 | 11/180 | 0.965 | 2318 | 944 | 1.00 | 45.3 |
| rule_llm | 0.7 | 0.645 | 0.940 | 0.752 | 0.355 | 0.060 | 15/180 | 0.983 | 2318 | 944 | 1.00 | 43.4 |
| rule_llm | 0.8 | 0.691 | 0.932 | 0.783 | 0.309 | 0.068 | 21/180 | 0.989 | 2318 | 944 | 1.00 | 41.7 |
| rule_llm_axis | 0.3 | 0.444 | 0.992 | 0.599 | 0.556 | 0.008 | 3/180 | 0.955 | 3927 | 964 | 0.65 | 81.7 |
| rule_llm_axis | 0.4 | 0.504 | 0.975 | 0.649 | 0.496 | 0.025 | 6/180 | 0.983 | 3927 | 964 | 0.65 | 75.3 |
| rule_llm_axis | 0.5 | 0.541 | 0.968 | 0.679 | 0.459 | 0.032 | 6/180 | 0.967 | 3927 | 964 | 0.65 | 72.0 |
| rule_llm_axis | 0.6 | 0.594 | 0.953 | 0.717 | 0.406 | 0.047 | 11/180 | 0.965 | 3927 | 964 | 0.65 | 68.2 |
| rule_llm_axis | 0.7 | 0.644 | 0.940 | 0.751 | 0.356 | 0.060 | 16/180 | 0.984 | 3927 | 964 | 0.65 | 65.1 |
| rule_llm_axis | 0.8 | 0.694 | 0.932 | 0.784 | 0.306 | 0.068 | 21/180 | 0.979 | 3927 | 964 | 0.65 | 62.4 |
| rule_llm_v2 | 0.3 | 0.533 | 0.986 | 0.670 | 0.467 | 0.014 | 9/180 | 0.955 | 2353 | 884 | 1.01 | 48.3 |
| rule_llm_v2 | 0.4 | 0.627 | 0.967 | 0.733 | 0.373 | 0.033 | 24/180 | 0.972 | 2353 | 884 | 1.01 | 44.2 |
| rule_llm_v2 | 0.5 | 0.682 | 0.965 | 0.775 | 0.318 | 0.035 | 35/180 | 0.975 | 2353 | 884 | 1.01 | 41.8 |
| rule_llm_v2 | 0.6 | 0.742 | 0.947 | 0.809 | 0.258 | 0.053 | 50/180 | 0.962 | 2353 | 884 | 1.01 | 40.0 |
| rule_llm_v2 | 0.7 | 0.812 | 0.932 | 0.843 | 0.188 | 0.068 | 73/180 | 0.988 | 2353 | 884 | 1.01 | 38.4 |
| rule_llm_v2 | 0.8 | 0.882 | 0.924 | 0.885 | 0.118 | 0.076 | 110/180 | 0.981 | 2353 | 884 | 1.01 | 36.6 |

rule_llm_v2 축별 오류 수(th 0.8): domain 40, lang 3, shape 1, task 70

| max_units | table 토큰(추정) | JSON 토큰(추정) | nDCG@k(gold 태그) | nDCG 1점당 table 토큰 |
|---:|---:|---:|---:|---:|
| 6 | 436 | 626 | 0.880 | 496 |
| 12 | 506 | 750 | 0.863 | 586 |
| 24 | 506 | 750 | 0.863 | 586 |

최종 결정: pred/gold evidence 일치 171/180 · pred abstain 153 · 호출당 토큰 1231
한쪽 이상이 프로필을 고른 경우 33: 일치 24 · ws-units(abstain/claude-default), ws-units(abstain/claude-default), ws-units(abstain/claude-default), ws-logs(abstain/claude-default), ws-logs(abstain/claude-default), ws-logs(abstain/claude-default), hard_long(claude-default/abstain), hard_long(claude-default/abstain), hard_long(claude-default/abstain)

## 역검색: unit 설명만으로 태깅 (active unit 53, th 0.8, agent_signal 등 always·lang 제외)

| 기준 | P | R | F1 |
|---|---:|---:|---:|
| 현행 unit.facets | 0.810 | 0.698 | 0.643 |
| unit_gold | 0.810 | 0.717 | 0.643 |
| task 축만(현행) | 0.959 | 0.811 | 0.783 |

설명에서 복원되지 않은 facet(설명 보강 후보, 호출당 입력 2346 토큰):
- arena:agent_bash_reliability/overall: task:terminal_ops
- arena:agent_steerability/overall: agent_signal:steerability
- arena:search_factuality/overall: task:search
- arena:search_style_control/overall: task:search
- arena:text_style_control/coding: task:coding
- arena:text_style_control/creative_writing: task:creative_writing
- arena:text_style_control/expert: difficulty:expert
- arena:text_style_control/hard_prompts_english: difficulty:hard_prompts
- arena:text_style_control/hard_prompts: difficulty:hard_prompts
- arena:text_style_control/industry_mathematical: domain:mathematical
- arena:text_style_control/industry_software_and_it_services: domain:software_it
- arena:text_style_control/instruction_following: task:instruction_following
- arena:text_style_control/math: task:math
- arena:vision_style_control/ocr: task:vision_ocr
- arena:webdev/overall: task:webdev_html, task:webdev_react
- mg:hle/no_tools: task:science_reasoning
