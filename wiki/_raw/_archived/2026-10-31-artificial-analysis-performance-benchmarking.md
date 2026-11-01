---
title: "Language Model API Performance Benchmarking"
site: "Artificial Analysis"
source: "https://artificialanalysis.ai/methodology/performance-benchmarking"
domain: "artificialanalysis.ai"
language: "en"
description: "Detailed performance benchmarking methodology for LLM inference services."
word_count: 1868
---

## Artificial Analysis Language Model API Performance Benchmarking Methodology

## Overview

Measuring LLM performance requires sending the LLM a prompt and measuring the characteristics of its output. We measure performance across several test workloads.

### Workload Types

| Workload type | Description |
| --- | --- |
| 1k input token | Approximately 1,000 input tokens, at least 1,000 answer tokens |
| 10k input token | Approximately 10,000 input tokens, at least 1,500 answer tokens (default benchmark on our website) |
| 100k input token | Approximately 100,000 input tokens, at least 2,000 answer tokens |
| Vision workload | A single 1 megapixel image and approximately 1,000 input tokens, 1,000 output tokens |

Longer prompts can result in both longer time to first token and slower output tokens per second compared to shorter prompts.

### Load Scenarios

| Load scenario | Description |
| --- | --- |
| Single prompt | One prompt is sent to the model's API at a time |
| Parallel prompts | 10 prompts are sent to the model's API simultaneously |

### Testing Frequency

- We test our 1k, 10k input token and vision workloads 8 times per day, approximately every 3 hours
- For our multiple or parallel workload test, we send 10 concurrent requests of our standard 1k input token workload once per day at a random time
- We test our 100k input token workload once per week
- We measure cache hit rates for each endpoint approximately every 18 hours, and update each endpoint's representative cache hit rate monthly from the median of the past four weeks of measurements

### Prompt Generation

Every test run uses a unique prompt that we generate at the time of the test and run on all endpoints we cover. Prompts combine a range of long-form input content (e.g., articles) with tasks including explanation/summarization, question and answer generation, comparative analysis, translation, or visual artifact generation.

We set the parameters of the generation process to fill the target token budget, producing diverse outputs that test different reasoning and generation capabilities.

Prompt diversity matters for performance benchmarking because techniques like speculative decoding mean that output speeds vary with the type of output.

### Measurement Representation

We represent performance measurements as the median (P50) over the past 72 hours to reflect sustained changes in performance that users can expect when using the API. The exception is the 100k input token workload, which we test once per week and represent as the median (P50) over the past 14 days.

## Key Definitions

- **Time to First Token:** The time in seconds between sending a request to the service or system and receiving the first token of the response. For reasoning models which return reasoning tokens, this will be the first reasoning token.
- **Time to First Answer Token:** The time in seconds between sending a request to the service or system and receiving the first answer token of the response. For reasoning models, this is measured after any 'thinking' time.
- **Output Speed (output tokens per second):** The average number of tokens received per second, after the first token is received.
- **Total Response Time for 100 Output Tokens:** The number of seconds to generate 100 output tokens, calculated synthetically based on TTFT and Output Speed to assure maximum comparison utility.
- **End-to-End Response Time:** The total time to receive a complete response, including input processing time, model reasoning time, and answer generation time.
- **Cache Hit Rate:** The share of cacheable input tokens served from the provider's prompt cache, as reported by the provider's API during multi-turn agentic coding sessions. We report a representative cache hit rate for each endpoint based on its recent measurements.
- **Average Reasoning Tokens:** Time reasoning models spend outputting 'reasoning' tokens before providing an answer. This is calculated based on the average number of 'reasoning' tokens across a diverse set of 60 prompts. Where the average number of reasoning tokens is not available or has not yet been calculated, we assume 2k reasoning tokens. These prompts are of varied lengths and include coverage of a range of topics including, personal-related queries, commercial-related queries, coding, math, science and others. Prompts are a combination of being written by Artificial Analysis and others sourced from the following evaluations: MMLU Pro, AIME 2025, and LiveCodeBench. These prompts can be accessed [here](https://artificialanalysis.ai/downloads/methodology/performance-prompts.xlsx).

## Technical Details

**Server Location:** Our primary testing server is a virtual machine hosted in Google Cloud's `us-central1-a` zone.

**Test Accounts:** We run tests using a combination of anonymous accounts, accounts with credits, and API keys provided explicitly for benchmarking. Where our primary benchmarking does not use an anonymous account, we register a separate anonymous account and validate that performance is not being manipulated.

**API Libraries:** For all providers claiming compatibility with OpenAI's API, we use the official OpenAI Python library to ensure consistency across tests. For providers without OpenAI compatibility, we use their recommended client libraries.

**Cache Hit Rate Measurement:** We run multi-turn coding agent tasks against each endpoint to capture a representative agentic trajectory, in which each turn re-sends the growing conversation so the provider can reuse cached input. We only record a measurement when the session completes and processes enough cacheable input to be meaningful.

**API Parameters:** We use the following API parameters for all tests:

- `temperature: 0.6` for reasoning models; `temperature: 0` for non-reasoning models unless specified otherwise by the model creator.
- `top_p: 1`

**Token Measurement:** We have two methods for measuring tokens:

- For performance benchmarking, we measure tokens as counted by OpenAI's tiktoken library (`o200k_base`). This standardizes the number of tokens counted across different models (with different tokenizers) so that the same text is represented as the same number of tokens.
- For the Artificial Analysis Intelligence Index evaluations, we instead use the token counts reported by each model's API provider (including cached input, reasoning, and output tokens), which let us more accurately report the cost of running the Intelligence Index. When reporting cache hit rates and cost, we combine these with live measurements of each model's typical cache hit rate, rather than relying on the one-off measurement when the evaluation was run.

**Output Speed Calculation:** For reasoning models that do not expose all reasoning tokens in the response, we calculate output speed using the last 80% of answer chunks. This keeps measured output speeds consistent and closer to the user experience.

## Known Limitations

**Tokenizer Efficiency and Pricing:** Different models use different tokenizers, so the same text can require different numbers of tokens. This means that pricing is not always directly comparable across models. We are working on publishing more details on tokenizer efficiency and its impact on pricing. In the meantime, we have shared some preliminary tokenizer efficiency adjusted pricing analysis on Twitter.

**Quantization:** Some models use quantization to reduce computational requirements and increase speed. However, quantization can also affect model quality. We are moving towards full disclosure of quantization methods used by the models we benchmark.

**Server Location and TTFT:** Time-to-first-token (TTFT) is sensitive to server location as it includes network latency. Our primary testing server is located in Google Cloud's us-central1-a zone, which may advantage or disadvantage certain providers based on their server locations. We are considering additional testing locations to mitigate this effect.

## Version History

**Version 2.2.0**

2 March 2026

- Updated prompts: We introduced a new set of prompts with broader, more varied content and a wider range of task types. Prompt diversity matters because techniques like speculative decoding mean that output speeds vary with the type of output.
- Default workload change: Default speed on our site now reflects results from 10k input token prompts (previously 1k) and we have deprecated performance measurements for 100 token input workloads. All 1k, 10k and 100k input token workloads are still visible on all pages by selecting the Prompt Options drop-down. The easiest way to compare output speeds for different workload shapes is using the Output Speed by Input Token Count chart.

## Integrity Terms

### Background

Artificial Analysis is an independent AI benchmarking and insights provider. Our benchmarks are consulted by millions of users and organizations.

We strive to ensure that all data published on Artificial Analysis is fair, transparent, and representative of the typical experience of developers and organizations using the models and endpoints we cover. Our inference benchmarking data is widely used as a reference standard for comparing inference providers across dimensions such as speed, latency, and quality. The value of these measurements depends on them reflecting the experience of an ordinary developer using a provider's standard, publicly available endpoint.

These terms formalize the approach Artificial Analysis has taken since we began benchmarking inference performance. They apply equally to all inference providers and platforms (together, "providers") that publish serverless endpoint data on Artificial Analysis, and they ensure every provider is measured on the same fair basis.

### Provider Requirements

Traffic from Artificial Analysis must be served on the same publicly available configuration that any ordinary developer would receive when using the endpoint. In particular, providers must not:

- Detect, fingerprint, or otherwise identify Artificial Analysis traffic (whether by account, API key, IP address, request headers, payloads, or traffic patterns) and serve it differently from ordinary traffic.
- Route Artificial Analysis traffic to dedicated, reserved, or non-public resources, including separate hardware, capacity pools, priority queues, or geographic regions that are not generally available.
- Serve Artificial Analysis a model, quantization, context length, or endpoint configuration that differs from what is publicly advertised and generally available under the same name.
- Serve Artificial Analysis traffic at a batch size, concurrency, or load configuration that is not representative of what ordinary traffic on the same endpoint receives (for example, running benchmark requests at reduced batch sizes to increase per-request speed).

On request, providers must confirm the model version, precision or quantization, and context length serving Artificial Analysis traffic, and confirm that this matches the standard public offering. Providers must ensure that every employee, contractor, advisor, or affiliate who is aware that an endpoint is being measured by Artificial Analysis complies with this policy.

Performance features that are part of the standard public offering and available to all developers on equivalent terms (for example, autoscaling, generally available caching, or published tiering that any customer can access) are not a violation, provided they are not applied selectively to Artificial Analysis traffic.

### Compliance Process

Artificial Analysis lists endpoints and providers at its sole discretion. We reserve the right to delist any endpoint or provider that does not comply with these terms, and to decline, withhold, or remove any listing for any reason.

We conduct frequent consistency checks on every endpoint we measure. As standard practice, we measure from our primary Artificial Analysis account alongside independent test accounts, each created and used in the same way an ordinary developer would. Where these return materially different results on identical payloads and the same endpoint, we investigate before drawing conclusions.

If we detect or reasonably suspect that Artificial Analysis traffic is being served differently from the standard public offering, we may:

- Withhold, remove, or delay publication of affected measurements.
- Re-measure on a standard, publicly created account and publish those results.
- Remove the endpoint or provider from performance leaderboards and listings.
- Suspend the provider across all leaderboards.
- Publicly disclose that a provider has served non-representative performance to Artificial Analysis.

By submitting endpoints to Artificial Analysis, providers acknowledge these terms and our shared commitment to maintaining benchmark integrity. Artificial Analysis may update this policy at any time.

We appreciate your cooperation. If you have questions or concerns, please contact our team.