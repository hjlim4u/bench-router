/** Public A2A workflow probe with stock gateway code and scripted workers; no agent is launched.
 * Run after npm ci/build in an unmodified herdr-a2a checkout:
 * node eval/herdr_a2a_collaboration.mjs /absolute/path/to/herdr-a2a
 */
import assert from "node:assert/strict";
import { randomUUID, createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";

const root = resolve(process.argv[2] ?? ".bench-router/herdr-a2a-patch-check");
const load = (file) => import(pathToFileURL(join(root, "dist", file)).href);
const require = createRequire(join(root, "package.json"));
const { Role, TaskState } = require("@a2a-js/sdk");
const { A2AGateway } = await load("a2a/server.js");
const { defaultAgentClientFactory } = await load("bridge/client.js");
const { run: runBridge } = await load("bridge/cli.js");
const { textPart } = await load("a2a/task-mapper.js");
const { HerdrDelegationService } = await load("core/delegation-service.js");
const { DelegatedTaskService } = await load("core/task-service.js");
const { DefaultSpawnManager } = await load("spawn/spawn-manager.js");
const { DefaultReusePolicy } = await load("spawn/reuse-policy.js");
const { defaultRuntimeAdapter } = await load("runtimes/default-adapter.js");
const { buildDefaultConfig } = await load("config/schema.js");

const taskRows = new Map(), instances = new Map(), panes = new Map(), delivered = new Map();
const scriptedOutcomes = new Map();
const tasks = {
  get: async (id) => taskRows.get(id),
  create: async (task) => { assert(!taskRows.has(task.id)); taskRows.set(task.id, task); return task; },
  update: async (id, patch) => { const task = { ...taskRows.get(id), ...patch }; taskRows.set(id, task); return task; },
  listByInstance: async (id) => [...taskRows.values()].filter((t) => t.liveInstanceId === id),
  listByContext: async (id) => [...taskRows.values()].filter((t) => t.contextId === id),
  listActive: async () => [...taskRows.values()].filter((t) => !["completed", "failed", "canceled", "rejected"].includes(t.state)),
};
const liveAgents = {
  get: async (id) => instances.get(id),
  put: async (agent) => instances.set(agent.instanceId, agent),
  all: async () => [...instances.values()],
  byLogicalTarget: async (name) => [...instances.values()].filter((a) => a.logicalTarget === name),
  delete: async (id) => instances.delete(id),
};
let sequence = 0;
const ids = { taskId: randomUUID, messageId: randomUUID, instanceId: randomUUID,
  shortId: () => (++sequence).toString(16).padStart(4, "0") };
const clock = { now: () => new Date(), nowIso: () => new Date().toISOString(), sleep: async () => {} };
const logger = { log() {}, child() { return this; } };
const events = { emit() {} };
const adapters = { for: () => defaultRuntimeAdapter };
const config = buildDefaultConfig({});
config.gateway.port = 0;
config.relay.settleTimeoutMs = 1000;
config.relay.turnStartTimeoutMs = 1000;
const catalogRows = ["writer", "reviewer"].map((name) => ({
  name, descriptorKind: "custom", runtimeKind: "codex", available: true,
  description: `${name} scripted worker`, profile: { name, runtime: "codex" },
  runtime: { kind: "codex", supportedByHerdr: true, hasDetectionManifest: true,
    hasIntegration: true, launchable: "yes", runningInstances: 0, sources: [] },
}));
const catalog = { get: async (name) => catalogRows.find((r) => r.name === name),
  list: async () => catalogRows, refresh: async () => {} };
const herdr = {
  agentGet: async (target) => {
    const pane = [...panes.values()].find((p) => p.pane_id === target || p.name === target);
    assert(pane, `missing scripted worker: ${target}`);
    return { ...pane };
  },
  paneProcessInfo: async () => ({ shell_pid: 1, foreground_process_group_id: 1 }),
  agentStart: async ({ name, kind, paneId, args = [] }) => {
    Object.assign(panes.get(paneId), { name, agent: kind, interactive_ready: true,
      launch_pending: false, agent_session: { source: "probe", agent: kind, kind: "id", value: randomUUID() } });
    return { agent: { ...panes.get(paneId) }, argv: args };
  },
};
const layout = {
  allocateHeadlessPane: async ({ cwd }) => {
    const pane = { pane_id: randomUUID(), terminal_id: randomUUID(), workspace_id: "probe", tab_id: "probe:t1",
      agent_status: "idle", revision: 1, focused: false, cwd };
    panes.set(pane.pane_id, pane);
    return pane;
  },
  releasePane: async (id) => panes.delete(id),
};
const reuse = new DefaultReusePolicy({ herdr, logger,
  hasActiveTask: async (id) => (await tasks.listByInstance(id)).some((t) => ["submitted", "working"].includes(t.state)) });
const spawn = new DefaultSpawnManager({ herdr, layout, reuse, liveAgents, adapters, ids, clock,
  events, logger, preflight: { run: async () => ({ ok: true, checks: [] }) }, config: { recovery: config.recovery } });
const taskService = new DelegatedTaskService({ tasks, liveAgents, herdr, adapters, clock, events, logger });
const relay = {
  enqueue: async (message) => {
    delivered.set(message.taskId, message.body);
    const live = instances.get(message.targetInstanceId);
    panes.get(live.paneId).agent_status = "working";
    // Scripted runtime boundary: this verifies protocol/selection, not model quality or real delivery.
    setTimeout(async () => {
      await taskService.transition(message.taskId, "working");
      panes.get(live.paneId).agent_status = "idle";
      const outcome = scriptedOutcomes.get(message.body) ?? "completed";
      await taskService.transition(message.taskId, outcome, outcome === "completed"
        ? { question: undefined, result: { text: `scripted ${live.logicalTarget} output`, source: "adapter" } }
        : outcome === "input-required" ? { question: "Which compatibility target?" }
        : { error: { code: "RESULT_UNAVAILABLE", message: "scripted extraction failure", retryable: false } });
    }, 25);
    return { messageId: message.id, state: "QUEUED", queuePosition: 1 };
  },
};
const delegation = new HerdrDelegationService({ catalog, spawn, relay, queue: {}, tasks, taskService,
  liveAgents, adapters, herdr, config, ids, clock, events, logger,
  resolveCaller: () => ({ role: "peer-agent", name: "workflow-probe" }), callerContext: () => ({ cwd: process.cwd() }) });
const gateway = new A2AGateway({ catalog, delegation, taskService, tasks, config, logger });
const trace = [];
try {
  const { baseUrl } = await gateway.listen();
  const clients = Object.fromEntries(await Promise.all(["writer", "reviewer"].map(async (name) =>
    [name, await defaultAgentClientFactory(`${baseUrl}/a2a/agents/${name}`, fetch)])));
  async function send(name, text, contextId = "", references = [], taskId = "", outcome = "completed") {
    scriptedOutcomes.set(text, outcome);
    let id;
    const eventKinds = [];
    const request = { tenant: "", message: {
      messageId: randomUUID(), contextId, taskId, role: Role.ROLE_USER, parts: [textPart(text)],
      metadata: { "urn:herdr:execution-options:v1": { visibility: "headless" } },
      extensions: [], referenceTaskIds: references,
    }, metadata: undefined, configuration: undefined };
    for await (const event of clients[name].sendMessageStream(request, { signal: AbortSignal.timeout(5000) })) {
      eventKinds.push(event.payload?.$case);
      if (event.payload?.$case === "task") id = event.payload.value.id;
    }
    assert(id, "standard A2A stream must expose a task id");
    const task = await clients[name].getTask({ tenant: "", id }, { signal: AbortSignal.timeout(5000) });
    assert.equal(task.status.state, {
      completed: TaskState.TASK_STATE_COMPLETED,
      "input-required": TaskState.TASK_STATE_INPUT_REQUIRED,
      failed: TaskState.TASK_STATE_FAILED,
    }[outcome]);
    assert(eventKinds.includes("statusUpdate"));
    if (outcome === "completed") assert(eventKinds.includes("artifactUpdate"));
    trace.push({ role: name, task_id: task.id, context_id: task.contextId,
      instance: task.metadata.instance, events: eventKinds });
    return task;
  }
  const draft = await send("writer", "Write the initial draft.");
  const review = await send("reviewer", JSON.stringify({ review: draft.artifacts }), "", [draft.id]);
  const revision = await send("writer", JSON.stringify({ revise: review.artifacts }), draft.contextId, [draft.id, review.id]);
  assert.equal(revision.contextId, draft.contextId);
  assert.notEqual(revision.id, draft.id);
  assert.equal(revision.metadata.instance, draft.metadata.instance);

  const oldWriter = instances.get(draft.metadata.instance);
  panes.get(oldWriter.paneId).agent_status = "working"; // original writer temporarily occupied
  const unrelated = await send("writer", "Independent work in another conversation.");
  panes.get(oldWriter.paneId).agent_status = "idle";
  assert.notEqual(unrelated.metadata.instance, oldWriter.instanceId);
  const followUp = "Revise the original draft using its previous context.";
  const afterContention = await send("writer", followUp,
    draft.contextId, [draft.id, review.id]);
  assert.equal(afterContention.contextId, draft.contextId);
  assert.notEqual(afterContention.metadata.instance, oldWriter.instanceId);
  assert.equal(afterContention.metadata.instance, unrelated.metadata.instance);
  assert.equal(delivered.get(afterContention.id), followUp);

  const examples = JSON.parse(await readFile(new URL("../examples/hybrid-collaboration.json", import.meta.url), "utf8"));
  const input = examples.input;
  const digest = createHash("sha256").update(input.content).digest("hex");
  assert.equal(input.sha256, digest, "example input hash must match exact UTF-8 content");
  for (const pattern of examples.patterns) {
    for (const step of pattern.steps) {
      assert.equal(step.input_sha256, digest);
      assert(["herdr", "a2a"].includes(step.backend));
      for (const dependency of step.depends_on) {
        assert(pattern.steps.findIndex((s) => s.id === dependency) < pattern.steps.indexOf(step));
        assert(pattern.steps.some((s) => s.id === dependency));
      }
    }
  }
  // Explicit content survives worker reassignment; references/context alone do not carry it.
  const packet = JSON.stringify({ ...input, previous_results: [draft.artifacts, review.artifacts],
    acceptance: "Report reproducible findings; do not delegate further." });
  const explicit = await send("writer", packet, draft.contextId, [draft.id, review.id]);
  assert.equal(explicit.metadata.instance, unrelated.metadata.instance);
  assert.equal(delivered.get(explicit.id), packet);
  const [goodReview, failedReview] = await Promise.all([
    send("reviewer", JSON.stringify({ ...input, focus: "correctness" })),
    send("reviewer", JSON.stringify({ ...input, focus: "security" }), "", [], "", "failed"),
  ]);
  assert(goodReview.artifacts.length > 0, "one review failure must not erase the successful result");
  assert.equal(failedReview.status.state, TaskState.TASK_STATE_FAILED);
  const question = await send("reviewer", "Ask for a compatibility target.", "", [], "", "input-required");
  const answered = await send("reviewer", "Target Python 3.11.", question.contextId, [], question.id);
  assert.equal(answered.id, question.id);
  assert.equal(answered.metadata.instance, question.metadata.instance);
  await assert.rejects(() => delegation.continueTask(answered.id, "Continue completed task"));
  const newQuestion = await send("reviewer", JSON.stringify({ ...input, previous_results: answered.artifacts }));
  assert.notEqual(newQuestion.id, answered.id);
  assert.deepEqual([TaskState.TASK_STATE_SUBMITTED, TaskState.TASK_STATE_WORKING, TaskState.TASK_STATE_COMPLETED,
    TaskState.TASK_STATE_FAILED, TaskState.TASK_STATE_CANCELED, TaskState.TASK_STATE_INPUT_REQUIRED,
    TaskState.TASK_STATE_REJECTED, TaskState.TASK_STATE_AUTH_REQUIRED], [1, 2, 3, 4, 5, 6, 7, 8]);
  const cliOutput = [];
  const cliCode = await runBridge(["get", newQuestion.id, "--base-url", baseUrl, "--json"], {
    stdout: (line) => cliOutput.push(line), stderr: (line) => assert.fail(line),
  });
  const cliTask = JSON.parse(cliOutput.join("\n"));
  assert.equal(cliCode, 0);
  assert.equal(cliTask.id, newQuestion.id);
  assert.equal(cliTask.status.state, 3);
  assert.equal(cliTask.metadata.target, "reviewer");
  assert.equal(cliTask.metadata.runtime, "codex");
  assert.equal(cliTask.metadata.instance, newQuestion.metadata.instance);

  // These are fixture checks of orchestrator decisions, not an implemented scheduler/recovery engine.
  const { stale_review, lost_response } = examples.recovery;
  assert.notEqual(stale_review.reviewed_sha256, digest);
  assert.equal(stale_review.decision, "withheld");
  assert.equal(lost_response.status, "delivery_uncertain");
  assert.equal(lost_response.action, "inspect_without_resubmit");
  assert.equal(lost_response.resubmissions, 0);
  assert.equal(examples.record.observed_status, "completed");
  assert.equal(examples.record.acceptance.decision, "withheld");
  console.log(JSON.stringify({ mode: "public_a2a_scripted_workers", live_agents: false,
    ordinary_workflow: "passed", streaming: "passed", new_task_same_context: "passed",
    same_writer_without_competition: true, same_writer_after_competition: false,
    referenced_history_injected: false,
    adoption_gate: "failed_same_writer_affinity", performance_cost_quality: "not_measured",
    hybrid_protocol: { explicit_handoff: "passed", parallel_partial_failure: "passed",
      input_required_continuation: "passed", completed_task_rejected: "passed", new_task_after_completion: "passed",
      stock_cli_contract: "passed" },
    example_checks: { input_hash: "passed", dependencies: "passed", stale_review_withheld: "passed",
      uncertain_delivery_no_resubmit: "passed", completion_not_acceptance: "passed" }, trace }, null, 2));
} finally {
  await gateway.close();
}
