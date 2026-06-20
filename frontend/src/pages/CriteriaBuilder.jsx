import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Plus, Trash2, GripVertical, RotateCcw, Save, Tag, ListChecks, Info, CheckCircle2 } from 'lucide-react';
import api from '../api/client';

const OUTCOME_LABELS = { vendor_score: 'Vendor', hybrid_score: 'Hybrid', independent_score: 'Independent' };
const OUTCOME_COLORS = { vendor_score: '#42a5f5', hybrid_score: '#ab47bc', independent_score: '#66bb6a' };

export default function CriteriaBuilder() {
  const { projectId } = useParams();
  const [criteria, setCriteria] = useState([]);
  const [editingScore, setEditingScore] = useState(null); // {criterionId, field}

  useEffect(() => { loadCriteria(); }, [projectId]);

  const loadCriteria = async () => {
    try { const { data } = await api.get(`/projects/${projectId}/criteria`); setCriteria(data); } catch(e) { console.error(e); }
  };

  const updateCriterion = async (id, updates) => {
    try { await api.patch(`/projects/${projectId}/criteria/${id}`, updates); setEditingScore(null); loadCriteria(); } catch(e) { console.error(e); }
  };

  const categoryColors = { Strategic: '#42a5f5', Technical: '#7c4dff', Risk: '#ef5350', Governance: '#26a69a', Financial: '#f9a825', Organizational: '#ff7043', Operational: '#66bb6a' };

  return (
    <>
      <div className="page-header">
        <h2>Evaluation Criteria</h2>
        <p>The fixed set of business criteria used to evaluate AI architecture alignment</p>
      </div>
      <div className="page-content">
        <div className="flex items-center justify-between mb-4">
          <div className="flex gap-2 items-center text-sm text-muted">
            <CheckCircle2 size={16} className="text-success" />
            <span>Criteria are locked for this project type to ensure assessment validity.</span>
          </div>
          <span className="text-sm text-muted">{criteria.length} criteria</span>
        </div>

        {/* Outcome Scores info */}
        {criteria.length > 0 && (
          <div className="card mb-4" style={{ padding: '12px 16px', background: 'var(--bg-tertiary)', borderLeft: '3px solid var(--accent-primary)' }}>
            <div className="flex items-center gap-2">
              <Info size={16} style={{ color: 'var(--accent-primary)', flexShrink: 0 }} />
              <span className="text-sm text-muted">
                <strong>Outcome Fit Scores</strong> — Each criterion has expert-derived scores (1-5) for how well each AI architecture fits it. Click a score to adjust. Respondents never see these — only the pairwise comparison dropdowns.
              </span>
            </div>
          </div>
        )}

        {/* Criteria List */}
        <div className="flex flex-col gap-2">
          {criteria.map((c, i) => (
            <div key={c.id} className="card animate-in" style={{ padding: '16px 20px', animationDelay: `${i * 40}ms` }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3" style={{flex:1}}>
                  <span style={{
                    width:24, height:24, borderRadius:'50%', display:'flex', alignItems:'center', justifyContent:'center',
                    background: 'var(--accent-glow)', color: 'var(--accent-primary)', fontSize:'0.7rem', fontWeight:700,
                  }}>{i+1}</span>
                  <div>
                    <div style={{fontWeight:600}}>{c.name}</div>
                    <div className="text-xs text-muted" style={{marginTop:2}}>{c.description}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {/* Outcome Fit Scores */}
                  {Object.entries(OUTCOME_LABELS).map(([field, label]) => {
                    const isEditing = editingScore?.criterionId === c.id && editingScore?.field === field;
                    const value = c[field] || 3;
                    return isEditing ? (
                      <select key={field} className="form-select" style={{ width: 60, padding: '2px 4px', fontSize: '0.75rem' }}
                        defaultValue={value}
                        onChange={e => updateCriterion(c.id, { [field]: parseFloat(e.target.value) })}
                        onBlur={() => setEditingScore(null)}
                        autoFocus
                      >
                        {[1,2,3,4,5].map(v => <option key={v} value={v}>{v}</option>)}
                      </select>
                    ) : (
                      <span key={field} title={`${label}: ${value}/5 — click to edit`}
                        onClick={() => setEditingScore({ criterionId: c.id, field })}
                        style={{
                          cursor: 'pointer',
                          padding: '2px 8px',
                          borderRadius: 12,
                          fontSize: '0.7rem',
                          fontWeight: 600,
                          background: `${OUTCOME_COLORS[field]}18`,
                          color: OUTCOME_COLORS[field],
                          border: `1px solid ${OUTCOME_COLORS[field]}30`,
                          whiteSpace: 'nowrap',
                          transition: 'all 0.15s',
                        }}
                      >
                        {label[0]}: {value}
                      </span>
                    );
                  })}
                  {c.category && (
                    <span className="badge" style={{
                      background: `${categoryColors[c.category] || '#666'}20`,
                      color: categoryColors[c.category] || '#666',
                    }}>
                      <Tag size={10} /> {c.category}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {criteria.length === 0 && (
          <div className="empty-state">
            <ListChecks size={48} />
            <h3>No criteria defined</h3>
            <p>Load the default criteria set or add custom criteria.</p>
          </div>
        )}
      </div>
    </>
  );
}

