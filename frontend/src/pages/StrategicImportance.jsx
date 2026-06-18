import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Shield, Plus, Trash2, AlertTriangle } from 'lucide-react';
import api from '../api/client';

export default function StrategicImportance() {
  const { projectId } = useParams();
  const [items, setItems] = useState([]);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({
    item_name: '', item_type: 'outcome', outcome: 'hybrid', strategic_importance: 0,
    justification: '', executive_sponsor: '', time_horizon: '', risk_of_not_acting: '', business_consequence: '', review_date: '',
  });

  useEffect(() => { loadItems(); }, [projectId]);

  const loadItems = async () => {
    try { const { data } = await api.get(`/projects/${projectId}/strategic-importance`); setItems(data); } catch(e) { console.error(e); }
  };

  const addItem = async () => {
    if (!form.item_name) return;
    try { await api.post(`/projects/${projectId}/strategic-importance`, form); setShowAdd(false); setForm({...form, item_name:'',strategic_importance:0,justification:''}); loadItems(); }
    catch(e) { alert(e.response?.data?.detail || 'Failed to save'); }
  };

  const deleteItem = async (id) => {
    if (!confirm('Remove this item?')) return;
    try { await api.delete(`/projects/${projectId}/strategic-importance/${id}`); loadItems(); } catch(e) { console.error(e); }
  };

  const siLabels = ['No override','Low','Low','Low','Moderate','Moderate','Moderate','High','High','Executive Priority','Critical Imperative'];
  const siColor = (v) => {
    if (v <= 3) return '#26a69a';
    if (v <= 6) return '#f9a825';
    if (v <= 8) return '#ff7043';
    return '#ef5350';
  };

  return (
    <>
      <div className="page-header">
        <h2>Strategic Importance</h2>
        <p>Override or boost scores based on executive strategic judgement</p>
      </div>
      <div className="page-content">
        <div className="alert alert-info mb-6">
          <Shield size={18} />
          <div>
            <strong>Transparency Rule:</strong> All strategic overrides are clearly documented in the final report.
            The tool separates the analytical AHP score from the strategic override, ensuring credibility.
          </div>
        </div>

        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold">Strategic Items</h3>
          <button className="btn btn-primary" onClick={() => setShowAdd(true)}><Plus size={16} /> Add Strategic Item</button>
        </div>

        {/* Add Form */}
        {showAdd && (
          <div className="card mb-4 animate-in">
            <h4 className="card-title mb-4">Add Strategic Importance Override</h4>
            <div className="grid grid-2">
              <div className="form-group"><label className="form-label">Item Name *</label>
                <input className="form-input" value={form.item_name} onChange={e => setForm({...form,item_name:e.target.value})} placeholder="e.g. Independent orchestration pilot" /></div>
              <div className="form-group"><label className="form-label">Type</label>
                <select className="form-select" value={form.item_type} onChange={e => setForm({...form,item_type:e.target.value})}>
                  <option value="outcome">Architecture Outcome</option><option value="initiative">Initiative</option><option value="project">Project</option>
                </select></div>
            </div>
            {form.item_type === 'outcome' && (
              <div className="form-group"><label className="form-label">Outcome</label>
                <select className="form-select" value={form.outcome} onChange={e => setForm({...form,outcome:e.target.value})}>
                  <option value="vendor">Strong Vendor Commitment</option>
                  <option value="hybrid">Hybrid AI Operating Model</option>
                  <option value="independent">Independent AI Control Model</option>
                </select></div>
            )}
            <div className="form-group">
              <label className="form-label">Strategic Importance (0-10): <strong style={{color:siColor(form.strategic_importance)}}>{form.strategic_importance} — {siLabels[form.strategic_importance]}</strong></label>
              <input type="range" min="0" max="10" value={form.strategic_importance} onChange={e => setForm({...form,strategic_importance:parseInt(e.target.value)})} />
            </div>

            {form.strategic_importance >= 7 && (
              <div className="animate-in" style={{background:'var(--bg-tertiary)',padding:16,borderRadius:'var(--radius-md)',marginBottom:16}}>
                <div className="flex items-center gap-2 mb-4"><AlertTriangle size={16} color="#f9a825" /> <span className="text-sm font-semibold" style={{color:'#f9a825'}}>Justification required for SI ≥ 7</span></div>
                <div className="grid grid-2">
                  <div className="form-group"><label className="form-label">Strategic Reason *</label><textarea className="form-textarea" rows={2} value={form.justification} onChange={e => setForm({...form,justification:e.target.value})} /></div>
                  <div className="form-group"><label className="form-label">Executive Sponsor *</label><input className="form-input" value={form.executive_sponsor} onChange={e => setForm({...form,executive_sponsor:e.target.value})} /></div>
                  <div className="form-group"><label className="form-label">Time Horizon *</label><input className="form-input" value={form.time_horizon} onChange={e => setForm({...form,time_horizon:e.target.value})} placeholder="e.g. 12 months" /></div>
                  <div className="form-group"><label className="form-label">Review Date *</label><input className="form-input" type="date" value={form.review_date} onChange={e => setForm({...form,review_date:e.target.value})} /></div>
                  <div className="form-group"><label className="form-label">Risk of Not Acting *</label><textarea className="form-textarea" rows={2} value={form.risk_of_not_acting} onChange={e => setForm({...form,risk_of_not_acting:e.target.value})} /></div>
                  <div className="form-group"><label className="form-label">Business Consequence *</label><textarea className="form-textarea" rows={2} value={form.business_consequence} onChange={e => setForm({...form,business_consequence:e.target.value})} /></div>
                </div>
              </div>
            )}
            <div className="flex gap-2 justify-end">
              <button className="btn btn-ghost" onClick={() => setShowAdd(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={addItem} disabled={!form.item_name}>Save</button>
            </div>
          </div>
        )}

        {/* Items List */}
        {items.length === 0 ? (
          <div className="empty-state"><Shield size={48} /><h3>No strategic overrides</h3><p>Add strategic importance items to override or boost scores.</p></div>
        ) : (
          <div className="flex flex-col gap-3">
            {items.map((item, i) => {
              const calc = item.score_calculation || {};
              return (
                <div key={item.id} className="card animate-in" style={{animationDelay:`${i*50}ms`}}>
                  <div className="flex items-center justify-between">
                    <div style={{flex:1}}>
                      <div className="flex items-center gap-3 mb-2">
                        <h4 style={{fontWeight:600}}>{item.item_name}</h4>
                        <span className="badge" style={{background:`${siColor(item.strategic_importance)}20`,color:siColor(item.strategic_importance)}}>
                          SI: {item.strategic_importance} — {item.label}
                        </span>
                      </div>
                      {calc.was_boosted && (
                        <div className="text-sm" style={{marginBottom:4}}>
                          Base: <strong>{calc.base_score?.toFixed(1)}</strong> → Final: <strong style={{color:'var(--accent-primary)'}}>{calc.final_score?.toFixed(1)}</strong>
                          <span className="text-muted"> (boost +{calc.boost}, {calc.floor ? `floor: ${calc.floor}` : 'no floor'})</span>
                        </div>
                      )}
                      {item.justification && <p className="text-xs text-muted">{item.justification}</p>}
                    </div>
                    <button className="btn btn-icon btn-ghost" onClick={() => deleteItem(item.id)}><Trash2 size={14} /></button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}
