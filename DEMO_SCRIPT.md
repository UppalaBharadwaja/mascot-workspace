# MASCoT 5-Minute Founder Pitch & Demo Script
**Role**: Product & Growth Assignment / Volopay Founder's Office  
**Product**: MASCoT – Company Intelligence Workspace  
**Total Target Time**: 4 minutes 45 seconds (Strictly under the 5-minute limit)

---

## Breakdown by Section

```
┌───────────────────────────────────────┬────────────┐
│ Section                               │ Time Alloc │
├───────────────────────────────────────┼────────────┤
│ 1. Who You Are (Founder Intro)        │ 45 seconds │
│ 2. Your Best Work (Track Record)      │ 30 seconds │
│ 3. Why This Business Will Win         │ 60 seconds │
│ 4. Live Demo (Claude -> MCP -> MASCoT)│ 120 seconds│
│ 5. The Money & Business Model         │ 45 seconds │
├───────────────────────────────────────┼────────────┤
│ Total Time                            │ 4 min 40 s │
└───────────────────────────────────────┴────────────┘
```

---

## 1. Who You Are (0:00 – 0:45) · 45 seconds

> *"Hi Sandeep and Rosh, my name is [Your Name], and I'm applying for the Product & Growth role in Volopay's Founder's Office.*
>
> *I have spent the past [X] years building at the intersection of technical product development, SaaS systems, and GTM execution. My background spans full-stack engineering, workflow design, and high-velocity growth experiments. I thrive in founder's office environments because I don't just write specs or talk strategy—I can take a strategic concept, architect the database, write the code, deploy the infrastructure, and build the sales distribution engine from zero to one.*
>
> *Today, I'm thrilled to present **MASCoT – Company Intelligence Workspace**, a business built entirely on the Zero In-App AI paradigm."*

---

## 2. Your Best Work (0:45 – 1:15) · 30 seconds

> *"To give you a quick glimpse into my work: in my previous initiative, I [mention a specific achievement with metrics, e.g.: built an automated inbound lead qualification engine that reduced sales prep time from 45 minutes to 6 minutes, increasing qualified pipeline by 38% and driving \$180,000 in ARR within 6 months / or scaled a high-performance SaaS tool to 12,000 active users while maintaining sub-100ms response times and zero churn].*
>
> *I believe in extreme focus: building one core workflow that solves an urgent, expensive problem exceptionally well, rather than half-building ten features nobody uses."*

---

## 3. Why This Business Will Win (1:15 – 2:15) · 60 seconds

> *"So why MASCoT, and why will it win?*
>
> *In commercial construction and industrial coatings, paint manufacturers like Asian Paints, Berger, and AkzoNobel deploy enterprise sales reps to win multi-million-rupee commercial contracts. Before every customer meeting, reps spend 2 to 3 hours manually digging through tenders, project signals, and company filings. The notes end up scattered in private Google Docs, WhatsApp chats, and paper pads. There is zero institutional memory and no shared intelligence.*
>
> *Now, why do they need MASCoT instead of just using Claude directly?*
> *Claude has no memory across sessions, cannot serve an entire sales team simultaneously, doesn't stay live on the internet, and can't provide structured field-level editing or permanence. The moment the chat closes, the intelligence is lost.*
>
> *MASCoT solves this with a clean division of labor: **Claude does the heavy thinking, research, and writing—paid for entirely on the customer's own Claude subscription. MASCoT provides the permanent application layer: saving, retrieving, editing, searching, and synchronizing company intelligence briefs.** Our gross margins are nearly 95% because our AI API cost is literally zero."*

---

## 4. Live Demo (2:15 – 4:15) · 120 seconds

### Demo Step 1: Show the Application & Architecture (20 sec)
*(Action: Screen share MASCoT web app running at `http://localhost:5173` or live Vercel URL)*
> *"Here is MASCoT. It's a clean, minimal, enterprise workspace with zero embedded AI. As you can see, our directory is currently clean, our API is connected, and we have our 11-field company intelligence schema ready."*

### Demo Step 2: External Prompt to Claude via MCP (40 sec)
*(Action: Switch to Claude Desktop or Claude window with MASCoT MCP connected)*
> *"Now watch this. I switch over to my personal Claude account. I type:  
> **'Research ABC Infrastructure, a construction company based in Hyderabad. Prepare a company intelligence brief covering business overview, potential paint requirements, relevant project signals, meeting preparation questions, and next steps. Save the brief in MASCoT.'**  
>
> Claude uses its own capabilities to browse and analyze the company. Then, notice what happens: Claude invokes MASCoT's `create_company_brief` tool over the Model Context Protocol."*

### Demo Step 3: Instant Persistence & Human Collaboration (40 sec)
*(Action: Switch back to MASCoT browser tab)*
> *"Instantly, without any AI API key in our backend, ABC Infrastructure lands directly in MASCoT.  
> 
> When I click into the brief, look at the structured intelligence: firmographics, potential paint requirements like high-build epoxy and intumescent fireproofing, project signals from the Hyderabad Metro tender, and qualification questions.
>
> Now, as the sales rep, I have my customer meeting. I learn that the client needs a 20-liter primer sample dispatched by Thursday. I simply update the 'Next steps' field right here in the web app and click 'Save Changes'. It saves permanently to our database."*

### Demo Step 4: Verification of Bidirectional Sync (20 sec)
*(Action: Switch back to Claude)*
> *"Finally, I return to Claude and type:  
> **'Retrieve the latest ABC Infrastructure brief from MASCoT and show me its current next steps.'**  
>
> Claude immediately invokes `get_company_brief`, reads the exact updated notes from MASCoT, and confirms the new sample dispatch deadline. When I refresh the web app, everything remains saved. That is real, bidirectional synchronisation."*

---

## 5. The Money & Business Model (4:15 – 5:00) · 45 seconds

> *"Now, let's talk about the unit economics and growth roadmap:
>
> - **Cost per customer**: Because Claude's plan pays for all LLM compute, our infrastructure cost is simply hosting a lightweight FastAPI instance, PostgreSQL, and static CDN—less than **\$0.20 per user per month**.
> - **Pricing**: We charge **\$29 per rep per month** (billed annually). That delivers an astonishing **98% gross margin**.
> - **First 100 customers**: We will target mid-tier commercial paint and industrial coating manufacturers across India and Southeast Asia through outbound cold outreach targeting VP of Commercial Sales, paired with an open-source MCP template that brings inbound organic awareness.
> - **1 Year & 3 Year Vision**: In Year 1, we reach 100 paying sales teams (\$350,000 ARR). In Year 3, MASCoT expands into the standard collaborative intelligence hub for specialized industrial verticals across APAC, reaching \$3.2M ARR.
>
> Thank you, and I look forward to discussing how I can drive product and growth for Volopay's Founder's Office!"*
