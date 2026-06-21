import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Plus, Trash2, Tag, ListChecks, Info, CheckCircle2, ToggleLeft, ToggleRight, Zap, Lock, PlusCircle, X } from 'lucide-react';
import api from '../api/client';

const OUTCOME_LABELS = { vendor_score: 'Vendor', hybrid_score: 'Hybrid', independent_score: 'Independent' };
const OUTCOME_COLORS = { vendor_score: '#42a5f5', hybrid_score: '#ab47bc', independent_score: '#66bb6a' };

export default function CriteriaBuilder() {
  const { projectId } = useParams();
  const [criteria, setCriteria] = useState([]);
  const [editingScore, setEditingScore] = useState(null);
  const [flexMode, setFlexMode] = useState(false);
  const [flexLibrary, setFlexLibrary] = useState([]);
  const [showFlexPicker, setShowFlexPicker] = useState(false);
  const [adding, setAdding] = useState(null);

  useEffect(() => { loadCriteria(); }, [projectId]);

  const loadCriteria = async () => {
    try { const { data } = await api.get(`/projects/${projectId}/criteria`); setCriteria(data); } catch(e) { console.error(e); }
  };

  const loadFlexLibrary = async () => {
    try { const { data } = await api.get(`/projects/${projectId}/criteria/flex-library`); setFlexLibrary(data); } catch(e) { console.error(e); }
  };

  const updateCriterion = async (id, updates) => {
    try { await api.patch(`/projects/${projectId}/criteria/${id}`, updates); setEditingScore(null); loadCriteria(); } catch(e) { console.error(e); }
  };

  const addFlexCriterion = async (flexItem) => {
    setAdding(flexItem.name);
    try {
      await api.post(`/projects/${projectId}/criteria`, {
        name: flexItem.name,
        description: flexItem.description,
        category: flexItem.category,
        vendor_score: flexItem.vendor_score,
        hybrid_score: flexItem.hybrid_score,
        independent_score: flexItem.independent_score,
      });
      await loadCriteria();
      await loadFlexLibrary();
    } catch(e) { alert(e.response?.data?.detail || 'Failed to add criterion'); }
    setAdding(null);
  };

  const removeCriterion = async (id) => {
    if (!confirm('Remove this flex criterion from the assessment?')) return;
    try { await api.delete(`/projects/${projectId}/criteria/${id}`); loadCriteria(); loadFlexLibrary(); }
    catch(e) { alert(e.response?.data?.detail || 'Cannot remove this criterion'); }
  };

  const toggleFlexMode = () => {
    const next = !flexMode;
    setFlexMode(next);
    if (next) { loadFlexLibrary(); setShowFlexPicker(false); }
    else { setShowFlexPicker(false); }
  };

  const categoryColors = { Strategic: '#42a5f5', Technical: '#7c4dff', Risk: '#ef5350', Governance: '#26a69a', Financial: '#f9a825', Organizational: '#ff7043', Operational: '#66bb6a' };

  const coreCriteria = criteria.filter(c => c.is_mandatory);
  const flexCriteria = criteria.filter(c => !c.is_mandatory);

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
            <span>Core criteria are locked to ensure assessment validity.</span>
          </div>
          {/* Flex Mode Toggle */}
          <div
            onClick={toggleFlexMode}
            style={{
              display: 'flex', alignItems: 'center', gap: 8,
              padding: '6px 14px', borderRadius: 20, cursor: 'pointer',
              background: flexMode
                ? 'linear-gradient(135deg, rgba(124, 77, 255, 0.15), rgba(66, 165, 245, 0.15))'
                : 'var(--bg-tertiary)',
              border: flexMode ? '1px solid rgba(124, 77, 255, 0.4)' : '1px solid var(--border)',
              transition: 'all 0.3s ease',
            }}
          >
            {flexMode
              ? <ToggleRight size={20} style={{ color: '#7c4dff' }} />
              : <ToggleLeft size={20} style={{ color: 'var(--text-muted)' }} />
            }
            <span style={{
              fontSize: '0.8rem', fontWeight: 600,
              color: flexMode ? '#7c4dff' : 'var(--text-muted)',
              transition: 'color 0.3s',
            }}>
              Flex Mode
            </span>
            {flexMode && <Zap size={14} style={{ color: '#f9a825' }} />}
          </div>
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

        {/* Flex Mode Banner */}
        {flexMode && (
          <div className="card mb-4 animate-in" style={{
            padding: '14px 18px',
            background: 'linear-gradient(135deg, rgba(124, 77, 255, 0.08), rgba(66, 165, 245, 0.08))',
            borderLeft: '3px solid #7c4dff',
          }}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Zap size={18} style={{ color: '#f9a825' }} />
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#7c4dff' }}>Flex Mode Active</div>
                  <div className="text-xs text-muted">Add additional strategic criteria to deepen your assessment. Core criteria remain locked.</div>
                </div>
              </div>
              <button
                className="btn btn-primary"
                style={{ fontSize: '0.8rem', padding: '6px 14px', background: '#7c4dff' }}
                onClick={() => { setShowFlexPicker(!showFlexPicker); if (!showFlexPicker) loadFlexLibrary(); }}
              >
                <PlusCircle size={14} /> {showFlexPicker ? 'Close Library' : 'Add Criteria'}
              </button>
            </div>
          </div>
        )}

        {/* Flex Criteria Picker */}
        {showFlexPicker && flexMode && (
          <div className="card mb-4 animate-in" style={{
            padding: '16px 20px',
            border: '1px dashed rgba(124, 77, 255, 0.3)',
            background: 'var(--bg-secondary)',
          }}>
            <div className="flex items-center justify-between mb-3">
              <h4 style={{ fontSize: '0.9rem', fontWeight: 600, margin: 0 }}>📚 Flex Criteria Library</h4>
              <button onClick={() => setShowFlexPicker(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={18} />
              </button>
            </div>
            <div className="flex flex-col gap-2">
              {flexLibrary.map((fc) => (
                <div key={fc.name} className="flex items-center justify-between" style={{
                  padding: '10px 14px', borderRadius: 8,
                  background: fc.already_added ? 'rgba(38, 166, 154, 0.08)' : 'var(--bg-tertiary)',
                  border: fc.already_added ? '1px solid rgba(38, 166, 154, 0.2)' : '1px solid var(--border)',
                  opacity: fc.already_added ? 0.7 : 1,
                }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{fc.name}</div>
                    <div className="text-xs text-muted" style={{ marginTop: 2 }}>{fc.description}</div>
                  </div>
                  <div className="flex items-center gap-2" style={{ marginLeft: 12 }}>
                    {fc.category && (
                      <span className="badge" style={{
                        background: `${categoryColors[fc.category] || '#666'}20`,
                        color: categoryColors[fc.category] || '#666',
                        fontSize: '0.65rem',
                      }}>
                        {fc.category}
                      </span>
                    )}
                    {fc.already_added ? (
                      <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>
                        <CheckCircle2 size={10} /> Added
                      </span>
                    ) : (
                      <button
                        className="btn btn-primary"
                        disabled={adding === fc.name}
                        onClick={() => addFlexCriterion(fc)}
                        style={{ fontSize: '0.75rem', padding: '4px 10px', background: '#7c4dff' }}
                      >
                        {adding === fc.name ? <div className="loading-spinner" style={{ width: 14, height: 14 }} /> : <Plus size={12} />}
                        Add
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Core Criteria List */}
        <div className="flex flex-col gap-2">
          {coreCriteria.map((c, i) => (
            <div key={c.id} className="card animate-in" style={{ padding: '16px 20px', animationDelay: `${i * 40}ms` }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3" style={{flex:1}}>
                  <span style={{
                    width:24, height:24, borderRadius:'50%', display:'flex', alignItems:'center', justifyContent:'center',
                    background: 'var(--accent-glow)', color: 'var(--accent-primary)', fontSize:'0.7rem', fontWeight:700,
                  }}>{i+1}</span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span style={{fontWeight:600}}>{c.name}</span>
                      <Lock size={12} style={{ color: 'var(--text-muted)', opacity: 0.5 }} />
                    </div>
                    <div className="text-xs text-muted" style={{marginTop:2}}>{c.description}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
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
                          cursor: 'pointer', padding: '2px 8px', borderRadius: 12, fontSize: '0.7rem', fontWeight: 600,
                          background: `${OUTCOME_COLORS[field]}18`, color: OUTCOME_COLORS[field],
                          border: `1px solid ${OUTCOME_COLORS[field]}30`, whiteSpace: 'nowrap', transition: 'all 0.15s',
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

        {/* Flex Criteria Section */}
        {flexCriteria.length > 0 && (
          <>
            <div className="flex items-center gap-2 mt-6 mb-2" style={{ paddingLeft: 4 }}>
              <Zap size={16} style={{ color: '#f9a825' }} />
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#7c4dff' }}>Flex Criteria ({flexCriteria.length})</span>
              <div style={{ flex: 1, height: 1, background: 'rgba(124, 77, 255, 0.2)', marginLeft: 8 }} />
            </div>
            <div className="flex flex-col gap-2">
              {flexCriteria.map((c, i) => (
                <div key={c.id} className="card animate-in" style={{
                  padding: '16px 20px', animationDelay: `${i * 40}ms`,
                  borderLeft: '3px solid #7c4dff',
                }}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3" style={{flex:1}}>
                      <span style={{
                        width:24, height:24, borderRadius:'50%', display:'flex', alignItems:'center', justifyContent:'center',
                        background: 'rgba(124, 77, 255, 0.15)', color: '#7c4dff', fontSize:'0.7rem', fontWeight:700,
                      }}>{coreCriteria.length + i + 1}</span>
                      <div>
                        <div className="flex items-center gap-2">
                          <span style={{fontWeight:600}}>{c.name}</span>
                          <span className="badge" style={{ fontSize: '0.55rem', padding: '1px 5px', background: 'rgba(124, 77, 255, 0.15)', color: '#7c4dff' }}>FLEX</span>
                        </div>
                        <div className="text-xs text-muted" style={{marginTop:2}}>{c.description}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
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
                              cursor: 'pointer', padding: '2px 8px', borderRadius: 12, fontSize: '0.7rem', fontWeight: 600,
                              background: `${OUTCOME_COLORS[field]}18`, color: OUTCOME_COLORS[field],
                              border: `1px solid ${OUTCOME_COLORS[field]}30`, whiteSpace: 'nowrap', transition: 'all 0.15s',
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
                      {flexMode && (
                        <button
                          onClick={() => removeCriterion(c.id)}
                          title="Remove flex criterion"
                          style={{
                            background: 'rgba(239, 83, 80, 0.1)', border: '1px solid rgba(239, 83, 80, 0.2)',
                            borderRadius: 6, padding: '4px 6px', cursor: 'pointer',
                            color: '#ef5350', transition: 'all 0.15s',
                          }}
                        >
                          <Trash2 size={13} />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {criteria.length === 0 && (
          <div className="empty-state">
            <ListChecks size={48} />
            <h3>No criteria defined</h3>
            <p>Load the default criteria set or add custom criteria.</p>
          </div>
        )}

        {/* Summary */}
        <div className="flex items-center justify-between mt-4" style={{ padding: '8px 4px' }}>
          <span className="text-sm text-muted">{coreCriteria.length} core + {flexCriteria.length} flex = {criteria.length} total criteria</span>
          {flexCriteria.length > 0 && (
            <span className="text-xs text-muted" style={{ color: '#f9a825' }}>
              ⚠️ Adding flex criteria increases pairwise comparisons in the survey
            </span>
          )}
        </div>
      </div>
    </>
  );
}
