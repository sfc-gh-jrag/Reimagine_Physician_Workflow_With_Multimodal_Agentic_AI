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

## Project Structure

```
├── configure.py                  # One-command setup: rewrites all files for your DB/schema/account
├── himss-physician-app/          # React + TypeScript + Tailwind (Vite)
│   ├── src/
│   │   ├── components/           # PatientSidebar, PatientDetailPanel, ChatPanel, ChatBubble
│   │   ├── hooks/                # useAgentChat (SSE streaming), usePatientData
│   │   └── types/                # TypeScript interfaces
│   └── public/images/dummy/      # Sample medical images (ECG, X-ray, Echo, etc.)
├── sql/
│   ├── deploy_medgemma.sql       # Step 2: MedGemma deployment prerequisites (compute pool, EAI, secrets)
│   ├── setup_data.sql            # Step 3: DDL for tables, data, MedGemma stored procedure
│   └── himss_patient_semantic_model.yaml  # Semantic View definition (6 tables, 17 VQRs)
└── README.md
```

## Snowflake Objects

> Default database/schema: `DEMO_DB.HIMSS_DEMO` — configurable via `configure.py`

| Object | Type | Purpose |
|--------|------|---------|
| `<DB>.<SCHEMA>.PATIENTS_IT` | Interactive Table | Patient demographics |
| `<DB>.<SCHEMA>.CONDITIONS_IT` | Interactive Table | Diagnoses & conditions |
| `<DB>.<SCHEMA>.MEDICATIONS_IT` | Interactive Table | Prescriptions |
| `<DB>.<SCHEMA>.VITALS_IT` | Interactive Table | Vital signs |
| `<DB>.<SCHEMA>.ENCOUNTERS_IT` | Interactive Table | Visits & encounters |
| `<DB>.<SCHEMA>.MEDICAL_IMAGES_IT` | Interactive Table | Image metadata |
| `<DB>.<SCHEMA>.HIMSS_PATIENT_SEMANTIC_VIEW` | Semantic View | Text-to-SQL (17 verified queries) |
| `<DB>.<SCHEMA>.MEDGEMMA_MEDICAL_INTERPRETER` | Stored Procedure | MedGemma 4B inference proxy |
| `SNOWFLAKE_INTELLIGENCE.AGENTS.HIMSS_PHYSICIAN_AGENT` | Cortex Agent | Orchestrator (claude-4-sonnet) |

## Prerequisites

- Snowflake account (commercial AWS/Azure/GCP) with Cortex Agent, Cortex Analyst, and SPCS enabled
- Python 3.8+ (for the configure script)
- Node.js 18+
- A [Hugging Face account](https://huggingface.co/join) with access to [MedGemma 4B](https://huggingface.co/google/medgemma-4b-it) (accept the license)
- A Hugging Face access token ([generate here](https://huggingface.co/settings/tokens))
- A Snowflake PAT (Programmatic Access Token) for API authentication

---

## Setup

### Step 1: Configure for your environment

Run the configure script to update all files (SQL, YAML, frontend) with your database, schema, and account:

```bash
python3 configure.py --db MY_DB --schema MY_SCHEMA --account myorg-myaccount --warehouse MY_WH \
    --interactive-wh MY_INTERACTIVE_WH --image-stage MY_DB.MY_SCHEMA.ECG_STAGE \
    --agent-db SNOWFLAKE_INTELLIGENCE --agent-schema AGENTS --agent-name MY_AGENT
```

Or run interactively:

```bash
python3 configure.py
```

This updates:
- `sql/deploy_medgemma.sql` — SET variables for DB/schema
- `sql/setup_data.sql` — SET variables for DB/schema/warehouse/image stage
- `sql/himss_patient_semantic_model.yaml` — all `database:` / `schema:` fields and VQR SQL
- `himss-physician-app/.env.example` — account, database, schema, warehouse, agent config

> **Defaults**: `DEMO_DB.HIMSS_DEMO` on `myorg-myaccount` with `DEMO_BUILD_WH`. If these work for you, skip this step.

### Step 2: Deploy MedGemma to SPCS

#### 2a. Run the prerequisite SQL

Open `sql/deploy_medgemma.sql` in a Snowflake worksheet and execute it. Before running, update the secrets:

| Placeholder | What to put |
|-------------|-------------|
| `hf_YOUR_TOKEN_HERE` | Your Hugging Face access token |
| `your_snowflake_pat_here` | Your Snowflake PAT |

This creates:
- `MEDGEMMA_GPU_POOL` — GPU compute pool (GPU_NV_S, 1 node)
- `HF_TOKEN_SECRET` — Hugging Face token for gated model access
- `MEDGEMMA_PAT_SECRET` — PAT for stored procedure authentication
- `MEDGEMMA_SPCS_EAI` — External access integration
- `MEDGEMMA_DEMO.PUBLIC.ECG_STAGE` — Stage for medical images

#### 2b. Import MedGemma via Snowsight UI

1. In Snowsight, navigate to **AI & ML → Models → Import model**
2. **Model handle**: `google/medgemma-4b-it`
3. **Task**: `text-generation`
4. Check **"Trust remote code"**
5. **HF token secret**: `<YOUR_DB>.<YOUR_SCHEMA>.HF_TOKEN_SECRET`
6. **Model name**: `MEDGEMMA_4B`
7. **Version**: `v1`
8. **Database/Schema**: `<YOUR_DB>.<YOUR_SCHEMA>`
9. Click **Continue to deployment**
10. **Service name**: `MEDGEMMA_SERVICE`
11. Check **"Create REST API endpoint"**
12. **Compute pool**: `MEDGEMMA_GPU_POOL`
13. **GPU**: `1`
14. Click **Deploy**

Deployment takes ~10-15 minutes. Monitor at **Monitoring → Services & jobs → Jobs tab**.

#### 2c. Retrieve your SPCS endpoint URL

After deployment completes, run:

```sql
SHOW ENDPOINTS IN SERVICE <YOUR_DB>.<YOUR_SCHEMA>.MEDGEMMA_SERVICE;
```

Copy the `ingress_url` value — it looks like:
```
https://<unique-id>-<org>-<account>.snowflakecomputing.app
```

You'll need this URL (with `/__call__` appended) in the next step.

#### 2d. Upload medical images to stage

```
PUT file:///path/to/himss-physician-app/public/images/dummy/*.png
    @<YOUR_IMAGE_STAGE>/dummy/;
```

### Step 3: Create Tables, Data & Stored Procedure

Open `sql/setup_data.sql` in a Snowflake worksheet. Update the SPCS endpoint at the top:

```sql
SET MEDGEMMA_ENDPOINT = 'https://<your-endpoint>.snowflakecomputing.app/__call__';
```

The DB, schema, and warehouse variables were already set by `configure.py` in Step 1. Execute the entire script.

### Step 4: Deploy the Semantic View

```sql
SELECT SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
  '<YOUR_DB>.<YOUR_SCHEMA>',
  $$<paste contents of sql/himss_patient_semantic_model.yaml>$$
);
```

### Step 5: Create the Cortex Agent

Create the agent via Snowsight UI or DDL:
- **Agent name**: `HIMSS_PHYSICIAN_AGENT` in `SNOWFLAKE_INTELLIGENCE.AGENTS`
- **Model**: `claude-4-sonnet`
- **Tools**: `PATIENT_ANALYST` (semantic view), `MEDGEMMA_MEDICAL_INTERPRETER` (stored procedure)

### Step 6: Frontend App

```bash
cd himss-physician-app
cp .env.example .env.local
```

Edit `.env.local` with your values:

```
VITE_SNOWFLAKE_PAT=<your Snowflake PAT>
VITE_SNOWFLAKE_ACCOUNT=<your account identifier>
VITE_SNOWFLAKE_DATABASE=<your database>
VITE_SNOWFLAKE_SCHEMA=<your schema>
VITE_SNOWFLAKE_WAREHOUSE=<your interactive warehouse>
VITE_AGENT_DATABASE=<agent database>          # default: SNOWFLAKE_INTELLIGENCE
VITE_AGENT_SCHEMA=<agent schema>              # default: AGENTS
VITE_AGENT_NAME=<agent name>                  # default: HIMSS_PHYSICIAN_AGENT
VITE_AGENT_MODEL=<agent model>                # default: claude-4-sonnet
```

Then:

```bash
npm install
npm run dev
```

The app runs at `http://localhost:5173`. The Vite dev server proxies `/api` requests to your Snowflake account.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_SNOWFLAKE_PAT` | Snowflake PAT for API authentication | (required) |
| `VITE_SNOWFLAKE_ACCOUNT` | Snowflake account identifier | `myorg-myaccount` |
| `VITE_SNOWFLAKE_DATABASE` | Database name | `DEMO_DB` |
| `VITE_SNOWFLAKE_SCHEMA` | Schema name | `HIMSS_DEMO` |
| `VITE_SNOWFLAKE_WAREHOUSE` | Warehouse for interactive queries | `HIMSS_INTERACTIVE_WH` |
| `VITE_AGENT_DATABASE` | Cortex Agent database | `SNOWFLAKE_INTELLIGENCE` |
| `VITE_AGENT_SCHEMA` | Cortex Agent schema | `AGENTS` |
| `VITE_AGENT_NAME` | Cortex Agent name | `HIMSS_PHYSICIAN_AGENT` |
| `VITE_AGENT_MODEL` | Cortex Agent model | `claude-4-sonnet` |

### SQL Session Variables (setup_data.sql)

| Variable | Description | Default |
|----------|-------------|---------|
| `MY_DB` | Database name | `DEMO_DB` |
| `MY_SCHEMA` | Schema name | `HIMSS_DEMO` |
| `MY_WAREHOUSE` | Build warehouse | `DEMO_BUILD_WH` |
| `MEDGEMMA_ENDPOINT` | SPCS endpoint URL | (required) |
| `IMAGE_STAGE` | Fully-qualified image stage | `MEDGEMMA_DEMO.PUBLIC.ECG_STAGE` |

---

## Verification

After completing all steps, verify the deployment (replace `<DB>.<SCHEMA>` with your values):

```sql
SELECT SYSTEM$GET_SERVICE_STATUS('<DB>.<SCHEMA>.MEDGEMMA_SERVICE');

CALL <DB>.<SCHEMA>.MEDGEMMA_MEDICAL_INTERPRETER(
    'text', NULL,
    'Patient: 67F, HTN, T2DM. Meds: Metoprolol 50mg, Lisinopril 20mg, Metformin 1000mg.',
    'Are there any drug interactions?'
);

CALL <DB>.<SCHEMA>.MEDGEMMA_MEDICAL_INTERPRETER(
    'image', 'IMG-7001', NULL, 'Interpret this ECG'
);
```

## Key Capabilities

1. **Cortex Agent** — Native agentic AI that routes physician queries to the right tool
2. **MedGemma on SPCS** — Google's 4B vision-language model for ECG, X-ray, and echo interpretation
3. **Cortex Analyst** — Natural language to SQL over 6 clinical tables via semantic view
4. **Zero Data Movement** — Patient records and model inference stay within Snowflake
5. **Sub-Second Structured Data** — Interactive Tables with always-on warehouse
6. **Unified Platform** — Agent orchestration, text-to-SQL, and GPU inference on one platform

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Model import fails | Check HF token is valid and MedGemma license is accepted |
| Service won't start | Verify compute pool has available GPU nodes: `SHOW COMPUTE POOLS` |
| Stored procedure timeout | MedGemma cold start can take 1-2 min. Retry after service warms up |
| "MEDGEMMA_REST_URL not configured" | Run `SET MEDGEMMA_ENDPOINT = '...'` before calling setup_data.sql |
| Frontend 401 errors | Verify PAT in `.env.local` is valid and not expired |
| Proxy errors in dev | Check `VITE_SNOWFLAKE_ACCOUNT` in `.env.local` matches your account |
| Wrong database/schema | Re-run `python3 configure.py` with correct values |

## License

Internal demo — not for distribution.
