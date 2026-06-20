import { useState } from 'react';
import {
  BookOpen, ChevronRight, ChevronDown, Search,
  LayoutDashboard, ListChecks, FileSpreadsheet, Upload,
  Calculator, Target, Shield, Brain, Download, Settings,
  HelpCircle, Lightbulb, AlertTriangle, CheckCircle2
} from 'lucide-react';

const SECTIONS = [
  {
    id: 'overview',
    title: 'What is AlphaAlign?',
    icon: BookOpen,
    color: '#42a5f5', // Blue
    content: `
**AlphaAlign** is a Strategic AI Choice Assessment Engine that helps organizations make informed, data-driven decisions about their AI architecture posture.

It uses the **Analytic Hierarchy Process (AHP)** — a proven mathematical framework for multi-criteria decision-making — combined with **LLM-powered narrative analysis** to evaluate three possible AI architecture outcomes:

| Outcome | Description |
|---------|-------------|
| **Strong Vendor Commitment** | Lock in with a major vendor (e.g. SAP, Microsoft, Google Cloud). Maximum integration, minimum control. |
| **Hybrid AI Operating Model** | Best-of-breed mix: vendor platforms for stable operations + independent AI for differentiation. |
| **Independent AI Control Model** | Full in-house AI stack. Maximum control, flexibility, and IP ownership. |

### Who Should Use It?

AlphaAlign is designed for **executive leadership teams** (CEO, CFO, CIO, CTO, CISO, COO) who need to align on a strategic AI direction. Each respondent fills out a structured survey, and the platform aggregates their input into a mathematically rigorous recommendation.
    `,
  },
  {
    id: 'workflow',
    title: 'Assessment Workflow',
    icon: LayoutDashboard,
    color: '#ab47bc', // Purple
    content: `
The AlphaAlign assessment follows a **7-step workflow**:

### Step 1: Create Assessment
Create a new assessment project from the Home screen. The system automatically loads the 10 fixed evaluation criteria.

### Step 2: Review Criteria
In **Evaluation Criteria**, review the 10 fixed criteria. While names and descriptions are locked to ensure assessment validity, you can adjust the expert-derived outcome scores (Vendor, Hybrid, Independent) per criterion.

### Step 3: Strategic Context
In **Strategic Context**, provide qualitative business context (Top Goals, Incumbent Tech Stack, Regulatory Constraints, Internal Capabilities). This information is injected directly into the LLM prompt during report generation to provide tailored, context-aware analysis.

### Step 4: Generate & Distribute Survey
The **Survey Generator** creates smart Excel templates for each respondent. These templates use plain-language dropdowns. Distribute these to your leadership team.

### Step 5: Upload & Validate
Upload completed surveys in the **Upload & Validate** tab. The system validates each response and checks for mathematical consistency.

### Step 6: Analyze Results
- **AHP Results**: View the computed criteria weights and outcome scores.
- **Recommendation**: See the final architectural recommendation.
- **LLM Analysis**: Generate an AI-powered narrative analysis of the results.

### Step 7: Export Report
Generate a comprehensive PDF/Excel report summarizing the entire assessment.
    `,
  },
  {
    id: 'ahp',
    title: 'Understanding AHP',
    icon: Calculator,
    color: '#ef5350', // Red
    content: `
### What is the Analytic Hierarchy Process?

The **Analytic Hierarchy Process (AHP)** was developed by Thomas L. Saaty in the 1970s. It's a structured method for organizing and analyzing complex decisions based on mathematics and psychology.

### How It Works in AlphaAlign

**Step 1: Pairwise Comparisons** — Instead of asking "rate each criterion on a scale of 1-10" (which is subjective and inconsistent), AHP asks you to compare criteria *two at a time*:

> "When thinking about your AI strategy, which is more important: **Core Business Criticality** or **Autonomous Operations Ambition**? And by how much?"

You answer with plain language like "A is clearly more important" — the system converts this to the Saaty scale behind the scenes.

**Step 2: Compute Weights** — From all pairwise comparisons, AHP calculates a mathematically consistent set of **criteria weights** (priorities). These weights represent how much each criterion matters relative to the others.

**Step 3: Consistency Check** — AHP automatically checks if your judgements are logically consistent. A high **Consistency Ratio (CR)** means contradictions (e.g., "A > B, B > C, but C > A"). CR should be below 0.10.

**Step 4: Score Alternatives** — Each AI architecture outcome is scored against each criterion. Combined with the criteria weights, this produces the **final recommendation**.

### The Saaty Scale

| Dropdown Label | Saaty Value | Meaning |
|---|---|---|
| Equal importance | 1 | Both criteria matter equally |
| A is slightly more important | 3 | Criterion A has a modest edge |
| A is clearly more important | 5 | A has a strong advantage |
| A is much more important | 7 | A is very strongly favored |
| A is overwhelmingly more important | 9 | A dominates completely |

When you pick "B is more important", the system automatically computes the reciprocal (1/3, 1/5, 1/7, 1/9). **You never need to enter fractions or numbers.**
    `,
  },
  {
    id: 'survey',
    title: 'Survey Template Guide',
    icon: FileSpreadsheet,
    color: '#66bb6a', // Green
    content: `
### The Smart Excel Survey

AlphaAlign generates simple Excel templates with **just one thing to fill in**: dropdown questions comparing criteria two at a time.

---

#### Pairwise Comparisons

For each pair of criteria, you see a simple question:

| # | Criterion A | compared to | Criterion B | Your Judgement |
|---|---|---|---|---|
| 1 | Core Business Criticality | compared to | Autonomous Operations Ambition | ▼ *Select from dropdown* |
| 2 | Core Business Criticality | compared to | Enterprise Integration Complexity | ▼ *Select from dropdown* |

Just pick from the dropdown — options like "A is clearly more important" or "Equal importance". No math required.

**With 10 criteria, you'll have 45 comparisons** (every unique pair). Takes about 10-15 minutes.

---

#### What About Outcome Scoring?

You might wonder: *how does the system know which AI architecture is best for each criterion?*

AlphaAlign uses **expert-derived defaults** for this. For example, the system already knows that "Independent AI Control Model" is a better fit for "Proprietary Data Sensitivity" than "Strong Vendor Commitment". These scores are pre-configured by the assessment coordinator in the Evaluation Criteria view.

**Respondents never see this** — they only answer the dropdown questions about which criteria matter most. The system handles the rest.

---

### Progress Tracking

The Welcome sheet shows a live progress bar that updates as you fill in the survey. Green highlighting appears on completed rows.

### Tips for Respondents

- If unsure about a comparison, pick "Equal importance" — you can always revisit later
- Think about your company's specific context, not abstract best practices
- There are no wrong answers — the survey captures your professional judgement
    `,
  },
  {
    id: 'criteria',
    title: 'Fixed Evaluation Criteria',
    icon: ListChecks,
    color: '#f9a825', // Yellow
    content: `
AlphaAlign uses **10 fixed evaluation criteria**, each representing a critical dimension of AI strategy:

| # | Criterion | What It Measures |
|---|-----------|-----------------|
| 1 | **Core Business Criticality** | How critical are the planned AI use cases to core value and revenue? |
| 2 | **Autonomous Operations Ambition** | To what extent do you envision autonomous actions (Agentic AI)? |
| 3 | **Enterprise Integration Complexity** | How deeply must AI integrate with existing legacy systems/data? |
| 4 | **Vendor Lock-in Tolerance** | How acceptable is heavy dependence on a single major tech vendor? |
| 5 | **Regulatory & Compliance Rigor** | How strict are regulatory and data sovereignty requirements? |
| 6 | **Proprietary Data Sensitivity** | How sensitive is the internal data and IP processed by AI? |
| 7 | **Technological Agility Needs** | How important is rapid swapping of underlying AI models? |
| 8 | **Cost Predictability Focus** | How important is strict predictability of ongoing AI costs? |
| 9 | **In-House AI Capability** | How strong is your internal engineering and data science talent? |
| 10 | **Time-to-Value Urgency** | How urgently does the organization need to deploy AI capabilities? |

**Note:** These criteria are locked to ensure mathematical validity across the assessment. However, the expert-derived Outcome Fit Scores (how well Vendor, Hybrid, or Independent models satisfy each criterion) can be tweaked by the administrator in the **Evaluation Criteria** tab.
    `,
  },
  {
    id: 'consistency',
    title: 'Consistency & Quality',
    icon: AlertTriangle,
    color: '#ff7043', // Orange
    content: `
### Consistency Ratio (CR)

AHP includes a built-in quality check: the **Consistency Ratio (CR)**. It detects logical contradictions in your judgements.

**Example of inconsistency:**
- You say: A is more important than B
- You say: B is more important than C  
- But then: C is more important than A ← This contradicts the first two!

### Interpreting CR

| CR Value | Interpretation |
|----------|---------------|
| **CR < 0.05** | ✅ Excellent consistency — very reliable |
| **CR < 0.10** | ✅ Acceptable — standard threshold |
| **CR 0.10 - 0.20** | ⚠️ Borderline — consider revisiting some comparisons |
| **CR > 0.20** | ❌ Poor — significant contradictions, re-evaluate |

### What To Do If CR Is High

1. Look for the most extreme comparisons — these are often where contradictions hide
2. Ask yourself: "If I ranked all criteria, would this ordering match my pairwise judgements?"
3. Re-fill the survey focusing on the pairs you're most unsure about
    `,
  },
  {
    id: 'llm',
    title: 'LLM Analysis',
    icon: Brain,
    color: '#26a69a', // Teal
    content: `
### AI-Powered Narrative Analysis

The **LLM Analysis** module sends your AHP results, criteria weights, strategic context, and outcome scores to an AI language model for qualitative analysis.

### What It Provides

- **Executive Summary**: Plain-language interpretation of the mathematical results
- **Strategic Insight**: Analysis of what the criteria weights reveal about organizational priorities
- **Risk Assessment**: Identification of potential risks with the recommended outcome
- **Implementation Roadmap**: Suggested next steps based on the chosen architecture
- **Dissent Analysis**: Where respondents disagreed, and what that means

### Supported AI Providers

| Provider | Models |
|----------|--------|
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 Turbo |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus |
| **Google (Gemini)** | Gemini 1.5 Pro, Gemini 1.5 Flash |
| **OpenRouter** | Any OpenRouter model |
| **Ollama** | Any locally-hosted model |
| **LM Studio** | Any locally-hosted model |
| **Azure OpenAI** | Deployed Azure models |
| **Custom** | Any OpenAI-compatible endpoint |

Configure your preferred provider in **Settings → AI Model Setup**.
    `,
  },
  {
    id: 'settings',
    title: 'Settings & Configuration',
    icon: Settings,
    color: '#8d6e63', // Brown
    content: `
### Global Settings

Access via the **Settings** link in the sidebar. Two tabs:

---

#### Company Profile
- **Company Name**: Auto-fills into new assessments
- **Industry**: Your sector (used for LLM context)
- **Contact Name & Email**: Assessment coordinator details

---

#### AI Model Setup
- **LLM Provider**: Select from supported cloud and local providers
- **Model Name**: The specific model to use
- **API Key**: Your provider API key (stored locally, never sent externally except to the provider)
- **API Endpoint**: For self-hosted models (Ollama, LM Studio, Custom)
- **Temperature**: Controls creativity vs. determinism (0.0 = focused, 1.0 = creative)
- **Max Tokens**: Response length limit

### Data Storage

All data is stored locally in a SQLite database at \`backend/data/alphaalign.db\`. No data is sent to external servers — only LLM API calls leave your machine (and only when you explicitly trigger analysis).
    `,
  },
  {
    id: 'glossary',
    title: 'Glossary',
    icon: HelpCircle,
    color: '#78909c', // Blue-Grey
    content: `
| Term | Definition |
|------|-----------|
| **AHP** | Analytic Hierarchy Process — mathematical framework for multi-criteria decision-making |
| **Pairwise Comparison** | Comparing two items at a time to determine relative importance |
| **Saaty Scale** | 1-9 scale used in AHP (you never see this — AlphaAlign uses plain language) |
| **Reciprocal** | If A vs B = 5, then B vs A = 1/5 (computed automatically) |
| **Criteria Weight** | How much each criterion matters (0-1, all weights sum to 1) |
| **Eigenvector** | Mathematical method used to derive consistent weights from pairwise comparisons |
| **Consistency Ratio (CR)** | Measure of logical consistency in judgements (should be < 0.10) |
| **Outcome** | One of the three AI architecture options being evaluated |
| **Alternative Score** | How well an outcome fits a criterion (1-5 scale) |
| **Strategic Context** | Qualitative business context injected into the LLM prompts |
| **Aggregation** | Combining multiple respondents' judgements (geometric mean) |
| **Sensitivity Analysis** | Testing how robust the recommendation is to changes in weights |
    `,
  },
];

export default function ReferenceManual() {
  const [expandedSections, setExpandedSections] = useState(new Set(['overview']));
  const [searchTerm, setSearchTerm] = useState('');

  const toggleSection = (id) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const expandAll = () => setExpandedSections(new Set(SECTIONS.map(s => s.id)));
  const collapseAll = () => setExpandedSections(new Set());

  const filteredSections = searchTerm
    ? SECTIONS.filter(s =>
        s.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.content.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : SECTIONS;

  // Simple markdown-to-HTML renderer for tables and formatting
  const renderMarkdown = (text) => {
    const lines = text.trim().split('\n');
    const elements = [];
    let i = 0;
    let key = 0;

    while (i < lines.length) {
      const line = lines[i];

      // Table detection
      if (line.trim().startsWith('|') && i + 1 < lines.length && lines[i + 1].trim().match(/^\|[\s-:|]+\|$/)) {
        const tableLines = [];
        while (i < lines.length && lines[i].trim().startsWith('|')) {
          tableLines.push(lines[i]);
          i++;
        }
        elements.push(renderTable(tableLines, key++));
        continue;
      }

      // H3
      if (line.trim().startsWith('### ')) {
        elements.push(<h3 key={key++} style={{ color: 'var(--accent)', marginTop: 24, marginBottom: 8, fontSize: '1.1rem' }}>{renderInline(line.trim().slice(4))}</h3>);
        i++; continue;
      }

      // H4
      if (line.trim().startsWith('#### ')) {
        elements.push(<h4 key={key++} style={{ color: 'var(--text-primary)', marginTop: 20, marginBottom: 6, fontSize: '1rem' }}>{renderInline(line.trim().slice(5))}</h4>);
        i++; continue;
      }

      // HR
      if (line.trim() === '---') {
        elements.push(<hr key={key++} style={{ border: 'none', borderTop: '1px solid var(--border-subtle)', margin: '16px 0' }} />);
        i++; continue;
      }

      // Blockquote
      if (line.trim().startsWith('> ')) {
        elements.push(
          <blockquote key={key++} style={{
            borderLeft: '3px solid var(--accent)',
            paddingLeft: 16,
            margin: '12px 0',
            color: 'var(--text-secondary)',
            fontStyle: 'italic',
          }}>
            {renderInline(line.trim().slice(2))}
          </blockquote>
        );
        i++; continue;
      }

      // List items
      if (line.trim().startsWith('- ')) {
        const listItems = [];
        while (i < lines.length && lines[i].trim().startsWith('- ')) {
          listItems.push(lines[i].trim().slice(2));
          i++;
        }
        elements.push(
          <ul key={key++} style={{ paddingLeft: 20, margin: '8px 0' }}>
            {listItems.map((li, idx) => <li key={idx} style={{ marginBottom: 4, lineHeight: 1.6 }}>{renderInline(li)}</li>)}
          </ul>
        );
        continue;
      }

      // Numbered list
      if (line.trim().match(/^\d+\.\s/)) {
        const listItems = [];
        while (i < lines.length && lines[i].trim().match(/^\d+\.\s/)) {
          listItems.push(lines[i].trim().replace(/^\d+\.\s/, ''));
          i++;
        }
        elements.push(
          <ol key={key++} style={{ paddingLeft: 20, margin: '8px 0' }}>
            {listItems.map((li, idx) => <li key={idx} style={{ marginBottom: 4, lineHeight: 1.6 }}>{renderInline(li)}</li>)}
          </ol>
        );
        continue;
      }

      // Empty line
      if (line.trim() === '') {
        i++; continue;
      }

      // Paragraph
      elements.push(<p key={key++} style={{ margin: '8px 0', lineHeight: 1.7 }}>{renderInline(line.trim())}</p>);
      i++;
    }

    return elements;
  };

  const renderInline = (text) => {
    // Bold + italic
    const parts = text.split(/(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|`.*?`)/g);
    return parts.map((part, i) => {
      if (part.startsWith('***') && part.endsWith('***')) return <strong key={i}><em>{part.slice(3, -3)}</em></strong>;
      if (part.startsWith('**') && part.endsWith('**')) return <strong key={i} style={{ color: 'var(--text-primary)' }}>{part.slice(2, -2)}</strong>;
      if (part.startsWith('*') && part.endsWith('*')) return <em key={i}>{part.slice(1, -1)}</em>;
      if (part.startsWith('`') && part.endsWith('`')) return <code key={i} style={{ background: 'var(--surface-hover)', padding: '2px 6px', borderRadius: 4, fontSize: '0.9em' }}>{part.slice(1, -1)}</code>;
      return part;
    });
  };

  const renderTable = (tableLines, key) => {
    const headers = tableLines[0].split('|').filter(c => c.trim()).map(c => c.trim());
    const rows = tableLines.slice(2).map(l => l.split('|').filter(c => c.trim()).map(c => c.trim()));

    return (
      <div key={key} style={{ overflowX: 'auto', margin: '12px 0' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '0.9rem',
        }}>
          <thead>
            <tr>
              {headers.map((h, i) => (
                <th key={i} style={{
                  padding: '8px 12px',
                  textAlign: 'left',
                  borderBottom: '2px solid var(--accent)',
                  color: 'var(--accent)',
                  fontWeight: 600,
                  whiteSpace: 'nowrap',
                }}>{renderInline(h)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri} style={{ background: ri % 2 === 0 ? 'transparent' : 'var(--surface-hover)' }}>
                {row.map((cell, ci) => (
                  <td key={ci} style={{
                    padding: '8px 12px',
                    borderBottom: '1px solid var(--border-subtle)',
                    lineHeight: 1.5,
                  }}>{renderInline(cell)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
          <BookOpen style={{ color: 'var(--accent)' }} size={28} />
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Reference Manual</h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
          Everything you need to know about AlphaAlign, AHP methodology, and how to run a strategic assessment.
        </p>
      </div>

      {/* Search + controls */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 24, alignItems: 'center' }}>
        <div style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          background: 'var(--surface-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 8,
          padding: '8px 14px',
        }}>
          <Search size={16} style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search documentation..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-primary)',
              flex: 1,
              fontSize: '0.95rem',
            }}
          />
        </div>
        <button onClick={expandAll} className="btn-secondary" style={{ padding: '8px 14px', fontSize: '0.85rem' }}>
          Expand All
        </button>
        <button onClick={collapseAll} className="btn-secondary" style={{ padding: '8px 14px', fontSize: '0.85rem' }}>
          Collapse All
        </button>
      </div>

      {/* Sections */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {filteredSections.map(section => {
          const isExpanded = expandedSections.has(section.id);
          const Icon = section.icon;

          return (
            <div key={section.id} style={{
              background: 'var(--surface-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 12,
              overflow: 'hidden',
              transition: 'border-color 0.2s',
              borderColor: isExpanded ? 'var(--accent)' : 'var(--border-subtle)',
            }}>
              {/* Section Header */}
              <div
                onClick={() => toggleSection(section.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  padding: '14px 20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  borderLeft: isExpanded ? `4px solid ${section.color || 'var(--accent)'}` : '4px solid transparent',
                  background: isExpanded ? `${section.color || 'var(--accent)'}15` : 'transparent',
                }}
                onMouseEnter={e => !isExpanded && (e.currentTarget.style.background = 'var(--surface-hover)')}
                onMouseLeave={e => !isExpanded && (e.currentTarget.style.background = 'transparent')}
              >
                <Icon size={20} style={{ color: section.color || 'var(--accent)', flexShrink: 0 }} />
                <span style={{ flex: 1, fontWeight: 600, fontSize: '1.05rem', color: isExpanded ? (section.color || 'inherit') : 'inherit' }}>{section.title}</span>
                {isExpanded
                  ? <ChevronDown size={18} style={{ color: section.color || 'var(--text-muted)' }} />
                  : <ChevronRight size={18} style={{ color: 'var(--text-muted)' }} />
                }
              </div>

              {/* Section Content */}
              {isExpanded && (
                <div style={{
                  padding: '0 20px 20px 52px',
                  color: 'var(--text-secondary)',
                  fontSize: '0.95rem',
                }}>
                  {renderMarkdown(section.content)}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div style={{
        marginTop: 32,
        padding: '16px 20px',
        background: 'var(--surface-card)',
        borderRadius: 12,
        border: '1px solid var(--border-subtle)',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.85rem',
      }}>
        AlphaAlign v1.0.0 — Strategic AI Architecture Assessment Engine
        <br />
        Built with AHP methodology • React + FastAPI • Local-first data
      </div>
    </div>
  );
}
