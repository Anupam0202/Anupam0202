<!--
  Profile README for github.com/Anupam0202
  The images in assets/ and CERTIFICATIONS.md are generated: edit data/profile.toml,
  then run `python3 scripts/build.py`. See SETUP.md.
-->

<a href="https://anupam-roy.vercel.app/">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/hero-light.svg">
  <img alt="Anupam Roy, AI/ML Analyst at Accenture in Kolkata, India. I build AI systems that prove their work: multi-agent GenAI platforms, cite-or-abstain retrieval and guarded automation. In production since 2022: about 20% faster turnaround, about 50% less SME dependency, 74 certifications." src="./assets/hero-light.svg" width="100%">
</picture>
</a>

<p align="center">
  <a href="https://anupam-roy.vercel.app/"><img alt="Portfolio" src="./assets/buttons/portfolio.svg" height="40"></a>
  <a href="https://www.linkedin.com/in/anupam--roy/"><img alt="LinkedIn" src="./assets/buttons/linkedin.svg" height="40"></a>
  <a href="mailto:anupam020202@gmail.com"><img alt="Email" src="./assets/buttons/email.svg" height="40"></a>
  <a href="https://www.credly.com/users/anupam_roy/"><img alt="Credly" src="./assets/buttons/credly.svg" height="40"></a>
  <a href="https://www.codechef.com/users/anupam_roy"><img alt="CodeChef" src="./assets/buttons/codechef.svg" height="40"></a>
</p>

<p align="center">
  <a href="#how-i-build"><b>How I build</b></a> ·
  <a href="#experience"><b>Experience</b></a> ·
  <a href="#proof-of-work"><b>Proof of work</b></a> ·
  <a href="#wall-of-mastery"><b>Wall of Mastery</b></a> ·
  <a href="#recognition"><b>Recognition</b></a> ·
  <a href="#stack"><b>Stack</b></a> ·
  <a href="#education"><b>Education</b></a>
</p>

I'm an AI/ML engineer at **Accenture** who builds production AI that **shows its evidence or says it doesn't know**. At work, that is a multi-agent GenAI platform running incident, problem, release and service-request operations. In public, it is a set of builds where models cite, verify and fail closed. Every claim on this page links to something you can check.

## How I build

Six rules that run through everything I ship, each with a repository you can audit.

<table>
<tr>
<td width="50%" valign="top">

**`01` Cite or abstain**<br>
An answer ships only when every claim resolves to a retrieved source. No source, no answer.<br>
<sub>Proof → <a href="https://github.com/Anupam0202/NexusRAG">NexusRAG</a></sub>

</td>
<td width="50%" valign="top">

**`02` Deterministic before AI**<br>
Exact rules make the safety-critical call. Models extract and propose; they never decide.<br>
<sub>Proof → <a href="https://github.com/Anupam0202/food-bank-recall-closure-agent">Recall Closure Agent</a> · <a href="https://github.com/Anupam0202/pantryproof">PantryProof</a></sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

**`03` Models propose, people approve**<br>
Agents get typed, allowlisted tools and stop at a human checkpoint before anything irreversible.<br>
<sub>Proof → <a href="https://github.com/Anupam0202/cutline">CUTLINE</a> · <a href="https://github.com/Anupam0202/raceproof">RaceProof</a></sub>

</td>
<td width="50%" valign="top">

**`04` Approvals expire with the evidence**<br>
A review is fingerprinted to the exact revision it approved. Change the text, and the approval goes stale.<br>
<sub>Proof → <a href="https://github.com/Anupam0202/cutline">CUTLINE</a> · <a href="https://github.com/Anupam0202/recordcheck">RecordCheck</a></sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

**`05` Attack it before users do**<br>
Red-team every guardrail, then measure the utility it costs. Safety that breaks the product is not safety.<br>
<sub>Proof → <a href="https://github.com/Anupam0202/boxshield-arena">BoxShield Arena</a></sub>

</td>
<td width="50%" valign="top">

**`06` Budget every model call**<br>
Quotas, cooldowns and bounded retries keep AI cost predictable, and fail closed when they run out.<br>
<sub>Proof → <a href="https://github.com/Anupam0202/ahawin">AhaWin</a> · <a href="https://github.com/Anupam0202/NexusRAG">NexusRAG</a></sub>

</td>
</tr>
</table>

## Experience

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/timeline-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/timeline-light.svg">
  <img alt="Career timeline: Class X in 2016, Class XII (Science) in 2018, B.Tech in Computer Science 2018 to 2022 with GPA 9.14, Associate Software Engineer at Accenture from August 2022, AI/ML Analyst at Accenture from December 2023 (current), Credly Top Badge Earner 2024, 74 certifications and 18 public builds by 2026." src="./assets/timeline-light.svg" width="100%">
</picture>

### AI/ML Analyst · Accenture · Dec 2023 – Present

**Built an enterprise AI operational assistant:** a production multi-agent GenAI platform that took SME-heavy production support, incident, testing and release work and handed it to specialist AI agents.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/experience-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/experience-light.svg">
  <img alt="System map of the Enterprise AI Operational Assistant. Signals from Jira, Confluence, SharePoint, GitHub, Splunk and databases flow through a chat interface and a LangGraph routing layer into incident, problem, release and service-request agents, backed by RAG knowledge, an RCA engine, an SQL analyst and a test generator. Outputs are resolution steps, test suites, release packs, ServiceNow tickets, SQL fixes and SOX reports. Impact: about 20% faster turnaround and about 50% less SME dependency." src="./assets/experience-light.svg" width="100%">
</picture>

- **Multi-agent orchestration.** Designed LangGraph workflows with incident, problem, release and service-request agents, routed dynamically by user intent and semantic retrieval.
- **Enterprise RAG.** Built indexing and retrieval pipelines over Jira, Confluence, SharePoint, GitHub, Splunk logs and databases, covering tickets, logs, documents and SQL.
- **Real-time root-cause analysis.** Correlates logs with historical incidents and writes context-grounded resolution steps: **≈20% faster turnaround** and **≈50% less SME dependency**.
- **AI test generation.** Turns design documents and existing frameworks into functional test cases and **Selenium, UFT and Karate** scripts.
- **Release intelligence.** Reads GitHub commits, Confluence and Jira to draft release notes, deployment plans and rollback strategies.
- **Operations automation.** Chat-to-ServiceNow ticket creation, docs-to-SQL analysis that pinpoints impacted tables, anomaly detection and audit-ready **SOX** reporting, all behind one context-aware chat backed by MongoDB.

<sub><b>Stack:</b> Python · LangGraph · LangChain · RAG · vector search · MongoDB · PostgreSQL · Databricks · Jira · ServiceNow · Confluence · SharePoint · Splunk · Selenium · UFT · Karate</sub>

### Associate Software Engineer · Accenture · Aug 2022 – Nov 2023

- Built and deployed **Spring Boot / Core Java** microservices with scalable REST APIs for insurance workflows.
- Designed event-driven serverless components on **AWS Lambda**, cutting infrastructure overhead.
- Automated build, test and deploy with **CI/CD pipelines on AWS CodeBuild**, removing manual release effort.
- Raised reliability with **JUnit** unit and integration tests, and caught vulnerabilities early with **SonarQube** and **SourceClear** gates.
- Delivered in Agile Scrum and wrote the automation scripts behind a DevOps-first team.

## Proof of work

18 public builds. The newest share one idea: **models propose; deterministic code and people decide.** Test counts are read from each repository; the Proof Atlas suite was run and passed for its release.

### Flagships

<a href="https://github.com/Anupam0202/NexusRAG">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/projects/nexusrag-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/projects/nexusrag-light.svg">
  <img alt="NexusRAG: cite-or-abstain document research on a tenant-scoped edge runtime. Next.js 16 on Cloudflare, a tenant-scoped gateway, Supabase, Qdrant vectors fenced by workspace, quota-gated Gemini, and a citation gate that publishes an answer only when every claim cites a retrieved source. 465 tests in 72 files, 5 CI workflows, MIT licence." src="./assets/projects/nexusrag-light.svg" width="100%">
</picture>
</a>

<a href="https://anupam-roy.vercel.app/">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/projects/proof-atlas-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/projects/proof-atlas-light.svg">
  <img alt="Proof Atlas: a portfolio where every claim links to evidence and its AI must cite it. Astro 7 with React islands, hashed CSP, an Express 5 API on Vercel functions, an egress guard, Ask the Atlas and an evidence ledger. 371 unit and API tests, 1,791 Playwright end-to-end tests, 430 production smoke checks, and mobile Lighthouse accessibility and SEO scores of 0.95 or better." src="./assets/projects/proof-atlas-light.svg" width="100%">
</picture>
</a>

<p align="center">
  <a href="https://github.com/Anupam0202/NexusRAG"><b>NexusRAG source</b></a> ·
  <a href="https://anupam-roy.vercel.app/"><b>Proof Atlas live</b></a> ·
  <a href="https://github.com/Anupam0202/Anupam_Roy"><b>Proof Atlas source</b></a>
</p>

### Agents with guardrails

<p align="center">
<a href="https://github.com/Anupam0202/cutline"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projects/cutline-dark.svg"><img alt="CUTLINE: fact-check approvals that expire the moment the script changes. SHA-256 fingerprints bind each review to its cue, evidence and edit. 30 tests, Cloud Run, MIT." src="./assets/projects/cutline-light.svg" width="49%"></picture></a>
<a href="https://github.com/Anupam0202/food-bank-recall-closure-agent"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projects/food-bank-recall-dark.svg"><img alt="Food-Bank Recall Closure Agent: from a recall notice to verified closure across every partner pantry. Exact UPC and lot matching before any AI, an ADK coordinator limited to eight allowlisted tools. 92 tests, Cloud Run with Pub/Sub, MIT." src="./assets/projects/food-bank-recall-light.svg" width="49%"></picture></a>
</p>
<p align="center">
<a href="https://github.com/Anupam0202/raceproof"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projects/raceproof-dark.svg"><img alt="RaceProof: turns a flaky JVM concurrency bug into a replayable, minimized, verified repair with a human checkpoint. 48 tests plus a Java harness, MIT." src="./assets/projects/raceproof-light.svg" width="49%"></picture></a>
<a href="https://github.com/Anupam0202/boxshield-arena"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projects/boxshield-arena-dark.svg"><img alt="BoxShield Arena: red-teams AI agents and measures what each guardrail costs. Recorded replay: safety 26 to 89 with utility 100 to 80. 60 TestBox tests, Apache-2.0." src="./assets/projects/boxshield-arena-light.svg" width="49%"></picture></a>
</p>

### Evidence-first products

<p align="center">
<a href="https://github.com/Anupam0202/pantryproof"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projects/pantryproof-dark.svg"><img alt="PantryProof: proves a food recall is closed everywhere, with a server-gated closure PDF and a SHA-256 evidence manifest. 26 tests, Vercel." src="./assets/projects/pantryproof-light.svg" width="49%"></picture></a>
<a href="https://github.com/Anupam0202/ahawin"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projects/ahawin-dark.svg"><img alt="AhaWin: a STEM reflection coach that refuses to invent a misconception. At most two validated Gemini attempts and fail-closed cost quotas. 108 tests, Vercel, MIT." src="./assets/projects/ahawin-light.svg" width="49%"></picture></a>
</p>
<p align="center">
<a href="https://github.com/Anupam0202/PlantPal"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projects/plantpal-dark.svg"><img alt="PlantPal: hyperlocal planting advice from five open environmental data sources, a CMIP6 climate projection and Gemini photo review. React 19 and Vite." src="./assets/projects/plantpal-light.svg" width="49%"></picture></a>
<a href="https://github.com/Anupam0202/mavunoguard-ai"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projects/mavunoguard-dark.svg"><img alt="MavunoGuard AI: a maize-grain photo becomes an explainable, bilingual post-harvest risk plan. Zero runtime dependencies, English and Kiswahili, MIT." src="./assets/projects/mavunoguard-light.svg" width="49%"></picture></a>
</p>

<p align="center"><sub>PantryProof also runs at <a href="https://pantryproof.vercel.app">pantryproof.vercel.app</a>.</sub></p>

### Retrieval lab and earlier work

| Project | What it shows | Links |
| --- | --- | --- |
| **RAG** | Gemini + LangChain + Streamlit Q&A over 7 file types; FAISS + BM25 hybrid search, chat memory, Markdown export | [Live demo](https://rag-with-langchain.streamlit.app/) · [Source](https://github.com/Anupam0202/RAG) |
| **Contextual RAG Chatbot** | PDF Q&A with Tesseract OCR fallback, tunable dense + sparse fusion, a 1–20 message context window and analytics export | [Live demo](https://contextual-rag-chatbot.streamlit.app/) · [Source](https://github.com/Anupam0202/Contextual-RAG-Chatbot) |
| **RecordCheck** | Local-only claim-versus-source review that binds sign-off to the exact revision checked; one HTML file, 43 tests | [Source](https://github.com/Anupam0202/recordcheck) |
| **Handwritten Chemical Compound Detection** | TensorFlow Object Detection (SSD EfficientDet-D0) trained on 30 hand-drawn compound classes | [Notebook](https://github.com/Anupam0202/Handwritten-Chemical_Compound-Detection/blob/main/object_detection_tutorial.ipynb) · [Source](https://github.com/Anupam0202/Handwritten-Chemical_Compound-Detection) |

<details>
<summary><b>Where it started: 2022 frontend builds</b></summary>
<br>

| Project | Stack | Links |
| --- | --- | --- |
| **My Portfolio** | Next.js 10 · React 17 · styled-components | [Live](https://portfolioanupamroy.netlify.app/) · [Source](https://github.com/Anupam0202/My-Portfolio) |
| **Anupam Portfolio** | React 17 · Create React App | [Live](https://anupamroyportfolio.netlify.app/) · [Source](https://github.com/Anupam0202/Anupam-Portfolio) |
| **Real Estate** | Next.js 11 · Chakra UI · Bayut listings API | [Live](https://real-estate-tau-ten.vercel.app/) · [Source](https://github.com/Anupam0202/Real-Estate) |
| **Modern UI/UX GPT-3** | React 17 · BEM CSS · flexbox and grid | [Live](https://anupam0202.github.io/Modern_UI-UX_GPT3/) · [Source](https://github.com/Anupam0202/Modern_UI-UX_GPT3) |

</details>

## Wall of Mastery

<a href="./CERTIFICATIONS.md">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/mastery-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/mastery-light.svg">
  <img alt="The Periodic Table of Mastery: 74 credentials laid out like chemical elements, from fundamentals (lightest) to expert (heaviest). Microsoft 45, Google Cloud 14, Snowflake 7, AWS 3, Databricks 2, Anthropic 1, MongoDB 1. 11 fundamentals, 39 associate, 4 specialty, 14 professional and 5 expert credentials; number 74 is awaiting its public link." src="./assets/mastery-light.svg" width="100%">
</picture>
</a>

<p align="center"><b>74 credentials · 7 ecosystems · 5 expert · 14 professional · all issuer-verifiable</b></p>

The table is ordered like the real one: **light elements are fundamentals, heavy ones are expert-level.** Element 1 is AZ-900; elements 69 to 73 are five Microsoft Expert certifications, ending with AZ-305. Tap any signature credential below to verify it now.

<p align="center">
<a href="https://www.credly.com/badges/abba82dd-73e2-46b7-967c-2ddbbfe40126/public_url"><img alt="Verify: AWS Certified Machine Learning Engineer – Associate" src="./assets/vault/signature/aws-mla.svg" width="49%"></a>
<a href="https://verify.skilljar.com/c/v3bg7pbc87fn"><img alt="Verify: Claude Certified Architect – Foundations (Anthropic)" src="./assets/vault/signature/claude-architect.svg" width="49%"></a>
<a href="https://credentials.databricks.com/65e9a608-48dd-43e8-8f63-134231a861a3"><img alt="Verify: Databricks Certified Generative AI Engineer Associate" src="./assets/vault/signature/databricks-genai.svg" width="49%"></a>
<a href="https://learn.microsoft.com/api/credentials/share/en-us/RoyAnupam-9387/B62389D156A906D1?sharingId=87E510F2D20A449"><img alt="Verify: Microsoft Azure AI Engineer Associate" src="./assets/vault/signature/ai-102.svg" width="49%"></a>
<a href="https://achieve.snowflake.com/aec2a575-7ec6-4c11-8a46-b064fd0a7c10"><img alt="Verify: SnowPro Specialty: Gen AI" src="./assets/vault/signature/snowpro-genai.svg" width="49%"></a>
<a href="https://www.credly.com/badges/f486243e-ddce-4a98-bb96-20a7b54f9f1b/public_url"><img alt="Verify: Google Cloud Professional Cloud Architect" src="./assets/vault/signature/gcp-pca.svg" width="49%"></a>
<a href="https://www.credly.com/badges/877f3676-e647-4df5-8845-f566ea7f0c1e/public_url"><img alt="Verify: Google Cloud Professional Machine Learning Engineer" src="./assets/vault/signature/gcp-pmle.svg" width="49%"></a>
<a href="https://learn.microsoft.com/api/credentials/share/en-us/RoyAnupam-9387/B178CAC5C8FCAD0C?sharingId=87E510F2D20A449"><img alt="Verify: Microsoft Azure Solutions Architect Expert" src="./assets/vault/signature/az-305.svg" width="49%"></a>
</p>

<h3 align="center"><a href="./CERTIFICATIONS.md">Open the verification vault: all 74, one tap each →</a></h3>

## Recognition

<p align="center">
<a href="https://www.credly.com/badges/3d899907-7a72-4cac-80d0-c7f80d9a892c/public_url"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/achievements/credly-top-dark.svg"><img alt="Credly Top Badge Earner 2024. Verify the badge." src="./assets/achievements/credly-top-light.svg" width="49%"></picture></a>
<a href="https://www.credly.com/users/anupam_roy/"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/achievements/badges-dark.svg"><img alt="180+ digital badges on Credly across cloud, AI, data and security. Browse the collection." src="./assets/achievements/badges-light.svg" width="49%"></picture></a>
<a href="https://www.linkedin.com/posts/anupam--roy_googlecloud-gcp-learninganddevelopment-activity-7385948527765639168-SuDJ"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/achievements/gcp-legend-dark.svg"><img alt="Google Cloud Arcade Legend: four straight seasons, all three Technical Expert badges, Early Adopter. Read the story." src="./assets/achievements/gcp-legend-light.svg" width="49%"></picture></a>
<a href="https://www.codechef.com/users/anupam_roy"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/achievements/codechef-dark.svg"><img alt="CodeChef 5 star, rated 2109. See the profile." src="./assets/achievements/codechef-light.svg" width="49%"></picture></a>
</p>

<p align="center"><sub>The three Google Cloud Technical Expert badges (Customer Engagement Suite with Google AI, Intelligent Search, Build with Vertex AI) came with Early Adopter recognition: <a href="https://www.linkedin.com/posts/anupam--roy_googlecloud-vertexai-accenture-activity-7367557930969182210-Goq9">read the post</a>.</sub></p>

## Stack

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/stack-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/stack-light.svg">
  <img alt="Technology stack, tagged by where each tool was used. In production at Accenture: LangGraph, LangChain, RAG pipelines, vector search, prompt engineering, Python, Core Java, Spring Boot, REST microservices, MongoDB, PostgreSQL, Databricks, SQL generation, AWS Lambda, AWS CodeBuild, a chat-based assistant UI, CI/CD, JUnit, SonarQube, Selenium, UFT, Karate, Jira, ServiceNow, Confluence, SharePoint, Splunk and GitHub. In public repositories: Gemini API, Vertex AI, Google ADK, Qdrant, FAISS and BM25, cross-encoders, TensorFlow, FastAPI, Node.js, Express, WebSockets, Supabase, Firestore, Upstash Redis, Cloud Run, Pub/Sub, Cloudflare Workers, Vercel, Docker, React, Next.js, TypeScript, Astro, Tailwind, Streamlit, GitHub Actions, Playwright, Vitest and gitleaks." src="./assets/stack-light.svg" width="100%">
</picture>

<sub>Cloud certifications cover AWS, Google Cloud and Azure architecture in depth. See the <a href="#wall-of-mastery">Wall of Mastery</a>.</sub>

## Education

**B.Tech, Computer Science & Engineering**: Maulana Abul Kalam Azad University of Technology, West Bengal · 2018–2022 · **GPA 9.14 / 10**

<sub>Data Structures & Algorithms · Operating Systems · Database Management Systems · Computer Networks · Machine Learning · Software Engineering · Distributed Systems</sub>

<details>
<summary><b>School</b></summary>
<br>

- **Class XII, Science** (Physics, Chemistry, Mathematics, Computer Science): Basirhat Town High School, WBCHSE · 2018 · 73%
- **Class X**: Itinda Union High School, WBBSE · 2016 · 84%

</details>

## Off the clock

Chess · cricket · BGMI `5187468970` · Clash of Clans `#92J9PUUYU` · practical problem-solving. Challenges welcome.

<br>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/footer-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/footer-light.svg">
  <img alt="Let's build AI that proves its work. Agentic AI, retrieval quality, cloud architecture and evidence-first products." src="./assets/footer-light.svg" width="100%">
</picture>

<p align="center">
  <a href="mailto:anupam020202@gmail.com"><b>anupam020202@gmail.com</b></a> ·
  <a href="https://anupam-roy.vercel.app/"><b>anupam-roy.vercel.app</b></a> ·
  <a href="https://www.linkedin.com/in/anupam--roy/"><b>linkedin.com/in/anupam--roy</b></a>
</p>

<p align="center"><sub>Repository facts reflect each project as reviewed in October 2026. Visuals are generated from <a href="./data/profile.toml">one data file</a>.</sub></p>
