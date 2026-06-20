# AlphaAlign 🎯

**Strategic AI Choice Assessment Engine**

AlphaAlign is a specialized, local-first decision support tool built for C-level executives and IT leadership. Rather than relying on hype or vendor sales pitches, AlphaAlign uses advanced mathematics (the Analytic Hierarchy Process) and Large Language Models (LLMs) to definitively answer: *"Which AI architecture strategy is right for our organization right now?"*

![AlphaAlign](Build%20Assets/AlphaAlign%20-%20Logo.png)

---

## 📑 Table of Contents
- [The Challenge](#the-challenge)
- [How AlphaAlign Works](#how-alphaalign-works)
- [The Three Architectural Outcomes](#the-three-architectural-outcomes)
- [The 10 Immutable Criteria](#the-10-immutable-criteria)
- [Key Features](#key-features)
- [Installation & Setup](#installation--setup)
- [Security & Data Privacy](#security--data-privacy)
- [Technology Stack](#technology-stack)

---

## ❓ The Challenge

Choosing an enterprise AI strategy is one of the most critical decisions leadership faces today. The market is saturated with conflicting advice:
- *Should we lock into our primary cloud vendor (Microsoft/Google)?*
- *Should we build a vendor-agnostic hybrid model?*
- *Should we maintain absolute control with an independent, open-source stack?*

AlphaAlign strips away the marketing hype and forces organizational alignment through rigorous, objective mathematical scoring combined with deep strategic context.

---

## ⚙️ How AlphaAlign Works

AlphaAlign operates on a seamless 5-step workflow designed for executive participation without technical friction:

1. **Strategic Context & Initialization**
   The Assessment Owner creates a project and defines the company's "Strategic Context" (ambition level, time horizon, internal capability, regulatory strictness, and incumbent vendors).
   
2. **Automated Excel Survey Generation**
   The platform generates a smart `.xlsx` survey file. Complex matrix math is hidden behind plain-English pairwise comparisons (e.g., *"Is Data Security more important than Cost Predictability?"*).

3. **Survey Import & Mathematical Engine (AHP)**
   Stakeholders complete the Excel files, which are imported back into AlphaAlign. The system uses the **Analytic Hierarchy Process (AHP)** to calculate the true priority weights of the criteria and mathematical Consistency Ratios for every respondent.

4. **Outcome Scoring**
   The AHP engine cross-references the aggregated organizational weights against pre-defined expert "Outcome Fit Scores" to mathematically rank the 3 architecture outcomes.

5. **LLM-Powered Strategic Narrative**
   (Optional) If connected to an AI provider (OpenAI, Anthropic, OpenRouter), AlphaAlign packages the mathematical results and Strategic Context and sends them to the LLM. It generates a boardroom-ready strategic consulting report, including Executive Summaries, Risk Assessments, and Implementation Roadmaps.

---

## 🏛️ The Three Architectural Outcomes

AlphaAlign scores your organization against three distinct paths:

1. **Strong Vendor Commitment**
   *Lock-in with a major player (e.g., Microsoft Copilot, Google Workspace).* 
   Best for organizations prioritizing speed, integration, and ease of use over ultimate control.
2. **Hybrid AI Operating Model**
   *A mix of vendor platforms and independent capabilities.*
   Best for organizations seeking flexibility, balancing rapid deployment in some areas with bespoke control in others.
3. **Independent AI Control Model**
   *Full in-house, open-source, or tightly controlled stack.*
   Best for organizations with extreme data sensitivity, high internal capabilities, and a need to avoid vendor lock-in at all costs.

---

## ⚖️ The 10 Immutable Criteria

To ensure rigorous and unbiased evaluation, AlphaAlign uses 10 fixed criteria that cover the entire spectrum of strategic technology adoption:

1. **Data Security & Privacy Requirements** (Strict control vs. Delegated trust)
2. **Proprietary Data Sensitivity** (IP protection)
3. **Internal Technical Capability** (Do we have the talent to build it?)
4. **Time-to-Value Urgency** (Do we need this tomorrow or next year?)
5. **Vendor Ecosystem Lock-in Tolerance** (Risk appetite for dependency)
6. **Cost Predictability vs. Flexibility** (OpEx/CapEx constraints)
7. **Technology Agility vs. Stability** (Cutting-edge vs. Proven)
8. **Compliance & Auditability Needs** (Regulatory strictness)
9. **Executive Sponsorship & Buy-in** (Top-down mandate strength)
10. **Organizational Change Management Capacity** (Can our people adapt?)

---

## ✨ Key Features

- **Executive-Friendly Surveys:** Smart Excel files that guide respondents without requiring any knowledge of AHP math.
- **Consistency Checking:** Automatically detects if a respondent answered randomly or contradictorily.
- **Dissent Analysis:** The LLM highlights misalignment between different executives (e.g., if the CTO's priorities vastly differ from the CFO's).
- **100% Local Execution:** By default, all data and projects are stored locally in an embedded SQLite database. No data leaves your machine unless you explicitly trigger the LLM analysis.
- **Beautiful, Presentation-Ready UI:** Designed with modern aesthetics to look like a premium enterprise tool right out of the box.

---

## 🚀 Installation & Setup

AlphaAlign requires **Python 3.10+** and **Node.js v18+**.

We provide zero-friction installation scripts for both Windows and macOS/Linux.

### Windows
1. Clone or download this repository.
2. Double-click **`install.bat`** to install all dependencies.
3. Once installed, double-click **`start.bat`**. This will launch both the backend and frontend servers automatically.
4. Your browser will open to `http://localhost:5173`.

### macOS / Linux
1. Clone or download this repository.
2. Open a terminal and run the install script:
   ```bash
   chmod +x install.sh start.sh
   ./install.sh
   ```
3. Once installed, start the platform by running:
   ```bash
   ./start.sh
   ```
4. Your browser will open to `http://localhost:5173`.

---

## 🔒 Security & Data Privacy

Because AlphaAlign is used to evaluate highly sensitive corporate strategy, it is designed to be **Local-First**.
- **Database:** Uses a local `alphaalign.db` SQLite file.
- **Surveys:** Excel files are parsed locally on the Python backend.
- **LLM Integration:** The only external network call is made when you explicitly click "Generate LLM Analysis". You provide your own API key (stored locally in `settings.json`) so your data is sent directly to your chosen provider under your own data privacy agreements.

---

## 💻 Technology Stack

- **Backend:** Python, FastAPI, SQLAlchemy, aiosqlite, openpyxl (for Excel manipulation).
- **Frontend:** React, Vite, React Router, Recharts, Lucide React (Icons).
- **Algorithms:** Analytic Hierarchy Process (AHP) matrix math.
- **AI Integration:** Direct REST API calls to major LLM providers (OpenAI, Anthropic, OpenRouter).

---

*Built for strategic clarity.*
