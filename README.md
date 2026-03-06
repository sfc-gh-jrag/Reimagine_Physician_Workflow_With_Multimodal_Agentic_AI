# PhysicianAssist — Snowflake Multimodal ML + Agentic AI Demo

An AI-powered clinical decision support application built entirely on Snowflake. A **Cortex Agent** orchestrates two tools — **Cortex Analyst** for text-to-SQL over patient data and **MedGemma 4B** (on SPCS) for medical image interpretation — giving physicians instant, governed access to structured clinical data and multimodal imaging insights without writing a line of SQL.

## Architecture

```
EHR App (React + Vite)
  │
  ▼ REST API (SSE Streaming)
Cortex Agent (claude-4-sonnet)
  ├── PATIENT_ANALYST        →  Cortex Analyst + Semantic View  →  6 Interactive Tables
  └── MEDGEMMA_INTERPRETER   →  Stored Procedure → SPCS (MedGemma 4B GPU)  →  Image Stage
```

See [`docs/architecture_diagram.html`](docs/architecture_diagram.html) for the full visual architecture.

## Project Structure

```
├── himss-physician-app/          # React + TypeScript + Tailwind (Vite)
│   ├── src/
│   │   ├── components/           # PatientSidebar, PatientDetailPanel, ChatPanel, ChatBubble
│   │   ├── hooks/                # useAgentChat (SSE streaming), usePatientData
│   │   └── types/                # TypeScript interfaces
│   └── public/images/dummy/      # Sample medical images (ECG, X-ray, Echo, etc.)
├── sql/
│   ├── setup_data.sql            # DDL for tables, data, MedGemma stored procedure
│   └── himss_patient_semantic_model.yaml  # Semantic View definition (6 tables, 17 VQRs)
├── docs/
│   ├── architecture_diagram.html # Visual architecture diagram
│   ├── key_highlights.html       # Key capabilities slide
│   └── HIMSS_DEMO_TALK_TRACKS.md # 3 guided demo talk tracks
└── README.md
```

## Snowflake Objects

| Object | Type | Purpose |
|--------|------|---------|
| `DEMO_DB.HIMSS_DEMO.PATIENTS_IT` | Interactive Table | Patient demographics |
| `DEMO_DB.HIMSS_DEMO.CONDITIONS_IT` | Interactive Table | Diagnoses & conditions |
| `DEMO_DB.HIMSS_DEMO.MEDICATIONS_IT` | Interactive Table | Prescriptions |
| `DEMO_DB.HIMSS_DEMO.VITALS_IT` | Interactive Table | Vital signs |
| `DEMO_DB.HIMSS_DEMO.ENCOUNTERS_IT` | Interactive Table | Visits & encounters |
| `DEMO_DB.HIMSS_DEMO.MEDICAL_IMAGES_IT` | Interactive Table | Image metadata |
| `DEMO_DB.HIMSS_DEMO.HIMSS_PATIENT_SEMANTIC_VIEW` | Semantic View | Text-to-SQL (17 verified queries) |
| `DEMO_DB.HIMSS_DEMO.MEDGEMMA_MEDICAL_INTERPRETER` | Stored Procedure | MedGemma 4B inference proxy |
| `SNOWFLAKE_INTELLIGENCE.AGENTS.HIMSS_PHYSICIAN_AGENT` | Cortex Agent | Orchestrator (claude-4-sonnet) |

## Prerequisites

- Snowflake account with Cortex Agent, Cortex Analyst, and SPCS enabled
- MedGemma 4B model deployed on SPCS (see `sql/setup_data.sql`)
- Node.js 18+
- Snowflake PAT token for authentication

## Setup

### 1. Snowflake Backend

Run the SQL setup to create the database objects, load sample patient data, and configure the semantic view:

```sql
-- Execute in Snowflake
-- 1. Run setup_data.sql to create tables, load data, and create the stored procedure
-- 2. Deploy the semantic view from the YAML
SELECT SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
  'DEMO_DB.HIMSS_DEMO',
  $$<contents of sql/himss_patient_semantic_model.yaml>$$
);
-- 3. Create the Cortex Agent via Snowsight UI or DDL
```

### 2. Frontend App

```bash
cd himss-physician-app
cp .env.example .env.local
# Edit .env.local — set your Snowflake PAT token and account
npm install
npm run dev
```

The app runs at `http://localhost:5173`. The Vite dev server proxies `/api` requests to your Snowflake account.

### 3. Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_SNOWFLAKE_PAT` | Snowflake PAT token for API authentication |
| `VITE_SNOWFLAKE_ACCOUNT` | Snowflake account identifier (e.g., `sfsenorthamerica-jrag`) |

## Key Capabilities

1. **Cortex Agent** — Native agentic AI that routes physician queries to the right tool
2. **MedGemma on SPCS** — Google's 4B vision-language model for ECG, X-ray, and echo interpretation
3. **Cortex Analyst** — Natural language to SQL over 6 clinical tables via semantic view
4. **Zero Data Movement** — Patient records and model inference stay within Snowflake
5. **Sub-Second Structured Data** — Interactive Tables with always-on warehouse
6. **Unified Platform** — Agent orchestration, text-to-SQL, and GPU inference on one platform

## Demo Talk Tracks

See [`docs/HIMSS_DEMO_TALK_TRACKS.md`](docs/HIMSS_DEMO_TALK_TRACKS.md) for three guided narratives:

1. **"The Critical Window"** — Acute STEMI, time-sensitive decision making
2. **"The Medication Detective"** — Drug interactions and clinical history analysis
3. **"The Multimodal Clinician"** — Combining structured data with medical image interpretation

## License

Internal demo — not for distribution.
