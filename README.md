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
├── himss-physician-app/          # React + TypeScript + Tailwind (Vite)
│   ├── src/
│   │   ├── components/           # PatientSidebar, PatientDetailPanel, ChatPanel, ChatBubble
│   │   ├── hooks/                # useAgentChat (SSE streaming), usePatientData
│   │   └── types/                # TypeScript interfaces
│   └── public/images/dummy/      # Sample medical images (ECG, X-ray, Echo, etc.)
├── sql/
│   ├── deploy_medgemma.sql       # Step 1: MedGemma deployment prerequisites (compute pool, EAI, secrets)
│   ├── setup_data.sql            # Step 2: DDL for tables, data, MedGemma stored procedure
│   └── himss_patient_semantic_model.yaml  # Semantic View definition (6 tables, 17 VQRs)
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

- Snowflake account (commercial AWS/Azure/GCP) with Cortex Agent, Cortex Analyst, and SPCS enabled
- Node.js 18+
- A [Hugging Face account](https://huggingface.co/join) with access to [MedGemma 4B](https://huggingface.co/google/medgemma-4b-it) (accept the license)
- A Hugging Face access token ([generate here](https://huggingface.co/settings/tokens))
- A Snowflake PAT (Programmatic Access Token) for API authentication

---

## Setup

### Step 1: Deploy MedGemma to SPCS

This step creates the GPU compute pool, secrets, network rules, and imports MedGemma from Hugging Face.

#### 1a. Run the prerequisite SQL

Open `sql/deploy_medgemma.sql` in a Snowflake worksheet and execute it. Before running, update these values:

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

#### 1b. Import MedGemma via Snowsight UI

1. In Snowsight, navigate to **AI & ML → Models → Import model**
2. **Model handle**: `google/medgemma-4b-it`
3. **Task**: `text-generation`
4. Check **"Trust remote code"**
5. **HF token secret**: `DEMO_DB.HIMSS_DEMO.HF_TOKEN_SECRET`
6. **Model name**: `MEDGEMMA_4B`
7. **Version**: `v1`
8. **Database/Schema**: `DEMO_DB.HIMSS_DEMO`
9. Click **Continue to deployment**
10. **Service name**: `MEDGEMMA_SERVICE`
11. Check **"Create REST API endpoint"**
12. **Compute pool**: `MEDGEMMA_GPU_POOL`
13. **GPU**: `1`
14. Click **Deploy**

Deployment takes ~10-15 minutes. Monitor at **Monitoring → Services & jobs → Jobs tab**.

#### 1c. Retrieve your SPCS endpoint URL

After deployment completes, run:

```sql
SHOW ENDPOINTS IN SERVICE DEMO_DB.HIMSS_DEMO.MEDGEMMA_SERVICE;
```

Copy the `ingress_url` value — it looks like:
```
https://<unique-id>-<org>-<account>.snowflakecomputing.app
```

You'll need this URL (with `/__call__` appended) in the next step.

#### 1d. Upload medical images to stage

```sql
-- From SnowSQL or Snowsight:
PUT file:///path/to/himss-physician-app/public/images/dummy/*.png
    @MEDGEMMA_DEMO.PUBLIC.ECG_STAGE/dummy/;
```

### Step 2: Create Tables, Data & Stored Procedure

Open `sql/setup_data.sql` in a Snowflake worksheet. Before running, update the variables at the top:

```sql
SET MEDGEMMA_ENDPOINT = 'https://<your-endpoint>.snowflakecomputing.app/__call__';
SET MY_WAREHOUSE = 'DEMO_BUILD_WH';  -- or your warehouse
```

Then execute the entire script. This creates:
- 6 clinical tables with sample patient data (3 patients, 9 images)
- `MEDGEMMA_MEDICAL_INTERPRETER` stored procedure

### Step 3: Deploy the Semantic View

```sql
SELECT SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
  'DEMO_DB.HIMSS_DEMO',
  $$<paste contents of sql/himss_patient_semantic_model.yaml>$$
);
```

### Step 4: Create the Cortex Agent

Create the agent via Snowsight UI or DDL:
- **Agent name**: `HIMSS_PHYSICIAN_AGENT` in `SNOWFLAKE_INTELLIGENCE.AGENTS`
- **Model**: `claude-4-sonnet`
- **Tools**: `PATIENT_ANALYST` (semantic view), `MEDGEMMA_MEDICAL_INTERPRETER` (stored procedure)

### Step 5: Frontend App

```bash
cd himss-physician-app
cp .env.example .env.local
```

Edit `.env.local` with your values:

```
VITE_SNOWFLAKE_PAT=<your Snowflake PAT>
VITE_SNOWFLAKE_ACCOUNT=<your account identifier>
```

Then:

```bash
npm install
npm run dev
```

The app runs at `http://localhost:5173`. The Vite dev server proxies `/api` requests to your Snowflake account.

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_SNOWFLAKE_PAT` | Snowflake PAT for API authentication | `ver:1-hint:...` |
| `VITE_SNOWFLAKE_ACCOUNT` | Snowflake account identifier | `myorg-myaccount` |

---

## Verification

After completing all steps, verify the deployment:

```sql
-- Check MedGemma service is running
SELECT SYSTEM$GET_SERVICE_STATUS('DEMO_DB.HIMSS_DEMO.MEDGEMMA_SERVICE');

-- Test the stored procedure (text mode)
CALL DEMO_DB.HIMSS_DEMO.MEDGEMMA_MEDICAL_INTERPRETER(
    'text', NULL,
    'Patient: 67F, HTN, T2DM. Meds: Metoprolol 50mg, Lisinopril 20mg, Metformin 1000mg.',
    'Are there any drug interactions?'
);

-- Test the stored procedure (image mode)
CALL DEMO_DB.HIMSS_DEMO.MEDGEMMA_MEDICAL_INTERPRETER(
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
| Proxy errors in dev | Check `vite.config.ts` proxy target matches your account |

## License

Internal demo — not for distribution.
