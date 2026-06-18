import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Plus, Trash2, GripVertical, RotateCcw, Save, Tag, ListChecks } from 'lucide-react';
import api from '../api/client';

export default function CriteriaBuilder() {
  const { projectId } = useParams();
  const [criteria, setCriteria] = useState([]);
  const [editing, setEditing] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [newCriterion, setNewCriterion] = useState({ name: '', description: '', category: '' });

  useEffect(() => { loadCriteria(); }, [projectId]);

  const loadCriteria = async () => {
    try { const { data } = await api.get(`/projects/${projectId}/criteria`); setCriteria(data); } catch(e) { console.error(e); }
  };

  const loadDefaults = async () => {
    if (!confirm('This will replace all existing criteria with the default set. Continue?')) return;
    try { await api.post(`/projects/${projectId}/criteria/defaults`); loadCriteria(); } catch(e) { console.error(e); }
  };

  const addCriterion = async () => {
    if (!newCriterion.name) return;
    try { await api.post(`/projects/${projectId}/criteria`, newCriterion); setNewCriterion({ name: '', description: '', category: '' }); setShowAdd(false); loadCriteria(); } catch(e) { console.error(e); }
  };

  const updateCriterion = async (id, updates) => {
    try { await api.patch(`/projects/${projectId}/criteria/${id}`, updates); setEditing(null); loadCriteria(); } catch(e) { console.error(e); }
  };

  const deleteCriterion = async (id) => {
    if (!confirm('Delete this criterion?')) return;
    try { await api.delete(`/projects/${projectId}/criteria/${id}`); loadCriteria(); } catch(e) { console.error(e); }
  };

  const categoryColors = { Strategic: '#42a5f5', Technical: '#7c4dff', Risk: '#ef5350', Governance: '#26a69a', Financial: '#f9a825', Organizational: '#ff7043', Operational: '#66bb6a' };

  return (
    <>
      <div className="page-header">
        <h2>Criteria Builder</h2>
        <p>Define the evaluation criteria for this assessment</p>
      </div>
      <div className="page-content">
        <div className="flex items-center justify-between mb-4">
          <div className="flex gap-2">
            <button className="btn btn-secondary" onClick={loadDefaults}><RotateCcw size={16} /> Load Defaults</button>
            <button className="btn btn-primary" onClick={() => setShowAdd(true)}><Plus size={16} /> Add Criterion</button>
          </div>
          <span className="text-sm text-muted">{criteria.length} criteria</span>
        </div>

        {/* Add form */}
        {showAdd && (
          <div className="card mb-4 animate-in">
            <h4 className="card-title">Add Custom Criterion</h4>
            <div className="grid grid-2 mt-4">
              <div className="form-group">
                <label className="form-label">Name *</label>
                <input className="form-input" value={newCriterion.name} onChange={e => setNewCriterion({...newCriterion, name: e.target.value})} placeholder="Criterion name" />
              </div>
              <div className="form-group">
                <label className="form-label">Category</label>
                <select className="form-select" value={newCriterion.category} onChange={e => setNewCriterion({...newCriterion, category: e.target.value})}>
                  <option value="">Select</option>
                  {Object.keys(categoryColors).map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea className="form-textarea" rows={2} value={newCriterion.description} onChange={e => setNewCriterion({...newCriterion, description: e.target.value})} placeholder="Describe what this criterion evaluates..." />
            </div>
            <div className="flex gap-2 justify-end">
              <button className="btn btn-ghost" onClick={() => setShowAdd(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={addCriterion} disabled={!newCriterion.name}><Save size={16} /> Save</button>
            </div>
          </div>
        )}

        {/* Criteria List */}
        <div className="flex flex-col gap-2">
          {criteria.map((c, i) => (
            <div key={c.id} className="card animate-in" style={{ padding: '16px 20px', animationDelay: `${i * 40}ms` }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3" style={{flex:1}}>
                  <GripVertical size={16} color="var(--text-tertiary)" style={{cursor:'grab'}} />
                  <span style={{
                    width:24, height:24, borderRadius:'50%', display:'flex', alignItems:'center', justifyContent:'center',
                    background: 'var(--accent-glow)', color: 'var(--accent-primary)', fontSize:'0.7rem', fontWeight:700,
                  }}>{i+1}</span>
                  {editing === c.id ? (
                    <input className="form-input" style={{maxWidth:300}} defaultValue={c.name}
                      onBlur={e => updateCriterion(c.id, { name: e.target.value })}
                      onKeyDown={e => e.key === 'Enter' && updateCriterion(c.id, { name: e.target.value })}
                      autoFocus
                    />
                  ) : (
                    <div>
                      <div style={{fontWeight:600, cursor:'pointer'}} onClick={() => setEditing(c.id)}>{c.name}</div>
                      <div className="text-xs text-muted" style={{marginTop:2}}>{c.description}</div>
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {c.category && (
                    <span className="badge" style={{
                      background: `${categoryColors[c.category] || '#666'}20`,
                      color: categoryColors[c.category] || '#666',
                    }}>
                      <Tag size={10} /> {c.category}
                    </span>
                  )}
                  {c.is_mandatory && <span className="badge badge-warning">Required</span>}
                  <button className="btn btn-icon btn-ghost" onClick={() => deleteCriterion(c.id)}><Trash2 size={14} /></button>
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
