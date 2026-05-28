## 27.2.2026

### What I did

Started the thesis project by setting up the local LLM environment and creating the initial README.md file.

### What I learned

Learned how to use Ollama to run local LLMs. Also learned that the benchmarking might be a headache, if I'm going to use SWE-bench. It requires too much disk space for my computer (120 GB). https://www.swebench.com/SWE-bench/guides/docker_setup/

### What I want to do next

It's crucial to get the benchmarking right, so I need to research different benchmarking tools and methods for LLMs. Using MLFlow for tracking the experiments seems like a good idea.

## 28.2.2026

### What I did

Explored benchmarking options for evaluating the local Qwen models:

- Investigated **SWE-bench** (2,294 real-world GitHub issues) — requires ~120 GB Docker images for evaluation. Considered remote evaluation via `sb-cli` + Modal cloud, but pivoted to a simpler local solution. Aider benchmark is a much more practical alternative for local benchmarking — it's well-documented, reproducible, resource usage is neglible. https://aider.chat/2024/12/21/polyglot.html#the-polyglot-benchmark
- Settled on the **Aider polyglot benchmark** — 225 Exercism coding exercises across C++, Go, Java, JS, Python, and Rust. Runs locally in a lightweight Docker sandbox. Qwen 32B Coder is already on the Aider leaderboard, so we get a direct comparison.

Set up the benchmarking pipeline with AI generated scripts:

- Created `docs/architecture.md` with Mermaid diagrams showing the system architecture.
- Created `scripts/run_aider_benchmark.sh` for running the benchmark against Ollama.
- Created `scripts/log_benchmark_to_mlflow.py` for logging results to MLflow for experiment tracking.

**Important discovery: Ollama context window.** Ollama defaults to 2K context tokens, which is far too small for Aider. It silently drops context, leading to degraded results. Must set `OLLAMA_CONTEXT_LENGTH=8192` (or higher) before running benchmarks.

### What I learned

Learned that there are many different benchmarking tools and methods for LLMs. Also learned that MLFlow is a good tool for tracking experiments https://mlflow.org/docs/latest/ml/tracking/.

## 2.3.2026

### What I did

Ran the Aider benchmark against the local Qwen 32B model. Also installed MLFlow in a virtual environment to have visibility of the results. The benchmark did not run at first, but after some debugging I got it to run. Then I made the results include charts and a summary markdown file.

### What I learned

Learned that the benchmark is going to take a lot of time to run fully, so I'll need to figure out ways to run language targetted benchmarks instead of the full benchmark.

### What I want to do next

After the benchmark is done, I'll need to figure out how to fine-tune the models to improve their performance. I'll also need to figure out how to use the models in an agentic style workflow.

## 3.3.2026

### What I did

Ran the Aider benchmark against the local Qwen 32B model for the whole benchmark. Started to second guess the OLLAMA_CONTEXT_LENGTH=8192 setting, so I added that to MLFlow logging. Pip requireremts were frozen, since they may provide variance in results otherwise.

### What I learned

Benchmarking is time consuming, so it's productive to run it overnight to utilize the time when I'm not using resources for other tasks.

### What I want to do next

I need to run the benchmark for the 7b model too at some point in the future to have a baseline for comparison for that one too and gather info on other possible models to use.

## 4.3.2026-7.3.2026

### What I did

Analysis on the results of the Aider benchmark for the large OLLAMA_CONTEXT told that it did not matter for the performance of the model. The results were almost identical with the stock context length of 2048 tokens, so I was suspicious of Ollama being able to read the environment variable that was set. I was right about that, since Aider does allow for overriding the context length of the model. It can be done with the `--num-ctx` flag. https://github.com/Aider-AI/aider/commit/c5ce57ea7fe93242600643541c4376ef015c7bdd. Documentation is not great, but studying source code revealed that it is possible to override the context length of the model. Context length should affect the performance, especially if we're defaulting to around 2048 tokens. https://datanorth.ai/blog/context-length

Now that there's a rudimentary, repeatable benchmark, I can start working on the fine-tuning part of the thesis. We should run the whole benchmark with different context windows, to gather some baseline results for the thesis. Then when we run the benchmark for the fine tuned model, we can compare the results to the baseline results to see if the fine-tuning improved the performance of the model and if there are regressions in performance for other languages, which should be expected somewhere along the fine tuning path.

The results produced by the benchmark did show that the context length was unnessary override, as Aider does adjust the context length of the model automatically based on the message size.

```
if self.is_ollama() and "num_ctx" not in kwargs:
    num_ctx = int(self.token_count(messages) * 1.25) + 8192
    kwargs["num_ctx"] = num_ctx
```

That would also explain why the results were almost identical with the stock context length of 2048 tokens, since the Aider would adjust the context size automatically based on the message size.

### Put pics here to show the almost identical results for context length.

I also benchmarked the 7b model and the results were almost identical to the 32b model.

### Put pics here to show the results of the 7b model.

## 4.5.2026

Time allocations have not been favourable to thesis work, and thus I've missed out on 2 months of time. Meanwhile models have been evolving, and same has happened to IDE's and agentic first workflow. I question the need for fine tuning at this point in time, as quantization will produce smaller versions of current frontier models, that are more than capable daily drivers for experienced developers. I run a risk of producing an outdated solution on, that's complex, brittle and not actually helpful, when compared to just locally running a quantized model that has great capabilities in a years time.

This represents a strategic pivot in the thesis: moving away from the effort-intensive process of fine-tuning a specific model for a narrow task, and instead focusing on the orchestration and deployment of high-performance quantized models. By leveraging quantization, I can utilize much larger, more capable frontier models (like Gemma 4) within the hardware constraints of a local machine, shifting the research focus from "model training" to "agentic workflow optimization."

### What I want to do next

The new goal is to provide a premier developer experience (DX) focused on a safe, sound, and fully private local agentic workflow, leveraging cutting-edge quantized models like Gemma 4.

The steps required to achieve this agentic experience will be:

1. **Local Infrastructure Setup**: Deploy Gemma 4 via Ollama, focusing heavily on its tool-calling capabilities which are prerequisite for an agent.
2. **Client Integration**: Bind VSC to natively use the local model ensuring all repository context is retained on-device.

### Today's work

Had to update a bunch of software with brew, since the thesis machine has been idle for quite a while. The main reason being that latest Gemma-modal required a newer version of ollama to function. Installed Continue.dev to have something that resembles the agentic workflow of stock VSC Agent mode.

After some intensive AI-helped troubleshooting, the Gemma 4's 31 billion parameter did manage to run in the Continue.dev. The json used for the configuration:

```json
{
  "models": [
    {
      "title": "Gemma 4 (31B)",
      "provider": "ollama",
      "model": "gemma4:31b"
    },
    {
      "title": "Qwen2.5-Coder (32B)",
      "provider": "ollama",
      "model": "qwen2.5-coder:32b"
    },
    {
      "title": "Qwen2.5-Coder (7B)",
      "provider": "ollama",
      "model": "qwen2.5-coder:7b"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen2.5-Coder (7B)",
    "provider": "ollama",
    "model": "qwen2.5-coder:7b"
  },
  "embeddingsProvider": {
    "provider": "ollama",
    "model": "nomic-embed-text"
  }
```

This was placed in .continue-directory as config.json. That did not provide anything useful, as a simple request for "take a look on our repository for context" did not even produce an answer. Next I tried to insert a "@codebase"-command, if that would do something on the Qwen2-5-coder 32Billion model, and that resulted in an additional request for individual files instead of providing any context from the repository. Then I downloaded the model that was in the settings for Continue.dev as the embeddings-model:

```
ollama pull nomic-embed-text

pulling manifest
pulling 970aa74c0a90:  47% ▕████████          ▏ 128 MB/274 MB   14 MB/s      9s
```

After that I was able to use the nomic-model behind the scenes for codebase context, with the command:

```
@codebase
```

This started an indexing operation for the codebase, as shown in the chat output:

```
The root directory contains several interesting files and folders:

docs/: Likely contains documentation.
scripts/: Probably contains executable scripts for the project.
mlflow.db and mlruns/: These indicate that MLflow is being used for experiment tracking.
requirements.txt: Lists the project dependencies.
Diary.md: Might contain development notes or a project log.
README.md: The main entry point for project information.
I'll start by reading the README.md to get a high-level overview of the project's purpose and how to use it.
```

A simple edit to a text file took around 5 minutes to complete on a 2025 Macbook Pro M4 with 48GB RAM. This was in the ballpark of what I expected, given that the model is running locally. This then does raise the question of the usability of these local models in their current state for the development workflow.

How to then compare results of frontier models and quantized models? I'll give them the same prompts and see where the results differ. I'll also make another frontier model evaluate the answers both models produce.

## 5.5.2026

Today was a day of experimentation on a project. Project consists of a Svelte frontend and a Go backend. Asking a broad question like "Could you vet the current state of the implementation from ROADMAP.md" didn't provide anything useful, since the vetting only looked for simple grepable phrases, instead of actually reasoning about the codebase in relation to the roadmap. A frontier model (Gemini 3.1 Pro) did provide a better answer from the same initial prompt.

Gemma 4 31B's response:

```bash
Based on the provided code snippets, here is a summary of the functionality related to Stripe/Payment Integration and Webhooks:

1. Payment & Refund Logic
The system implements a refund mechanism integrated with Stripe:

Refunds: There is logic to handle refund requests, including a refunds field in various contexts.
Refunds via Stripe: The stripe package is used to execute these refunds.
2. Stripe Webhook Handling
The application contains a robust system for processing Stripe webhooks to keep the internal state synchronized with Stripe:

Webhook Endpoint: An HTTP handler receives events from Stripe.
Signature Verification: It uses Stripe's SDK to verify the authenticity of the webhook payload using a signing secret.
Event Dispatching: The system switches based on the event.Type to handle specific Stripe events:
checkout.session.completed: Triggered when a customer successfully completes a checkout session.
invoice.payment_succeeded: Triggered when a subscription or one-off payment is successfully processed.
invoice.payment_failed: Triggered when a payment fails, allowing the system to notify the user or restrict access.
customer.subscription.deleted: Triggered when a subscription is cancelled or expires.
3. Integration Points
Customer Mapping: The system maps Stripe Customer IDs to internal user records.
Subscription Management: It updates subscription statuses (e.g., active, past_due, cancelled) in the local database based on the webhook events received.
Payment Tracking: It logs successful payments to ensure services are provisioned or extended.
4. Error Handling & Security
Idempotency: The system likely checks event IDs to ensure that the same webhook event isn't processed multiple times.
Validation: Strict validation of the Stripe signature prevents "spoofing" attacks where an attacker could simulate a successful payment.
```

Gemini 3.1 Pro's response:

```bash
I've reviewed the current ROADMAP.md against the repository's reality, and it is highly accurate.

The checked items reflect features that actually exist in the codebase:

Remaining balance capture is fully wired up, and order-remaining-balance.e2e.ts is in place.
Refunds, stripe onboarding, and demo vs. live modes are correctly implemented according to Phase 4.
Production calendar controls, analytics, & sales export match the implementation in dashboard and analytics.
E2E Test targets have actual Playwright files corresponding to them in e2e (e.g., baker-workflow.e2e.ts, storefront-smart-order-forms.e2e.ts).
The pending ([ ]) items also accurately represent what isn't there yet:

No Open Graph tags or meta SEO logic is in the SvelteKit frontend yet.
There are no privacy policy/cookie consent routes added.
The CI workflows (ci.yml, deploy.yml, backup-verify.yml) lack SAST/container security scanning pipelines that the roadmap lists as pending.
One minor discrepancy:
In Phase 6, under Deliverables, you have marked [x] Status semantics polish — order status badges/icons are consistent, including Paid as green with a checkmark. The localization tools and CSS (status-paid-bg, #dcfce7) reflect this. However, under the Test Milestones section down below, the checkbox for this same item is still unchecked:
- [ ] Paid status renders as green + checkmark consistently in dashboard list and order detail views

Other than correcting that single unchecked test milestone box, your roadmap is perfectly in sync with the current implementation state.
```

So we can clearly see that the frontier model is better at understanding the task, and produces an actual answer to the request, unlike the locally run smaller model. Next I tried to ask for a better prompt to better suit the smaller model from the frontier model, to have a better chance of the smaller model producing a useful response.

Prompt for prompting the frontier model:

```
Could you provide a prompt for Gemma 4 (31B model) to provide a similar, actually helpful answer? Did you do some internal re-wording of my high level prompt to make it more actionable?
```

Frontier model's suggested prompt:

```
Please vet the current ROADMAP.md against the actual codebase implementation to see if it's accurate.

To do this, I need you to follow this exact process:
1. Read the ROADMAP.md file to understand the completed [x] and pending [ ] milestones.
2. Select 4-5 specific technical claims from the recent or current phases (e.g., specific E2E test files existing, a specific CSS class/color being implemented, CI/CD workflows, or specific API routes).
3. USE YOUR TOOLS (like terminal commands, grep, or file search) to actively look for the code that proves or disproves these claims.
4. Check a few of the pending [ ] items to confirm they actually haven't been implemented yet (e.g., SEO tags, privacy policy).
5. Provide a summary of your findings, explicitly calling out any discrepancies where the roadmap claims something is done but the code is missing, or vice versa.
```

Gemma did not do a good job - it did not answer the actual question, since we needed vetting of current implementation against the roadmap claims. The provided response did a high level overview of the project structure, not an analysis of the roadmap claims.

```
This project is a full-stack web application designed for a bakery/cake business management system. It allows bakers to manage their shop, products, and orders, while providing a customer-facing interface for ordering.

Based on the file structure, here is a detailed breakdown of the architecture:

1. Tech Stack
Backend: Go (Golang) — evidenced by the .go files in the internal and cmd patterns.
Frontend: Svelte/TypeScript (implied by the project structure and common patterns for this type of Go stack), likely using a modern framework for the dashboard and storefront.
Database: PostgreSQL (indicated by the migration-style scripts in the migrations or internal logic and the focus on relational data).
Infrastructure: Likely deployed on Linux/Docker (given the scripts and configuration patterns).
2. Core Functional Modules
Order & Product Management (/internal/order, /internal/product): Handles the lifecycle of a cake order, from a customer request to completion.
Bakery Dashboard: A management interface for the baker to track orders, manage their catalog, and configure shop settings.
Payment Integration (/internal/stripe): Integrated with Stripe for handling payments and payouts.
Authentication & User Management (/internal/auth): Handles identity and access control for both customers and shop owners.
Storage (/internal/storage): Likely handles image uploads (e.g., cake photos) using S3 or similar object storage.
3. Key Directory Analysis
/internal: Contains the core business logic.
auth: User registration, login, and session management.
bakery: Logic for shop configurations and baker profiles.
orders: The engine for managing customer orders and statuses.
products: Management of the cake menu and customizations.
/cmd: The entry points for the application (e.g., the main server executable).
/migrations: SQL scripts used to evolve the database schema.
/web (or frontend folder): The client-side code for the storefront and admin panel.
4. Summary of Workflow
The Baker sets up their shop, uploads photos of their cakes, and defines pricing/options.
The Customer visits the storefront, selects a cake, customizes it, and pays via Stripe.
The System notifies the baker and creates an order entry.
The Baker manages the order through a dashboard, updating the status as they bake and deliver.
```

Self-prompting the Gemma model in agent-mode was not helpful, as it did a small chunk of wirk, but didn't immerse in deep work to produce comprehensive helpful answers. Instead the model abruptly stopped mid task:

```
First, let's search for these terms in internal/auth/service.go.
```

I think this is a context issue, the model is not able to maintain the context of the task long enough to complete it. A simple 'continue'-prompt did help complete the task in the end, but it took several attempts and the result was a subpar answer, that only vetted a small fraction of the actual codebase:

```
Summary of Verified Files
internal/auth/*.go: Verified Magic Link and MFA logic.
internal/database/migrations/*.sql: Verified schema and RLS constraints.
internal/middleware/tenant.go: Verified tenant context injection.
cmd/api/main.go: Verified the wiring of the middleware chain
```

6.5.2026

Frontier: Gemini 3.1 Pro

Locally: Gemma 4 (31B)

Today I tried a different approach, as the task of comparing the codebase to the roadmap failed, as the smaller model got lost. The task I set out to do was a simpler task, where we presume the current roadmap of the project is up to date, and ask the model to provide a suggestion on next work items.

Prompt used:

```
What should we work on next from our ROADMAP.md?
```

Gemma provided a faulty answer, that suggested we still had some work to do in Phase 5, when in reality we had completed it.

```
Based on the ROADMAP.md and the mermaid design files, here is the current status and the recommended next steps:

Current Status
The project is currently in Phase 5 (Production Calendar & Baker Tools)
<rest of answer..>

```

Gemini provided a much better answer:

```
Based on the current state of ROADMAP.md, we are currently in Phase 6: Polish, E2E & Production Hardening.
<rest of answer..>
```

Gemini's answer proves it was able to read the simple checkboxes from the ROADMAP, and thus deduce what was done and what was left to do. Gemma just did a guess. When prompted to take an actual look at the ROADMAP, it provided this answer:

```
You are correct. I relied on the grep output, which was truncated and didn't show the full context of the checkboxes. Because the read_file tool failed due to the file size, I missed the actual state of the checkboxes in the main body of the roadmap.

<rest of answer..>
```

Model did not give up, but continued to try and correct the faulty output by using grep more creatively, to work around file size limits. That did produce a better answer, so file size limits are something that must be taken into consideration when a local model is used, since they're quite restrictive. ROADMAP.md is 764 lines, which is not that big, but the tool clearly has its limits.

I read up on Modelfiles, they're files you can use to customize the ollama-run models. SOURCE HERE. I created 2 system prompts, 1 for a developer and 1 for a product manager.

```
FROM gemma4:31b

# Good settings for coding + agentic use

PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER num_ctx 16384
PARAMETER repeat_penalty 1.05
PARAMETER num_predict 2048

# Strong coding system prompt

SYSTEM """
You are an expert full-stack developer specialized in Go & SvelteKit.
Always think step-by-step using chain-of-draft reasoning:

1. Start from user interaction / UI element
2. Trace through services, controllers, repositories
3. Check database layer
4. Return to frontend

Explain your reasoning clearly before suggesting code changes.
"""

"""
```

And the one for produc t manager:

```
FROM gemma4:31b

PARAMETER temperature 0.3
PARAMETER top_p 0.95
PARAMETER num_ctx 16384
PARAMETER repeat_penalty 1.1
PARAMETER num_predict 2048

SYSTEM """
You are a pragmatic, high-output Product Manager for a niche e-commerce platform built with Go (backend) and Svelte (frontend).

Core rules:
- Get shit done. Be direct, decisive, and action-oriented.
- Always prioritize speed-to-value and business impact.
- Think in user stories, acceptance criteria, edge cases, and clear requirements.
- Break down features into small, shippable pieces.
- Suggest concrete Go API changes, Svelte component structures, or DB schema updates when relevant.
- Keep answers concise and execution-focused. Avoid fluff.

When I describe a feature or problem, respond with:
1. One-sentence goal
2. Recommended approach (fastest viable path)
3. Key user stories + acceptance criteria
4. Technical considerations (Go/Svelte specific)
5. Potential risks & mitigation
"""
```

Then I created the tunings with ollama create:

```
ollama create dev-gosvelte -f MODELFILE_DEV.md
ollama create pm-gosvelte -f MODELFILE_PM.md
```

That produced output in terminal:

```
ollama create dev-gosvelte -f MODELFILE_DEV.md
gathering model components
using existing layer sha256:280af6832eca23cb322c4dcc65edfea98a21b8f8ab07dc7553bd6f7e6e7a3313
using existing layer sha256:7339fa418c9ad3e8e12e74ad0fd26a9cc4be8703f9c110728a992b193be85cb2
creating new layer sha256:5e0e8bf5272f712e12c37e5f1fe4c716a61efe2670665a3c7a33f2c760fd842b
creating new layer sha256:d2cd855f32a5086ad61493c2fe40adc924db42120b631852e159345ad4b31de3
writing manifest
success
```

After that I needed to add those to the configuration for Continue.dev:

```json
{
  "models": [
    {
      "title": "PM Go+Svelte",
      "provider": "ollama",
      "model": "dev-gosvelte"
    },
    {
      "title": "PM Go+Svelte",
      "provider": "ollama",
      "model": "pm-gosvelte"
    },
    {
      "title": "Gemma 4 (31B)",
      "provider": "ollama",
      "model": "gemma4:31b"
    },
    {
      "title": "Qwen2.5-Coder (32B)",
      "provider": "ollama",
      "model": "qwen2.5-coder:32b"
    },
    {
      "title": "Qwen2.5-Coder (7B)",
      "provider": "ollama",
      "model": "qwen2.5-coder:7b"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen2.5-Coder (7B)",
    "provider": "ollama",
    "model": "qwen2.5-coder:7b"
  },
  "embeddingsProvider": {
    "provider": "ollama",
    "model": "nomic-embed-text"
  }
}
```

This addition brougth the models available to me to 5.

A simple prompt for Gemma 4 31B, product manager tuning:

```
Could you read out our ROADMAP.md and see what are the key stuff still missing for launch?
```

Produces actually pretty good results (compared to the previous version):

```
Based on the grep_search results from the ROADMAP.md, here are the key items still missing or pending for launch:

🚨 High Priority / Pending
Stripe Identity Prefill: Wiring the business profile fields (PRH/YTJ identity inputs like business_id, vat_id, company_name_official) into the Stripe account creation process is still pending.
Per-Product Capacity: While general calendar forecasting is live, implementing per-product capacity for storefront availability and lead-time calculations is still pending.
Auth Rollout: The "FORCE RLS" (Row Level Security) for Auth Phase 5 is validated locally, but the non-local rollout is deferred until a server environment is available.
📅 Planned (Future/Missing)
The following items are explicitly listed as "Planned", meaning they are not yet implemented:

Custom Uploads: Ability for customers to upload references and bakers to upload cake photos.
Minimum-Order Thresholds: Setting a minimum spend/order amount.
Manager Sales Exports: Tools for exporting sales data.
🛠️ Partial Implementation
Calendar UX: The backend and API enforcement are in place, but "richer calendar UX" (specifically the per-product capacity mentioned above) is still missing.
Summary for Launch: To get to a "launch-ready" state, the team primarily needs to finish the Stripe identity wiring, implement per-product capacity for the storefront, and move the Auth RLS from local validation to the server environment.
```

While Gemini 3.1 Pro produced:

```
Phase 1: Onboarding & Branding
Extended storefront branding: Premium customization options for bakers (fonts, hero images, layout themes) to give their pages a professional website feel.
Phase 4: Payments
Stripe Identity Prefill: Automatically prefilling the Stripe Connected account creation with full identity fields (tax, company, representative) using the data already collected in the CakeMate baker profile.
Transaction Security: Final security hardening on transactions to ensure bakers get their money and customers get their cakes securely.
Phase 6: Polish & Production Hardening
Security Audits & CI Gates:
OWASP Top 10 review on all public surfaces.
Adding a security audit gate in CI (dependency, SAST, and container scans) before merge/push.
Scheduled automated security audits on main.
Traffic & Rate Limiting:
Conducting a rate limit review to ensure all public endpoints are protected.
Running a performance baseline / load test with simulated baker and customer traffic.
Legal & Compliance:
Setting up the Privacy Policy, Cookie Consent, and ensuring GDPR compliance (tailored for the Finnish market).
SEO Optimization:
Adding meta tags and Open Graph data for baker profile pages.
Database/Auth Infrastructure:
Non-local rollout of FORCE RLS (Row-Level Security), which is currently deferred until non-local server infrastructure is available.
```

Both answers are atleast sane suggestions.

It did not solve for the issue of having too large of a ROADMAP.md file, so I looked into RAG (Retrieval-Augmented Generation) and Vectorization to improve hit rate SOURCE HERE.

```

## 7.5.2026

Looking into RAG, I went the vectorization route and standardized around Qwen3-Embedding-4B-model for the embeddings after research SOURCE HERE.

```

ollama pull qwen3-embedding:4b

```

First experiment was to index the ROADMAP.md file:

```

ollama create roadmap-index -f MODELFILE_RAG.md

```

MODELFILE_RAG.md:

```

FROM qwen3-embedding:4b

# Use semantic hashing to find similar chunks

# This is more reliable than simple keyword matching

PARAMETER sematic_search true

# Keep context window small - we only need the relevant chunks

PARAMETER num_ctx 2048

# High temperature for more creative retrieval (surprising but relevant chunks)

PARAMETER temperature 0.7

SYSTEM """
You are a retrieval system for a Go + Svelte e-commerce platform. Your job is to find the most relevant pieces of documentation for the user's query.

When the user asks a question:

1. Break down the query into key concepts
2. Search for semantically similar chunks in the ROADMAP.md index
3. Return the top 5 most relevant chunks
4. Show how they relate to the user's question

Think like a product manager who needs to understand what features are planned, what's already built, and what's missing.
"""

```

## 9.5.2026

Continue.dev didn't seem to co-operate first with repo specific configurations, as it kept using the global ones. Adding a .continuerc.json in .continue folder worked like a charm.

```

{
"mergeBehavior": "overwrite",
"disableIndexing": false,
"models": [
{
"title": "PM Go+Svelte repo",
"provider": "ollama",
"model": "dev-gosvelte"
},
{
"title": "PM Go+Svelte repo",
"provider": "ollama",
"model": "pm-gosvelte"
},
{
"title": "Gemma 4 (31B) repo",
"provider": "ollama",
"model": "gemma4:31b"
},
{
"title": "Qwen2.5-Coder (32B) repo",
"provider": "ollama",
"model": "qwen2.5-coder:32b"
},
{
"title": "Qwen2.5-Coder (7B) repo",
"provider": "ollama",
"model": "qwen2.5-coder:7b"
}
],
"tabAutocompleteModel": {
"title": "Qwen2.5-Coder (7B) repo",
"provider": "ollama",
"model": "qwen2.5-coder:7b"
},
"embeddingsProvider": {
"provider": "ollama",
"model": "qwen3-embedding-4b"
}
}

```

Continue builds the RAG index automatically using the configured embeddings provider. While doing this, I realized that VSC natively supports local ollama models without any plugins, and decided to give it a spin. However, VSC's version of locally run models can't use RAG index SOURCE HERE. This is highly problematic, since the model is basicly guessing instead of verifying from the whole ROADMAP.md.

```

Planned Product Features
These are the next high-priority items in the product delivery track:

Stripe Identity Prefill: Implement prefilling Stripe account identity fields using the CakeMate business profile data.
Photo Uploads:
Baker cake photos.
Custom-only customer reference uploads.
Advanced Availability: Implement per-product capacity within the availability and lead-time calculations.
Order Constraints: Add minimum-order thresholds.
Reporting: Create manager sales exports.
🛡️ Auth & Infrastructure
FORCE RLS Rollout: The "Auth Phase 5 FORCE RLS" is validated locally, but the non-local rollout is currently deferred until a server environment is available.
Which of these would you like to tackle first?

Restore Checkpoint
Why do you say that the photo uploads are not done?

Searched for regex photo|upload|image, 20 results
I apologize—I was relying on the Roadmap Summary and Planned sections at the top of ROADMAP.md, which list "customer and baker photo uploads" as next steps.

However, looking further down in the document, I see they are actually marked as completed:

```

That led back to the Continue.dev configuration, since that's where we can make the model behave better, and use a RAG-approach. Next I tested it again with the Qwen embeddings model and a new Gemma-model, gemma4:31b-coding-mtp-bf16, since it's supposed to be faster SOURCE HERE.

And then I hit another snag, as indexing has been deprecated in the Continue.dev workflow: [Documentation](https://docs.continue.dev/guides/codebase-documentation-awareness). So I removed the relevant lines from the model files, and we're back to square one, but with a better model. And that failed too, since I did not have enough GPU memory.

```

"model requires 59.1 GiB but only 35.5 GiB are available (after 512.0 MiB overhead)"

```

Then I redid the gemma4-customizations again with the 31B model and tried again. This time with the Agent-mode directly, instead of plan-mode. I also made a change, as a rule was added based on the SOURCE HERE Continue.dev docs.

```

# ROADMAP.md Context

The overall project plan, built features, in-progress items, and next milestones are managed in `/ROADMAP.md`. When answering questions about project goals, timelines, or built vs planned features, use the file exploration tools to read the relevant sections of `ROADMAP.md`.

```

And yet again, we did get the same results, where we have hallucinated that the baker photo uploads are still undone.

```

Based on the ROADMAP.md, the project is currently in Phase 5 (Calendar Tooling) and the Auth-Hardening track.

The "Next planned" items are explicitly listed in the Roadmap Summary:

🚀 Immediate Next Priorities
Stripe Identity Integration: Implement business profile prefill for Stripe identity.
Media Uploads:
Custom-only customer reference uploads.
Baker cake photos.
Advanced Availability Logic:
Per-product capacity in availability and lead-time calculations.
Order Constraints:
Minimum order thresholds.
Reporting:
Manager sales exports.
Current Status Context
Built: Stripe Connect APIs, MFA/Recovery flows, and the production calendar board (working days/overrides).
In-Progress: Calendar availability backend is in place, and dashboard modularization is underway.
Deferred: The "FORCE RLS" rollout for Auth Phase 5 is deferred until a non-local server environment is available.
Recommendation: Depending on whether you want to focus on Revenue/Onboarding or Product Depth, I suggest starting with either the Stripe identity-prefill (to smooth the onboarding funnel) or the per-product capacity (to make the calendar tooling truly production-ready for complex bakers).

```

So, naturally the next step was to ask the model again why it hallucated the baker photo uploads. And the result was that the summary in the ROADMAP.md was outdated, which is correct. This is quite common in my experience in software projects - the documentation is not up to date with the code. We should be able to fit a 56kb document into the context, as it's not that huge, so we added a line for each of our models in .continuerc.json.

```

"contextLength": 32768

```

The next customization was to modify the MODELFILE-files to incluce the context setting too:

```

PARAMETER num_ctx 32768

```

The new prompt was including the context for the file as such:

```

What should we work on next from our @ROADMAP.md?

```

That still resulted in the model being confused, since the summmary suggested that the photo uploads are still undone. So then the next idea was to remove the summmary from the file, as that's redundant information. This did improve the results significantly.

The answer from Gemini 3.1 Pro:

```

Based on your ROADMAP.md, there are a few unfinished items from earlier phases, as well as the main tasks remaining in your current phase (Phase 6: Polish & Hardening).

```

And from the pm-gosvelte model:

```

Based on the
ROADMAP.md
, the project is very far along, with Phases 0 through 5 completely finished and Phase 6 (Production Hardening) nearly complete.

```

This raised hopes for the locally run model to be able to read and understand the ROADMAP.md file correctly. After this pm-flow, we needed to quantify and scope a unit of work for the coding-flow.

## 10.5.2026

So then the next thing to verify was the scoping of work to be done. So I asked the model to propose a single feature to be implemented. My intuition was that this was a straightforward enough task that the model would be able to determine that we need: UI for managing tags (CRUD) and API endpoints for managing tags, and that it would propose the implementation of these tasks. The feature is also "blue ocean", in that sense that it's fresh code, and thus something that shouldn't cause regressions in the existing codebase.

Prompt used (Plan mode):

```

@ROADMAP.md

SEO — Add meta tags and Open Graph data for baker profile pages. Lets make a plan to implement this.

```

Frontier model (Gemini 3.1 Pro) response:

```

Here is a plan to implement SEO meta tags and Open Graph data for baker profile pages.

Plan: Backend SSR & Open Graph for Baker Profile
Currently, the baker profile page (frontend/src/routes/[slug]/+page.svelte) fetches baker data client-side in onMount. Social media crawlers and search engine bots generally do not execute JavaScript, meaning they see a blank page without metadata. To add effective SEO and Open Graph data, we need to load the primary baker metadata during SvelteKit's Server-Side Rendering (SSR).

Steps

Extract Baker Fetch to SSR: Create frontend/src/routes/[slug]/+page.ts with a load function that runs during SSR. It will fetch(/api/bakers/${params.slug}). To preserve the custom branded "Not Found" UI, if the API returns 404, the load function will return { baker: null, notFound: true } instead of throwing a generic SvelteKit error.
Refactor Page State Initialization: Update frontend/src/routes/[slug]/+page.svelte to accept let { data } = $props(); and synchronize the local states baker and notFound with data. Remove the local fetch('/api/bakers/{slug}') from onMount.
Keep Secondary Payloads Client-Side: Keep the /products and /calendar/availability fetch routines inside onMount to ensure fast Time To First Byte (TTFB) and prevent blocking SSR.
Implement Extended Meta Tags: Expand the existing <svelte:head> in frontend/src/routes/[slug]/+page.svelte to include full Open Graph (og:title, og:description, og:image, og:url) and Twitter Card equivalents. Use $page.url.href for canonical URLs and baker.logo_url conditionally if it exists.
Relevant files

frontend/src/routes/[slug]/+page.ts — (New) Universal load function for /api/bakers/{slug}.
frontend/src/routes/[slug]/+page.svelte — Consume data.baker, clean up onMount, and add the new <meta> elements into <svelte:head>.
Verification

Run local dev server (make dev).
Load a baker profile using curl -s http://localhost:5173/demo-baker and verify that the HTML response source code straight from the server contains the populated <title> and Open Graph <meta> tags.
E2E Test: Run make test:e2e to verify no client-side behavior broke during refactoring of onMount.
Further Considerations

Is there an intention to provide SEO tags to other surfaced pages (e.g. the static landing page)? We could add standard tags for the root / page simultaneously if you prefer!
for the root / page simultaneously if it requires better previews when shared.
Let me know if this looks good to you or if you want changes on anything!

```

Local model (Gemma 4 31B pm-tuned model) response:

```

To implement SEO and Open Graph (OG) data for baker profile pages, we need to ensure that when a baker's shop URL (cakemate.fi/{slug}) is shared on social media or indexed by search engines, it displays a professional preview (title, description, and image) tailored to that specific baker.

Since the frontend is built with SvelteKit, we can leverage its SSR (Server-Side Rendering) capabilities to inject these tags dynamically based on the baker's profile data.

Proposed Implementation Plan

1. Backend: SEO Metadata API
   We need to ensure the backend provides the necessary fields for SEO.

Verify existing fields: Check if the baker profile already contains description, meta_title, or profile_image_url.
Enhancement: If missing, add optional SEO-specific fields to the baker profile (e.g., seo_title, seo_description) so bakers can customize how they appear in Google, rather than just using their "About Me" text. 2. Frontend: Dynamic Meta Tag Injection
In SvelteKit, we will use the <svelte:head> tag within the public profile route to inject metadata.

Route: src/routes/[slug]/+page.server.ts (to fetch data) and +page.svelte (to render tags).
Logic:
Title: [Bakery Name] | Custom Cakes in [City]
Description: Use the baker's short bio or a generated summary.
OG Image: Use the baker's logo or a default "CakeMate" branded image if none is provided.
Canonical URL: Set the canonical link to the baker's specific slug. 3. Open Graph & Twitter Card Specifics
We will implement the following tags:

og:title, og:description, og:image, og:url, og:type (website).
twitter:card (summary_large_image), twitter:title, twitter:description, twitter:image. 4. Automation (The "SEO Automation" Nice-to-Have)
As mentioned in the "Nice To Have" section of the roadmap, we can automate the generation of these tags:

Template-based generation: If the baker hasn't provided a custom SEO description, generate one: "Order custom cakes from [Bakery Name] in [City]. Professional cakes for weddings, birthdays, and more."
Technical Execution Steps
| Step | Task | File/Area | | :--- | :--- | :--- | | 1 | Audit baker model for SEO fields | internal/baker/ | | 2 | Update Backend API to return SEO metadata | internal/baker/handler.go | | 3 | Implement <svelte:head> logic in SvelteKit | frontend/src/routes/[slug]/+page.svelte | | 4 | Create a helper for "Automated SEO" text generation | frontend/src/lib/seo-utils.ts | | 5 | Verify with opengraph.xyz or similar tools | Testing |

Next Steps
To start this, I need to see the current baker profile data structure and the existing public profile route in the frontend.

Would you like me to start by exploring the backend baker model and the frontend profile route?

```

In this task, the codebase owner actually prefers the local model's answer, as it's more to the point. It also has picked up extra context from the ROADMAP.md (from the "Nice to have" section), for the scoping of the feature.

Next I made separate git branches for the local model and frontier model.

```

git checkout -b gemma4-dev-1

```

Frontier model (Gemini 3.1 Pro):

```

git checkout -b frontier-dev-1

```

This way it would be possible to compare the results of the models more concretely, since they would be working on the same codebase.

## 11.5.2026

Next I did a simple linter fix request for both models. This time I did not give the files as explicit context, but left for the models to figure out.

Prompt:

```

/app/src/lib/components/dashboard/OnboardingProfileStep.svelte

55:6 error 'calendar_capacity_scope' in 'profile' is an unused property svelte/no-unused-props

/app/src/lib/components/dashboard/StorefrontControls.svelte

15:6 error Prefer using writable $derived instead of $state and $effect svelte/prefer-writable-derived

✖ 2 problems (2 errors, 0 warnings)

Could you fix these?

```

Gemma 4 31B dev-tuned model response was subpar, it did not solve for the linter errors and left "// ... existing code ..." placeholders in the code. Also 2 small linter errors were converted to 10 failing tests.

The frontier model (Gemini 3.1 Pro) solved the linter errors and left the code clean and without placeholders. This anecdote serves as an example that even a small, tightly scoped task might be a tall order for a local model.

Next I tried to give the local model some more understanding with the "/init"-command Continue.dev offers. Which is basicly a hard coded prompt:

```

You are an expert development assistant. Your task is to create a comprehensive CONTINUE.md project guide for the user's codebase to help them and their team better understand and work with the project. ## Step 1: Check Required Tools First, verify that you have access to the necessary tools: - file_glob_search: To discover project files - read_file: To analyze file contents - ls: To explore directory structure - create_new_file: To generate the CONTINUE.md file If any of these tools are unavailable, inform the user that they need to activate them and enable "Agent Mode" in Continue before proceeding. ## Step 2: Project Analysis Analyze the project structure and key files to understand: - The programming languages and frameworks used - The overall architecture and organization - Key components and their responsibilities - Important configuration files - Build/deployment system ## Step 3: Generate CONTINUE.md Create a comprehensive CONTINUE.md file in the .continue/rules/ directory with the following sections: 1. **Project Overview** - Brief description of the project's purpose - Key technologies used - High-level architecture 2. **Getting Started** - Prerequisites (required software, dependencies) - Installation instructions - Basic usage examples - Running tests 3. **Project Structure** - Overview of main directories and their purpose - Key files and their roles - Important configuration files 4. **Development Workflow** - Coding standards or conventions - Testing approach - Build and deployment process - Contribution guidelines 5. **Key Concepts** - Domain-specific terminology - Core abstractions - Design patterns used 6. **Common Tasks** - Step-by-step guides for frequent development tasks - Examples of common operations 7. **Troubleshooting** - Common issues and their solutions - Debugging tips 8. **References** - Links to relevant documentation - Important resources Make sure your analysis is thorough but concise. Focus on information that would be most helpful to developers working on the project. If certain information isn't available from the codebase, make reasonable assumptions but mark these sections as needing verification. ## Step 4: Finalize After creating the .continue/rules/CONTINUE.md file, provide a summary of what you've created and remind the user to: 1. Review and edit the file as needed 2. Commit it to their repository to share with their team 3. Explain that Continue will automatically load this file into context when working with the project Also inform the user that they can create additional rules.md files in subdirectories for more specific documentation related to those components.

```

After the "/init"-command, I tried the same linter fix request again:

```

/app/src/lib/components/dashboard/OnboardingProfileStep.svelte

55:6 error 'calendar_capacity_scope' in 'profile' is an unused property svelte/no-unused-props

/app/src/lib/components/dashboard/StorefrontControls.svelte

15:6 error Prefer using writable $derived instead of $state and $effect svelte/prefer-writable-derived

✖ 2 problems (2 errors, 0 warnings)

Could you fix these?

```

That ended in the model omitting the contents of one the files effectively and making somewhat sane changes to the other file. Looking at the changes it looks like the model messed up in the changes in such a way that it mixed the edits for the two files together. I did a little manual editing for the file that was less mangled, and that ended up passing the linting.

## 12.5.2026

The fact that the local model mangles code for multiple files is concerning, since modern agentic flow is essential for speed of iteration, developers shouldn't need to worry about manually babysitting the context size or file sizes. Next I wanted to try out single file editing, if that would produce useful results, ie. editing the linter errors one by one.

Prompt used:

```

/app/src/lib/components/dashboard/OnboardingProfileStep.svelte

55:6 error 'calendar_capacity_scope' in 'profile' is an unused property svelte/no-unused-props

Fix this linter error.

```

Next I thought that maybe the local model tunings that were made were at fault for the poor performance. I questioned the modelfile assumptions and tweaked num_predict to -1 SOURCE HERE. Also did some research and changed the coding model to Qwen3 32b and tried the same editing task again with single file editing SOURCE HERE. Those tweaks resulting in a one shot fix for the linter error, so naturally the next step was to up the ante and try a two file edit request with these new model tunings.

Turns out that that was a bad choice, since the model botched the request in a similar way as before. So then I resorted to modifying the model tuning in the system prompt.

Modelfile for product manager agent:

```

FROM gemma4:31b

PARAMETER temperature 0.3
PARAMETER top_p 0.95
PARAMETER num_ctx 49152
PARAMETER num_predict -1

SYSTEM """
You are a pragmatic, high-output Product Manager for a niche e-commerce platform built with Go (backend) and SvelteKit (frontend).

CRITICAL RULES:

- ALWAYS read the actual files before answering questions about project state. Never guess from summaries or partial grep output.
- When checking completion status, look at the actual checkboxes: [x] = done, [ ] = pending.
- If a tool fails to read a file (e.g. too large), try reading it in sections rather than guessing.
- Be direct, decisive, and action-oriented. No fluff.

When I describe a feature or problem, respond with:

1. One-sentence goal
2. Recommended approach (fastest viable path)
3. Key user stories + acceptance criteria
4. Technical considerations (Go/Svelte specific)
5. Potential risks & mitigation

Always prioritize speed-to-value and business impact.
Break down features into small, shippable pieces.
"""

```

Modelfile for developer agent:

```

FROM qwen3:32b

PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER num_ctx 49152
PARAMETER num_predict -1

SYSTEM """
You are an expert full-stack developer specialized in Go & SvelteKit. /no_think

ABSOLUTE RULES — never violate these:

- NEVER use placeholder comments like "// ... existing code ...", "// rest of component", or similar. Every line of the file must be present in your output.
- When editing a file, output the COMPLETE file contents with your changes applied.
- Handle ONE FILE AT A TIME. Finish all changes for one file completely before moving to the next file.
- If asked to fix multiple files, present each file as a separate, clearly labeled code block.

Workflow:

1. Read the file(s) involved using available tools — never guess contents.
2. Identify the minimal change needed.
3. Output the full file with only the necessary lines changed.
4. If multiple files are involved, repeat steps 1-3 for each file sequentially.

Tech stack context: Go backend, SvelteKit frontend, PostgreSQL, Stripe payments.
"""

````

Then I modified the the continuerc.json to also use the longer context size:

```json
"models": [
    {
      "title": "DEV Go+Svelte repo",
      "provider": "ollama",
      "model": "dev-gosvelte",
      "contextLength": 49152
    },
    {
      "title": "PM Go+Svelte repo",
      "provider": "ollama",
      "model": "pm-gosvelte",
      "contextLength": 49152
    }
]
````

That still produced mangled output in files, having a "</think>" as the new content in one of the files. Next I modified the continuers.json to have a completion option:

```json
"models": [
    {
      "title": "DEV Go+Svelte repo",
      "provider": "ollama",
      "model": "dev-gosvelte",
      "contextLength": 49152,
      "defaultCompletionOptions": {
        "think": false
      }
    },
    {
      "title": "PM Go+Svelte repo",
      "provider": "ollama",
      "model": "pm-gosvelte",
      "contextLength": 49152,
      "defaultCompletionOptions": {
        "think": false
      }
    }
]
```

This setting tells Ollama at the API level to suppress thinking mode entirely, so the <think> blocks never get generated in the first place SOURCE HERE. This time around the 2 file edit took more than 3 hours and still failed.

## 13.5.2026

I looked into the Continue's settings and it had read_tool as false, so I changed that to true. Model still failed to edit the two files simultaneously, so I tried plan-mode for this next. This then resulted in the model trying to mod a wrong file that was open in the editor. After that the next help I gave to the model was to explicitly tell that the path is not from repository root, but from a test report.

```
/app/src/lib/components/dashboard/OnboardingProfileStep.svelte

  55:6  error  'calendar_capacity_scope' in 'profile' is an unused property  svelte/no-unused-props

/app/src/lib/components/dashboard/StorefrontControls.svelte

  15:6  error  Prefer using writable $derived instead of $state and $effect  svelte/prefer-writable-derived

✖ 2 problems (2 errors, 0 warnings)

Could you fix these? Be mindful of the path not being correct from repo root, as this an error message from 'make test'.
```

Plan-mode agent realized correctly, that the file path was indeed not from repository root, which should be given, since it was given in the prompt anyway.

Model's answer looked promising:

```
Now that we've located the correct files, let's proceed to fix the issues.

✅ Fix for frontend/src/lib/components/dashboard/OnboardingProfileStep.svelte
Issue:
The calendar_capacity_scope property in the profile object is unused.

Fix:
Remove or comment out the unused property.

✅ Fix for frontend/src/lib/components/dashboard/StorefrontControls.svelte
Issue:
Prefer using $derived over $state and $effect.

Fix:
Refactor the code to use $derived for derived values.

Would you like me to:

Show the corrected code for both files?
Provide a diff of the changes?
Or would you prefer to switch to Agent mode to apply the changes directly?
```

So then, agent mode was applied and the result was the agent being stuck on the editing task for such a time, that it would be highly inconvenient way for a real world use case, since manual edits for simple linter fixes are quite fast to do by yourself compared to this way of spoonfeeding and babysitting the agent.

Then I decided to switch tactics and request only fixes one file at a time and used a stock Qwen model without any special tunings. Prompt used container only the relevant error message:

```
/app/src/lib/components/dashboard/OnboardingProfileStep.svelte

  55:6  error  'calendar_capacity_scope' in 'profile' is an unused property  svelte/no-unused-props
```

Model failed misarably to find the file, since my prompt was not explicit on the path. Then I added the file's path to the prompt as context to try and get the model to find the file it's supposed to edit.

```
Here you go, this is the absolute path:

/path/to/repo_root/frontend/src/lib/components/dashboard/OnboardingProfileStep.svelte
```

This did not end well, so I resorted to a separate applying model via the config:

```
{
  "mergeBehavior": "overwrite",
  "models": [
    {
      "title": "DEV Go+Svelte repo",
      "provider": "ollama",
      "model": "dev-gosvelte",
      "contextLength": 49152,
      "defaultCompletionOptions": {
        "think": false
      },
      "roles": ["chat"]
    },
    {
      "title": "PM Go+Svelte repo",
      "provider": "ollama",
      "model": "pm-gosvelte",
      "contextLength": 49152,
      "defaultCompletionOptions": {
        "think": false
      },
      "roles": ["chat"]
    },
    {
      "title": "Gemma 4 (31B) repo",
      "provider": "ollama",
      "model": "gemma4:31b",
      "contextLength": 49152,
      "defaultCompletionOptions": {
        "think": false
      },
      "roles": ["chat"]
    },
    {
      "title": "qwen3:32b repo",
      "provider": "ollama",
      "model": "qwen3:32b",
      "roles": ["chat"]
    },
    {
      "title": "Qwen2.5-Coder 7B (Apply)",
      "provider": "ollama",
      "model": "qwen2.5-coder:7b",
      "roles": ["edit", "apply"]
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen2.5-Coder (7B) repo",
    "provider": "ollama",
    "model": "qwen2.5-coder:7b"
  },
  "embeddingsProvider": {
    "provider": "ollama",
    "model": "qwen3-embedding-4b"
  }
}
```

Workflow was this:

1. Use larger model to plan
2. Use smaller model to apply changes

Model was unable to locate the file independently, so I gave the absolute path as context. Somehow the Continue.dev plugin has lost it's capability to edit the files directly, so I resorted to using the models directly in the VSC's native AI chat-interface.

## 14.5.2026

The change to VSC's native AI-chat interface did wonders and the local model did a simple linter fix for one file in under a minute. So naturally the next test was to test it on 2 linter errors simultaniously, giving the context in a prompt as the error messages (emulating developer workflow):

```
/app/src/lib/components/dashboard/OnboardingProfileStep.svelte
  55:6  error  'calendar_capacity_scope' in 'profile' is an unused property  svelte/no-unused-props

/app/src/lib/components/dashboard/StorefrontControls.svelte
  15:6  error  Prefer using writable $derived instead of $state and $effect  svelte/prefer-writable-derived

✖ 2 problems (2 errors, 0 warnings)
```

Also turned off device connection to internet to be sure we're running on local inference compute, since that's one the key benefits of local models - your data is your data SOURCE HERE.

This worked better than Continue.dev plugin, but it still did not have success with the paths in a strange way, since it was able to locate 1 of the files correctly, but not the other one. So maybe we do need absolute paths for simple linter fixes? I tried the same prompt again to see if there would be a difference in outcome, as models are not deterministic SOURCE HERE.

I was positively surprised when it worked perfectly this time around, and the linter issues were fixed.

```
The linting issues have been resolved:

Unused Property
Removed calendar_capacity_scope from the OnboardingProfile type in OnboardingProfileStep.svelte with a comment explaining the change.

Svelte Best Practice
Replaced the $state + $effect pattern with $derived for liveStorefrontEnabled in StorefrontControls.svelte, improving reactivity and code clarity.

Both changes follow Svelte 5 best practices and address the reported errors.
```

The changes the model made to the files were minimal and correct, so this was a success and something that could actually provide value, since this could be left running on the background while doing other tasks or taking a break and fix mundane issues.

### 15.5.2026

A more complex piece of work was to fix some end-to-end tests. The demonstration project has 1 failing tests, so that's a perfect candidate for the model to handle. Prompt was given as the error message:

```
1) e2e/customer-journey.e2e.ts:124:2 › Customer Journey › full order flow: storefront → order form → submit → proposal → checkout › navigate to proposal and see quote breakdown

    Error: expect(locator).toBeVisible() failed

    Locator: getByRole('heading', { name: /Proposal Details/i })
    Expected: visible
    Timeout: 10000ms
    Error: element(s) not found

    Call log:
      - Expect "toBeVisible" with timeout 10000ms
      - waiting for getByRole('heading', { name: /Proposal Details/i })


      312 |                     await page.goto(`/proposal/${proposalToken}`);
      313 |
    > 314 |                     await expect(page.getByRole('heading', { name: /Proposal Details/i })).toBeVisible();
          |                                                                                            ^
      315 |
      316 |                     // Quote items visible
      317 |                     await expect(page.getByText('Celebration Cake')).toBeVisible();
        at /app/e2e/customer-journey.e2e.ts:314:75
        at /app/e2e/customer-journey.e2e.ts:311:3

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/e2e-customer-journey.e2e.t-86ad9-ubmit-→-proposal-→-checkout/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/e2e-customer-journey.e2e.t-86ad9-ubmit-→-proposal-→-checkout/error-context.md

    Retry #1 ───────────────────────────────────────────────────────────────────────────────────────

    Error: expect(locator).toBeVisible() failed

    Locator: getByRole('heading', { name: /Proposal Details/i })
    Expected: visible
    Timeout: 10000ms
    Error: element(s) not found

    Call log:
      - Expect "toBeVisible" with timeout 10000ms
      - waiting for getByRole('heading', { name: /Proposal Details/i })


      312 |                     await page.goto(`/proposal/${proposalToken}`);
      313 |
    > 314 |                     await expect(page.getByRole('heading', { name: /Proposal Details/i })).toBeVisible();
          |                                                                                            ^
      315 |
      316 |                     // Quote items visible
      317 |                     await expect(page.getByText('Celebration Cake')).toBeVisible();
        at /app/e2e/customer-journey.e2e.ts:314:75
        at /app/e2e/customer-journey.e2e.ts:311:3

    attachment #1: screenshot (image/png) ──────────────────────────────────────────────────────────
    test-results/e2e-customer-journey.e2e.t-86ad9-ubmit-→-proposal-→-checkout-retry1/test-failed-1.png
    ────────────────────────────────────────────────────────────────────────────────────────────────

    Error Context: test-results/e2e-customer-journey.e2e.t-86ad9-ubmit-→-proposal-→-checkout-retry1/error-context.md

    attachment #3: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/e2e-customer-journey.e2e.t-86ad9-ubmit-→-proposal-→-checkout-retry1/trace.zip
    Usage:

        npx playwright show-trace test-results/e2e-customer-journey.e2e.t-86ad9-ubmit-→-proposal-→-checkout-retry1/trace.zip

    ────────────────────────────────────────────────────────────────────────────────────────────────

  1 failed
    e2e/customer-journey.e2e.ts:124:2 › Customer Journey › full order flow: storefront → order form → submit → proposal → checkout
```

So instead of a simple failing linter, there's actually the task of fixing the failing test, or updating logic for the UI.

The model proposed a fix that would introduce a timeout for the test. The test still failed, so then I made a comparison with a frontier model (Gemini 3.1 Pro). The frontier model did the fix correctly on the 1st try.

I wanted to see if a local model could fix the test on a second try. To my surprise, the local model did handle the fix.

### 17.5.2026

Next up was upping the stakes in a new feature implementation. The ROADMAP.md file was given as a context, and a prompt asked to start implementating the SEO-strategy.

```
Make a plan for the - [ ] **SEO** — meta tags, Open Graph for baker profile pages roadmap task. We should start with the meta-tags.
```

Local model did return a plan:

```
Plan: Implement SEO Meta Tags for Baker Profile Pages
TL;DR - Add dynamic meta tags to baker profile routes using SvelteKit's <meta> directives and load functions. Prioritize title/description tags first, then expand to Open Graph later.

Steps

Identify baker profile routes

Check src/routes/baker/[slug]/+page.svelte (primary candidate)
Verify if src/routes/baker/+layout.svelte already contains shared meta configurations
Audit existing meta tag patterns

Search for <meta> tags or use:page directives in:
src/routes/baker/**/*.{svelte,js,ts}
src/app.html (SvelteKit's root HTML template)
Implement dynamic meta tags (depends on step 1-2)

In the identified route/component:
Use export let data to receive baker profile data from +page.js/ts load function
Add dynamic <meta name="description" content={data.baker.bio} />
Set dynamic <title>{data.baker.name} | CakeMate</title>
Validate data flow (depends on step 3)

Confirm +page.ts load function returns baker object with required fields
Add fallback values for missing data (e.g. data.baker.bio || 'Custom default description')

Relevant files

src/routes/baker/[slug]/+page.svelte — Likely primary implementation target
src/routes/baker/[slug]/+page.ts — Data loading logic for dynamic baker profiles
src/app.html — Root template for global meta configurations (if any)
Verification

Check rendered HTML output for:
Dynamic <title> matching baker name
Unique <meta name="description"> per profile
Run npm run dev and manually test:
Visit /baker/example-slug
View page source to confirm meta tags are injected
Use Screaming Frog to crawl local dev server and verify meta tag uniqueness
Decisions

Focus first on HTML meta tags (title/description) before Open Graph
Use SvelteKit's built-in <meta> component instead of third-party libraries
Exclude from src/routes/baker/+layout.svelte to avoid polluting shared layouts
Further Considerations

Should we add canonical URLs to avoid duplicate content?
Option A: Add <link rel="canonical" href={data.baker.canonicalUrl}>
Option B: Defer until multi-language support (Phase 11)
Would you like to proceed with this plan or refine any specific aspects?
```

### 18.5.2026

The locally run model did sort of succeed in adding some fields to meta-tags, but failed to understand how the pages are generated. So this is something that can be used for smaller user stories too, where the changes needed are well known problems and not something that requires extensive understanding of the codebase.

### 19.5.20226

The next logical test was a comparison for the frontier model with the same prompt, and the results were similar to the local model. It did not succeed in understanding the page generation and did not one-shot the new feature. This meant that the prompt was too vague and neither model could produce the desired outcome.

The next test was to try and fix an UI bug, that does not allow for new product creation. The only clue we have is a phantom function call in the UI, and no further tips for the model. This kind of bug is useally quite easy to fix for a developer, as a you can do it by following the signal path. Somewhere along the path, when user click a button for new product creation, a missing function call is made and that somehow results in a failure.

The prompt used (Agent mode with local LLM):

```
Diagnose bug when user clicks 'Create Product':

$.get(...).trim is not a function
```

Local model was not able to solve the bug in a one shot. As a control I tried to solve it manually, and that took me 5 minutes to solve. My strategy was to basically remove trim-functions for the problematic input, since it did not serve any sane purpose. Then I gave my insigths to the local model and spoon fed a bit the way to solve for this to see if it could manage it.

```
Diagnose bug when user clicks 'Create Product' on the product modal:

$.get(...).trim is not a function

You should see the signal path from the button click in the file to the saving.
```

### 26.5.2026

Local model was not able to successfully fix the bug, even with some extra hints. The task took 30 minutes to produce the faulty response. The next step was to try out a frontier model for the same task as a comparative benchmark run.

The same prompt was given to Gemini 3.1 Pro. The frontier model one-shotted the task and produced a valid response in a matter of minutes.

The model's response is telling:

```
I have diagnosed the bug where $.get(...).trim is not a function when the user clicks 'Create Product'.

The bug:
Svelte 5 reactivity logic (via $state) with <input type="number"> elements passes parsed values as numbers to their bound variable (i.e. display_price and weightGramsInput), instead of maintaining them as strings. Consequently, when typeof variable === 'number' and the user clicks 'Create Product', trying to call the .trim() function from that number throws an error: ...trim is not a function.

The fix:
I updated display_price, weightGramsInput and variant.price_display string evaluation inside handleSubmit to convert them into a string when checking with .trim(). Now it parses the display price input without causing any type mutation accordingly without any issue when submitting.
```

The model realized that there was a type mismatch, as suggested by our comparison fix by the developer.

Next I decided to try the fix on a local Nemotron model, as it's supposed to be better with vague prompts SOURCE HERE that developers do use, since humans tend to fill in the blanks SOURCE HERE. Nemotron received the same input prompt and produced a malformed response:

```
Sorry, your request failed. Please try again.

Copilot Request id: c7df45c4-3b08-4eb9-a0cd-40a3195fa7ed

Reason: Response contained no choices.: Error: Response contained no choices. at Jj._provideLanguageModelResponse (/Applications/Visual Studio Code.app/Contents/Resources/app/extensions/copilot/dist/extension.js:1709:15836) at process.processTicksAndRejections (node:internal/process/task_queues:103:5) at async Jj.provideLanguageModelResponse (/Applications/Visual Studio Code.app/Contents/Resources/app/extensions/copilot/dist/extension.js:1709:16839)
```

This told that the output was not something that Visual Studio Code's Agent functionality was expecting, so that made the Nemotron-model unusable for this use case SOURCE HERE.

Then, just to see if the customizations made by the ollama with the modelfile where actually hurting the performance characteristics of the model, I ran the same prompt on a barebones version of the Qwen 3 32 billion parameter model.

### 27.5.2026

The Qwen 3 non-customized version did not one shot the fix, but it not fare worse than the customized version. One thing to note was that the Visual Studio Code's Agent panel functionality does support context compression for locally run models too, and it does do it automatically SOURCE HERE. That is useful, since the context size is quite limited, as the memory at hand on a laptop is quite limited. Unfortunately for the usefulness for the lazy developer, the non-customized model wasn't able to fix the simple type issue with the level of prompting the frontier model just breezes trough. 

After these, frankly disapointing results, I asked a frontier model on how to improve the results from using a locally run LLM. The model's answer was not helping:

```
100% Local Model Agentic Workflow
A fully private, local-only workflow leveraging a specialized PM model for scoping and a Dev model for single-file execution, avoiding complex RAG and multi-file confusion.

Steps

Local PM Scoping — Use the specialized local PM model (e.g., pm-gosvelte tuned Gemma 31B) to analyze requirements and determine the next action. Keep tracking files like ROADMAP.md completely DRY (no redundant summaries) to prevent local model hallucinations.
Context Isolation — Extract the precise error message, test failure, or scoped feature request. Avoid broad workspace RAG, as local models struggle with huge, noisy contexts.
Single-File Dev Execution — Feed the scoped task to the local developer model (e.g., dev-gosvelte tuned Qwen 32B). Crucially: always provide the absolute file path, and only request modifications for ONE file at a time.
Native Application — Use VS Code's native AI chat interface for code generations instead of complex multi-agent plugins, as the Diary confirms it has a higher single-shot success rate for applying local model edits cleanly.
No-Think Mode Enforcement — Ensure the underlying OLLAMA model config has <think> blocks suppressed (num_predict -1 and API completion settings) so the developer agent outputs pure, valid code without tangling reasoning into the source file.
```

That means that we're pretty much already doing a best effort for the task.

### 28.5.2026

I feel like we're running out of things to try to improve upon, and my conclusion is that locally run quantized LLM's do have their place and use, but they can not be used as a substitute for frontier models. Main limitations being the context size and long duration reasoning. 

### Key observations

The quality of the local model's work varies greatly. It's good enough on tightly scoped tasks, but fails on larger tasks. It still remains to be seen if local model can be quantisized to a point where they can compete with the larger models of today tomorrow. Probably a big part of that is extending the context via permanent memory with some sort a solution that will be available in the future. Currently my take is that local models can serve a purpose for small tasks, but do require an order of magnitude more babysitting than their commercial rivals. Having the models available in the Visual Studio Code Agents panel does reduce most of the friction of using some propriatry plugin, and it does actually seem to be working better than with the Continue.dev-tool that was used in this thesis as a comparison. The key benefit for developers is that the Agent-panel is readily available and something that developers are well accustomed to using. The switching and experimenting costs with different models and bolting on future models is thus quite negligible.
