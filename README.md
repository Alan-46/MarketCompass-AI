# Market Compass: Hierarchical Multi-Agent Investment Orchestrator

[![Language: Python3](https://img.shields.io/badge/Language-Python3-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Framework: CrewAI](https://img.shields.io/badge/Framework-CrewAI-FF4B4B.svg)](https://crewai.com)
[![Observability: LangSmith](https://img.shields.io/badge/Observability-LangSmith-00C7B7.svg)](https://smith.langchain.com)
[![Package Manager: uv](https://img.shields.io/badge/Environment-uv-DE5D83.svg)](https://github.com/astral-sh/uv)
[![Serper](https://img.shields.io/badge/Serper-2563EB.svg)](https://serper.dev)

Market Compass is a practical, production-ready system designed to automate financial news analysis, deep industry research, and stock selection. Built on top of the CrewAI framework, the system uses a Hierarchical Process where a central manager agent coordinates several specialized analyst agents. It uses Pydantic to keep data formats strictly organized and consistent, and it sends out real-time trade signals through decoupled webhooks.

This project is built with solid backend engineering principles rather than basic scripting templates. It integrates native OpenTelemetry (OTel) tracking directly into LangSmith, resolves tricky cross-platform timezone bugs, and manages project dependencies cleanly and quickly using `uv`.

---

## 🚀 Key Real-World Applications

* **Automated Sector Screening & Trend Analysis**: The system monitors high-growth or fast-moving market areas (such as Banking, FinTech, or Energy) to track shifting macroeconomic trends and flag emerging companies.
* **Autonomous Market Intelligence Extraction**: It constantly scans live news sources, collects data feeds, and compiles detailed, professional-grade research reports on active market movers.
* **Real-Time Trade Alerts**: It evaluates financial entities, narrows them down to the single best option, and immediately sends out a trade alert via live push webhooks.
---

## 🏗️ System Architecture & Design

The work is split among specific, independent roles overseen by a supervisor engine to ensure everything stays organized, focused, and contained.

### 1. Agentic Roles & Collaboration Layout

* **Supervisor Manager Agent (`manager`)**: Acts as the main controller of the system. It checks the overall status, hands out context and inputs, assigns tasks to the other agents, and reviews the final work before finishing the run.
* **Financial News Analyst (`trending_company_finder`)**: Scans live, regional news updates to find 2 or 3 high-interest companies that are getting a lot of media attention in the selected sector.
* **Senior Financial Researcher (`financial_researcher`)**: Takes the list of target companies from the manager and does deep online research to build detailed financial profiles.
* **Equity Selection Specialist (`stock_picker`)**: Compares the research data qualitatively, picks the absolute best asset to invest in, writes a final markdown report, and triggers the external alert pipeline.

### 2. Structured Data Flow & Serialization

To make sure data doesn't break when passed between agents, we enforce strict structures using Pydantic models. Framework boundaries use schemas like `TrendingCompanyList` and `TrendingCompanyResearchList` to prevent parsing errors or missing data during handoffs.

### 3. Architecture Flowchart

```mermaid
graph LR
    User([User Input: Target Sector]) ==> Manager[Supervisor Manager Agent<br/>ollama/gemma4:31b-cloud]
    
    subgraph Orchestration ["Hierarchical Crew Orchestration"]
        Manager ==>|1. Delegate Trend Discovery| Analyst[Financial News Analyst<br/>trending_company_finder]
        Analyst ==>|Structured Company List| Manager
        
        Manager ==>|2. Delegate Deep Research| Researcher[Senior Financial Researcher<br/>financial_researcher]
        Researcher ==>|Comprehensive Dossiers| Manager
        
        Manager ==>|3. Delegate Selection| Picker[Equity Selection Specialist<br/>stock_picker]
    end
    
    subgraph Infrastructure ["Decoupled Infrastructure & Serialization"]
        Analyst -->|Live Scraping| Serper[Google Serper API Tool]
        Researcher -->|Data Retrieval| Serper
        Picker -->|Strict Contract Validation| Pydantic[Pydantic Models Serialization]
        Picker -->|Push Notification Webhook| Ntfy[ntfy.sh Notification Endpoint]
    end
    
    subgraph Observability ["Observability Tracing Layer"]
        Orchestration -.->|Telemetry Stream| OTel[OpenTelemetry Bridge]
        OTel -.->|Unified Inspection Traces| LangSmith[LangSmith Dashboard]
    end
    
    subgraph Outputs ["Local Storage Volume"]
        Picker ==>|Atomic I/O Write| Out[Structured Storage Artifacts<br/>- output/trending_companies.json<br/>- output/research_report.json<br/>- output/decision.md]
    end

    %% Style Rules for Recruiter Presentation
    classDef manager fill:#8B1E21,stroke:#111,stroke-width:2px,color:#fff;
    classDef agent fill:#2C3E50,stroke:#111,stroke-width:1px,color:#fff;
    classDef tool fill:#1E5631,stroke:#111,stroke-width:1px,color:#fff;
    classDef obs fill:#4A235A,stroke:#111,stroke-width:1px,color:#fff;
    classDef art fill:#424949,stroke:#111,stroke-width:1px,color:#fff;
    
    class Manager manager;
    class Analyst,Researcher,Picker agent;
    class Serper,Pydantic,Ntfy tool;
    class OTel,LangSmith obs;
    class Out art;
```

# 🛠️ Systems Engineering Challenges & Resolutions

Because this project focuses heavily on infrastructure stability and reliability, it directly solves several real-world production issues that standard tutorials usually ignore:

### 1. Missing Visibility in Multi-Agent Frameworks
* **The Challenge:** Frameworks like CrewAI run complex internal loops—such as agent thoughts, tool calls, and delegation steps—that remain completely hidden in standard application logs. This makes it incredibly difficult to debug runtime failures or track unexpected API token usage.
* **The Resolution:** I set up an OpenTelemetry (OTel) Bridge inside `crew.py`. By wrapping executions with an `OtelSpanProcessor` and initializing the `CrewAIInstrumentor`, every single token exchange, inner monologue, and tool execution hook is explicitly streamed into an external LangSmith Dashboard for easy monitoring and auditing.

### 2. Temporal Cloud Drift & Hallucination
* **The Challenge:** CCloud hosting environments (like Hugging Face Spaces containers) typically run on strict UTC system clocks. This can cause agents to guess incorrect dates or fail time-sensitive web lookups when evaluating live financial data. On top of that, local Windows development setups often lack native IANA time zone files, triggering a fatal `ZoneInfoNotFoundError`.
* **The Resolution:** I built a time-aware localization framework using Python’s built-in `zoneinfo` module. To make sure it works across all platforms without crashing, the official IANA database package (`tzdata`) is explicitly added directly to the managed runtime via `uv`. This lets the agents accurately calculate the correct local date thresholds before making live web searches.

### 3. Container Isolation & Output Exfiltration
* **The Challenge:** Standard containers isolate the filesystem, meaning any markdown or JSON file generated locally inside the workspace disappears as soon as the execution stops or the session resets.
* **The Resolution:** wrote a custom, asynchronous notification tool (`PushNotificationTool`) extending `crewai.tools.BaseTool`. It formats the final results and sends a live push notification payload directly to an external `ntfy.sh` server. This keeps data delivery completely real-time and cost-free, without needing complex mail servers or expensive cloud storage buckets.

---

# ⚙️ Installation & Setup

### Prerequisites
Ensure you have `uv` (the ultra-fast Python package and environment manager) installed on your system.

```bash
# Install uv if you haven't already
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
```

### 1. Clone & Synchronize Environment
Clone the project repository, navigate into the directory, and compile project dependencies automatically into an isolated virtual environment:

```bash
git clone [https://github.com/your-username/Market-Compass.git](https://github.com/your-username/Market-Compass.git)
cd Market-Compass
uv sync
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory of the project and add your infrastructure and API credentials:

```env
# LLM & Infrastructure Credentials
OPENAI_API_BASE="your-ollama-cloud-or-local-endpoint"
OPENAI_API_KEY="your-llm-access-token"

# Search Infrastructure
SERPER_API_KEY="your-serper-dev-search-key"

# Real-time Webhook Dissemination
NTFY_URL="[https://ntfy.sh/your_custom_secure_topic_id](https://ntfy.sh/your_custom_secure_topic_id)"

# LangSmith OpenTelemetry Observability
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_PROJECT="Market-Compass-Orchestration"
LANGCHAIN_API_KEY="your-langsmith-api-key"
```


### 3. Execute the Orchestration Loop
Run the multi-agent framework directly from your terminal:

```bash
uv run run_crew
```

The application will detect the localized runtime stamp we have specified in the code (e.g., `Asia/Kolkata`), pass your target sector parameters (again specified in the code) to the supervisor, and save the structured files directly to disk (`output/trending_companies.json`, `output/research_report.json`, and `output/decision`.md). At the same time, it will fire a mobile alert via your custom push notification web endpoint.

---

### 🚧 Roadmap & Work in Progress
* [ ] **User Interface (Gradio Web UI):** Developing a clear web frontend so users don't have to use the terminal to type options. This will allow you to input market sectors dynamically and view token logs side-by-side.
* [ ] **Docker Containerization & Cloud Hosting:** Building a multi-stage `Dockerfile` to host the backend on Hugging Face Spaces, including automated cloud-build hooks.
* [ ] **Cloud Databases for Long-Term Memory:** Moving data storage from local caching files to cloud databases (like MongoDB Atlas or Neon PostgreSQL), using automated data-retention scripts to manage session history safely.