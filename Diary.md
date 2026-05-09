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

````
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
````

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
What should we work on next from our  @ROADMAP.md?
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
