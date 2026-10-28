---
title: "Model selection | OpenAI API"
site: "OpenAI Developers"
source: "https://developers.openai.com/api/docs/guides/model-selection"
domain: "developers.openai.com"
language: "en"
description: "Find the right model for your use case"
word_count: 689
---

## Meet the models

Availability, tools, reasoning settings, and usage limits differ by product and model version. Check the [models available in ChatGPT](https://developers.openai.com/codex/models) or the [API model catalog](https://developers.openai.com/api/docs/models).

## Find the right model for your workflow

Choose your work and task and get a recommendation.

What type of task are you doing?Make small edits to existing files

### When to consider GPT-6.1 Terra

Try [GPT-6.1 Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra) for concise writing based on supplied material, computer-use tasks with a defined outcome, and scoped code fixes. Provide clear inputs, requirements, and a way to verify the result, such as checking saved records or running regression tests.

Compare it with GPT-6.1 Sol on the same inputs and reasoning effort. For writing, judge audience fit, voice, and useful detail as well as accuracy and length. For computer use, check the saved result and the accuracy of the completion report.

### When to consider GPT-6.1 Sol

Consider GPT-6.1 Sol for complex projects where cost matters, such as creating a board presentation from financial results or building a website from a product brief. Compare it with Astra on the same task to assess the tradeoff between quality and cost.

See the [API model page](https://developers.openai.com/api/docs/models/gpt-6.1-sol) for specifications and API pricing, or [Codex and ChatGPT Work availability](https://developers.openai.com/codex/models#gpt-6.1-sol) for access through your ChatGPT plan.

## How to think about models and reasoning effort

Luna is the most cost-efficient model, while Astra is our state-of-the-art, most powerful model. If cost and latency aren’t a concern, you can default to Astra. To reduce costs or latency, use the guidance below to choose a model and reasoning effort for your needs.

Luna is our most efficient model, while Astra is our state-of-the-art, most powerful model. If you don’t need to think about usage or how long it takes to complete a task, you can default to Astra. To optimize usage, use the guidance below to choose a model and reasoning effort for your needs.

Model and reasoning effort

1. Luna · Low
	Fine-grained edits, well-scoped problem-solving, and simple data extraction.
2. Luna · Extra high
	Finding current context across multiple apps, prioritizing work, and solving problems with clear constraints.
3. GPT-6.1 Sol · Medium
	Complex technical work and coordinated deliverables you expect to revise.
4. GPT-6.1 Sol · Extra high
	Polished deliverables, connected visual systems, and decisions built from conflicting evidence.
5. Astra · Low
	Concise writing and content adaptation that preserve facts and nuance.
6. Astra · Medium
	Ambitious projects that need broad context, reliable interactions, and complete results.
7. Astra · Extra high
	Demanding analysis and complex deliverables with exacting requirements.

Model strengths

<svg viewBox="0 0 440 380" role="img" aria-label="Abstract comparison of reviewed Insights category scores and AutomationBench completion. Small gaps in category scores are enlarged; computer use shows completion relative to the leading result. Distances across axes are not comparable benchmark scores. Available task samples and reported reasoning settings differ. The shapes preserve each source ordering and ties without numeric labels."><path fill="none" d="M215.66987298107782,151.9 Q220,149.4 224.33012701892218,151.9 L250.83050437472602,167.2 Q255.1606313936482,169.7 255.1606313936482,174.7 L255.1606313936482,205.29999999999998 Q255.1606313936482,210.29999999999998 250.83050437472602,212.79999999999998 L224.33012701892218,228.1 Q220,230.6 215.66987298107782,228.1 L189.16949562527398,212.8 Q184.8393686063518,210.3 184.8393686063518,205.3 L184.8393686063518,174.7 Q184.8393686063518,169.7 189.16949562527398,167.2 Z"></path><path fill="none" d="M215.66987298107782,117.1 Q220,114.6 224.33012701892218,117.1 L280.9681884264245,149.8 Q285.2983154453467,152.3 285.2983154453467,157.3 L285.2983154453467,222.7 Q285.2983154453467,227.7 280.9681884264245,230.2 L224.33012701892218,262.9 Q220,265.4 215.66987298107782,262.9 L159.03181157357554,230.20000000000005 Q154.70168455465335,227.70000000000005 154.70168455465335,222.70000000000005 L154.70168455465333,157.29999999999998 Q154.70168455465333,152.29999999999998 159.0318115735755,149.79999999999998 Z"></path><path fill="none" d="M215.66987298107782,76.5 Q220,74 224.33012701892218,76.5 L316.12881982007264,129.5 Q320.45894683899485,132 320.45894683899485,137 L320.4589468389949,242.99999999999997 Q320.4589468389949,247.99999999999997 316.1288198200727,250.49999999999997 L224.33012701892218,303.5 Q220,306 215.66987298107782,303.5 L123.87118017992734,250.50000000000003 Q119.54105316100514,248.00000000000003 119.54105316100514,243.00000000000003 L119.54105316100512,137 Q119.54105316100512,132 123.87118017992732,129.5 Z"></path><line stroke-opacity="0.2" stroke="currentColor" x1="220" y1="190" x2="220" y2="74"></line><line stroke-opacity="0.2" stroke="currentColor" x1="220" y1="190" x2="320.45894683899485" y2="132"></line><line stroke-opacity="0.2" stroke="currentColor" x1="220" y1="190" x2="320.4589468389949" y2="247.99999999999997"></line><line stroke-opacity="0.2" stroke="currentColor" x1="220" y1="190" x2="220" y2="306"></line><line stroke-opacity="0.2" stroke="currentColor" x1="220" y1="190" x2="119.54105316100514" y2="248.00000000000003"></line><line stroke-opacity="0.2" stroke="currentColor" x1="220" y1="190" x2="119.54105316100512" y2="132"></line><text fill="currentColor" x="220" y="32" text-anchor="middle"><tspan x="220" dy="0">3D and </tspan><tspan x="220" dy="16">design </tspan></text><text fill="currentColor" x="356.8320137979413" y="111" text-anchor="middle"><tspan x="356.8320137979413" dy="0">Software </tspan></text><text fill="currentColor" x="356.83201379794133" y="269" text-anchor="middle"><tspan x="356.83201379794133" dy="0">Data and </tspan><tspan x="356.83201379794133" dy="16">analysis </tspan></text><text fill="currentColor" x="220" y="348" text-anchor="middle"><tspan x="220" dy="0">Documents </tspan><tspan x="220" dy="16">and slides </tspan></text><text fill="currentColor" x="83.16798620205873" y="269.00000000000006" text-anchor="middle"><tspan x="83.16798620205873" dy="0">Computer </tspan><tspan x="83.16798620205873" dy="16">use </tspan></text><text fill="currentColor" x="83.1679862020587" y="110.99999999999999" text-anchor="middle"><tspan x="83.1679862020587" dy="0">Research and </tspan><tspan x="83.1679862020587" dy="16">planning</tspan></text></svg>

### Experiment

Treat the guidance on this page as a starting point. The best way to find the right model for your workflow is to experiment with different models and reasoning settings to see what works.

Start by considering:

- **How often does your workflow run?** A frequent automation makes usage and cost add up faster than an occasional project.
- **How quickly do you need the result?** A task you’re waiting on may need a faster setting than one that runs overnight.
- **How will you use the output?** A draft for your review may need less polish than something you’ll share externally.
- **How important is the quality of the result?** Depending on your use case or industry, you might want to use a stronger model to put an emphasis on quality.

If you can, experiment using the same inputs to compare results and keep the lightest setting that meets your quality bar.

Choose acceptance criteria before comparing models:

- **Writing:** check required facts, qualifications, audience, and voice. Review both outputs before deciding whether the shorter one is more useful.
- **Computer use:** reopen the affected record or page to verify saved changes, confirm that the workflow preserved unrelated data, and compare the completion report with the actual result.
- **Code and interfaces:** run regression tests. For an interactive application, also inspect the rendered result on desktop and mobile.

Repeat the comparison across representative tasks. Measure completion time alongside quality, including time spent reviewing or repairing the result. Then vary reasoning effort while keeping the model and inputs fixed.