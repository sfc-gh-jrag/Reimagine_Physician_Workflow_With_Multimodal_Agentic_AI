# HIMSS PhysicianAssist Demo Talk Tracks
### 3 Powerful Narratives — Each Under 3 Minutes

---

## TALK TRACK 1: "The Critical Window"
**Theme**: A 72-year-old man arrives in acute STEMI — every second matters. Show how AI collapses the time from data to decision.

**Patient**: James Wilson (P-1002) — Critical, Acute STEMI (RCA)

### Script (2:45)

**[OPEN — Set the scene]**
> "It's 2 AM. A 72-year-old male, James Wilson, arrives by ambulance — crushing chest pain, diaphoretic, ST elevation on the field ECG. You're the cardiologist on call. You have minutes, not hours."

**[CLICK James Wilson in the patient panel]**

> "With PhysicianAssist, every data point about this patient is unified in one view — vitals, conditions, medications, images, encounters — all pulled live from Snowflake. No searching through five different systems."

*Pause — let the audience absorb the clinical dashboard: vitals, 6 active conditions, 8 medications, severity badges.*

**[CLICK the chat icon, then click "ECG Interpretation"]**

> "Now watch this. With one tap, I'm asking Snowflake's Cortex Agent to orchestrate two AI tools simultaneously — first it queries the structured clinical data through a semantic layer, then it sends the actual ECG image to MedGemma, Google's medical foundation model running *inside* Snowflake on Snowpark Container Services."

*The audience sees the real-time streaming: tool status chips appear — "Analyzing with PATIENT_ANALYST" then "Interpreting with MedGemma" — with a live elapsed time counter.*

> "Notice what's happening: the data never leaves Snowflake's security perimeter. The ECG image, the patient record, the AI inference — all governed, all auditable, all within your existing data cloud."

*Response streams in with ECG findings — ST elevation in inferior leads, RCA involvement, clinical recommendations.*

**[TYPE into chat]**: `Are there any medication interactions I should worry about before we take him to the cath lab?`

> "And because it's agentic, I can have a clinical conversation. It remembers the context. It knows this is James Wilson with acute STEMI, on Warfarin, Metoprolol, and Clopidogrel — and it flags the anticoagulation considerations for an emergent PCI."

**[CLOSE — The impact]**
> "What used to take 15 minutes of chart review across fragmented systems — now takes seconds. Same data governance. Same compliance. But the physician gets the complete picture at the moment it matters most."

---

## TALK TRACK 2: "The Hidden Risk"
**Theme**: A stable post-MI patient looks fine on paper — but the AI finds what a busy physician might miss. Show the power of multi-modal reasoning.

**Patient**: Maria Santos (P-1001) — Stable, Post-MI Recovery (LAD STEMI)

### Script (2:30)

**[OPEN — Challenge the assumption]**
> "Here's the scenario that keeps every cardiologist up at night. Maria Santos, 68 years old, recovering from a LAD STEMI. She's listed as 'stable.' Her vitals look normal. But is she really safe to discharge?"

**[CLICK Maria Santos in the patient panel]**

> "At a glance, the dashboard shows stable vitals — heart rate 72, blood pressure controlled, SpO2 97%. Six conditions, seven medications. Looks routine."

**[CLICK the chat icon, then click "Risk Assessment"]**

> "But watch what happens when we ask the AI to think across modalities — structured data, unstructured notes, and medical imaging — all at once."

*Streaming begins — tool chips show PATIENT_ANALYST querying conditions, medications, vitals trends, then MedGemma analyzing the echocardiogram.*

> "The Cortex Agent is doing something no single clinician could do in real-time — it's correlating her medication regimen against her comorbidities, checking her vitals trend over the past week, and interpreting her echocardiogram... simultaneously."

*Response streams in with a comprehensive risk profile.*

> "It identifies that while she's hemodynamically stable, the combination of her diabetes with hyperglycemia, her cholesterol levels, and post-MI cardiac remodeling visible on echo creates a compound risk that isn't obvious from any single data point."

**[TYPE into chat]**: `What's her complete medication list and are there any gaps in her current treatment protocol?`

> "Now I'm having a physician-level conversation with my data. It pulls her full medication table — Lisinopril, Atorvastatin, Metoprolol, Aspirin, Clopidogrel — and can flag if guideline-directed medical therapy has any gaps."

**[CLOSE — The vision]**
> "This is the future of clinical decision support — not alerts that cry wolf, but an intelligent agent that reasons across your entire data estate. Built on Snowflake. Governed. Scalable. And running Google's MedGemma model right next to where the data already lives."

---

## TALK TRACK 3: "From Fragmented to Unified"
**Theme**: Three patients, three acuity levels, one platform. Show the breadth of the system by rapidly switching patients and demonstrate how this replaces an entire ecosystem of disconnected tools.

**Patient**: All three — Maria Santos, James Wilson, Aisha Rahman

### Script (2:50)

**[OPEN — The problem statement]**
> "Raise your hand if your health system uses more than five different applications to manage a single patient encounter."

*Pause for audience reaction.*

> "EHR for notes. PACS for imaging. A separate analytics dashboard. A drug interaction checker. And maybe a clinical decision support system that nobody trusts because it fires too many alerts. What if all of that was one conversation?"

**[CLICK James Wilson — show the critical patient]**

> "James Wilson — 72, acute STEMI, critical. In one view: vitals, conditions with severity badges, medications with drug classes, imaging, and recent encounters. All from Snowflake interactive tables — real-time, governed, zero ETL."

**[Quickly CLICK Aisha Rahman — show the monitoring patient]**

> "Now Aisha Rahman — 57, supraventricular tachycardia, on monitoring. Different acuity, different needs."

**[CLICK the chat icon, then click "ECG Interpretation"]**

> "Same question — interpret her ECG. But watch: the AI *adapts its context automatically*. It knows this is Aisha, not James. It pulls HER ECG, queries HER conditions, considers HER medications."

*Streaming shows tool orchestration with Aisha's context.*

> "Behind the scenes, Snowflake's Cortex Agent is orchestrating a semantic query against structured clinical data AND sending the ECG to MedGemma for interpretation — and it's doing this with full patient context injection. The model knows exactly who it's looking at."

*Response arrives — SVT-specific findings, Holter correlation, rhythm management recommendations.*

**[TYPE into chat]**: `Compare her heart rate trends over the last week and correlate with her rhythm findings`

> "And because it's built on a semantic model with verified queries, the SQL it generates is *accurate*. Not hallucinated. Not approximate. Verified against fifteen ground-truth query patterns."

**[CLOSE — The architecture pitch]**

> "Let me tell you what's under the hood in 10 seconds: Snowflake Cortex Agent orchestrating two tools — Cortex Analyst for text-to-SQL over a semantic view, and MedGemma 4B running on Snowpark Container Services. React frontend. Real-time streaming. No data leaves Snowflake. No PHI in transit. And the entire thing — data, models, governance, and application — lives in one platform."

> "This isn't a demo of what's possible someday. This is running right now. On Snowflake."

---

## QUICK REFERENCE: Key Talking Points for Q&A

| Question | Answer |
|----------|--------|
| "Where does MedGemma run?" | On Snowpark Container Services — inside Snowflake's compute layer. The image never leaves your account perimeter. |
| "Is the SQL hallucinated?" | No — Cortex Analyst uses a semantic view with 15 verified query patterns. It generates SQL grounded in the actual schema, not guessed. |
| "How fast is it?" | Sub-10 seconds for structured queries, 15-25 seconds when MedGemma image analysis is involved. Real-time streaming so the physician sees results as they arrive. |
| "What about HIPAA?" | All data, compute, and inference stay within Snowflake's governed perimeter. No external API calls. Role-based access control on every table. |
| "Can this work with our EHR?" | The data layer is Snowflake tables — any EHR that can export to Snowflake (via Health Data Cloud, HL7 FHIR ingestion, or standard ETL) feeds this directly. |
| "What model powers the agent?" | Claude Sonnet via Snowflake Cortex as the orchestration LLM, with Google MedGemma 4B as the specialized medical vision model. |
| "How hard is this to build?" | The entire application is ~15 files. The Cortex Agent is defined in YAML. The semantic view is a single YAML file with verified queries. The hardest part was already done — getting the data into Snowflake. |

---

## PRO TIPS FOR DELIVERY

1. **Start with the patient, not the technology.** The audience connects with "72-year-old man, crushing chest pain" — not "Cortex Agent with SSE streaming."
2. **Let the streaming do the talking.** When the tool status chips appear and the timer counts up, stay silent for 2-3 seconds. The audience sees the AI *working* in real-time — that's more powerful than any slide.
3. **Click, don't type, for the first query.** The quick action buttons are pre-loaded with perfect prompts. Use them for speed and reliability. Save the free-text typing for the follow-up question — that shows it's truly conversational.
4. **Name the architecture only at the end.** Physicians care about workflow. CTOs care about architecture. Lead with the clinical story, close with the stack.
5. **Have all three talk tracks ready.** If the first demo goes fast, pivot to a second patient. If you get a question about imaging, switch to the ECG track. Flexibility wins.
