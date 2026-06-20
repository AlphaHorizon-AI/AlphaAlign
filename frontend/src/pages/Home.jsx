import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, FolderOpen, Sparkles, ArrowRight, Building2, Calendar, Trash2 } from 'lucide-react';
import api from '../api/client';

export default function Home() {
  const [projects, setProjects] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: '', company_name: '', industry: '', owner: '', time_horizon: '', ai_ambition: '', primary_vendor: '', description: '' });
  const navigate = useNavigate();

  useEffect(() => { loadProjects(); }, []);

  useEffect(() => {
    const handler = async () => {
      // Auto-fill from global settings
      try {
        const { data } = await api.get('/settings');
        setForm(f => ({
          ...f,
          company_name: f.company_name || data.company_name || '',
          industry: f.industry || data.industry || '',
          primary_vendor: f.primary_vendor || data.primary_vendor_ecosystem || '',
          owner: f.owner || data.primary_contact || '',
        }));
      } catch {}
      setShowModal(true);
    };
    window.addEventListener('open-create-modal', handler);
    return () => window.removeEventListener('open-create-modal', handler);
  }, []);

  const loadProjects = async () => {
    try { const { data } = await api.get('/projects'); setProjects(data); } catch(e) { console.error(e); }
  };

  const createProject = async () => {
    if (!form.name || !form.company_name) return;
    try {
      const { data } = await api.post('/projects', form);
      navigate(`/project/${data.id}`);
    } catch(e) { console.error(e); }
  };

  const deleteProject = async (e, id) => {
    e.stopPropagation();
    if (!confirm('Delete this assessment?')) return;
    try { await api.delete(`/projects/${id}`); loadProjects(); } catch(e) { console.error(e); }
  };

  const statusColors = { draft: 'badge-neutral', calculated: 'badge-success', in_progress: 'badge-info' };

  return (
    <>
      <div className="page-header">
        <h2>AlphaAlign</h2>
        <p>Strategic AI Choice Engine — Leadership decision support for AI architecture positioning</p>
      </div>
      <div className="page-content">
        {/* Hero */}
        <div className="card mb-6" style={{
          background: 'linear-gradient(135deg, rgba(33,150,243,0.08) 0%, rgba(13,13,21,0.95) 100%)',
          border: '1px solid rgba(33,150,243,0.15)',
          textAlign: 'center',
          padding: '48px 32px',
        }}>
          <img src="/logo.png" alt="AlphaAlign" style={{ width: 80, height: 80, margin: '0 auto 20px', display: 'block', filter: 'drop-shadow(0 0 20px rgba(33,150,243,0.4))' }} />
          <h2 style={{ fontSize: '1.5rem', marginBottom: 8 }}>Strategic AI Architecture Assessment</h2>
          <p className="text-muted" style={{ maxWidth: 600, margin: '0 auto 24px' }}>
            Help your leadership team make an intentional strategic choice between
            Strong Vendor Commitment, Hybrid AI Operating Model, or Independent AI Control.
          </p>
          <button className="btn btn-primary btn-lg" onClick={() => window.dispatchEvent(new CustomEvent('open-create-modal'))}>
            <Plus size={20} /> Create New Assessment
          </button>
        </div>

        {/* Projects */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Recent Assessments</h3>
          <span className="text-xs text-muted">{projects.length} assessment{projects.length !== 1 ? 's' : ''}</span>
        </div>

        {projects.length === 0 ? (
          <div className="empty-state">
            <FolderOpen size={48} />
            <h3>No assessments yet</h3>
            <p>Create your first assessment to get started.</p>
          </div>
        ) : (
          <div className="grid grid-auto">
            {projects.map(p => (
              <div key={p.id} className="card" style={{ cursor: 'pointer' }} onClick={() => navigate(`/project/${p.id}`)}>
                <div className="card-header">
                  <span className={`badge ${statusColors[p.status] || 'badge-neutral'}`}>{p.status}</span>
                  <button className="btn btn-icon btn-ghost" onClick={(e) => deleteProject(e, p.id)}><Trash2 size={14} /></button>
                </div>
                <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 4 }}>{p.name}</h4>
                <div className="flex items-center gap-2 text-sm text-muted" style={{ marginBottom: 12 }}>
                  <Building2 size={14} /> {p.company_name}
                </div>
                <div className="flex items-center gap-4 text-xs text-muted">
                  <span>{p.criteria_count} criteria</span>
                  <span>{p.respondent_count} respondent{p.respondent_count !== 1 ? 's' : ''}</span>
                </div>
                <div className="flex items-center justify-between mt-4">
                  <span className="text-xs text-muted">
                    <Calendar size={12} style={{ display: 'inline', marginRight: 4 }} />
                    {new Date(p.created_at).toLocaleDateString()}
                  </span>
                  <ArrowRight size={16} className="text-accent" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3 className="modal-title">Create New Assessment</h3>
            <div className="form-group">
              <label className="form-label">Assessment Name *</label>
              <input className="form-input" placeholder="e.g. AI Architecture Strategic Choice 2026" value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Company Name *</label>
              <input className="form-input" placeholder="e.g. Acme Corporation" value={form.company_name} onChange={e => setForm({...form, company_name: e.target.value})} />
            </div>
            <div className="grid grid-2">
              <div className="form-group">
                <label className="form-label">Industry</label>
                <select className="form-select" value={form.industry} onChange={e => setForm({...form, industry: e.target.value})}>
                  <option value="">Select industry</option>
                  <option>Manufacturing</option><option>Financial Services</option>
                  <option>Healthcare</option><option>Technology</option><option>Retail</option>
                  <option>Energy</option><option>Government</option><option>Education</option>
                  <option>Professional Services</option><option>Other</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Assessment Owner</label>
                <input className="form-input" placeholder="Your name" value={form.owner} onChange={e => setForm({...form, owner: e.target.value})} />
              </div>
            </div>
            <div className="grid grid-2">
              <div className="form-group">
                <label className="form-label">Time Horizon</label>
                <select className="form-select" value={form.time_horizon} onChange={e => setForm({...form, time_horizon: e.target.value})}>
                  <option value="">Select</option>
                  <option>6 months</option><option>12 months</option>
                  <option>18 months</option><option>24 months</option><option>36 months</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">AI Ambition Level</label>
                <select className="form-select" value={form.ai_ambition} onChange={e => setForm({...form, ai_ambition: e.target.value})}>
                  <option value="">Select</option>
                  <option>Exploratory</option><option>Operational</option>
                  <option>Strategic</option><option>Transformational</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Primary Vendor Ecosystem</label>
              <input className="form-input" placeholder="e.g. Microsoft, SAP, Google, AWS" value={form.primary_vendor} onChange={e => setForm({...form, primary_vendor: e.target.value})} />
            </div>
            <div className="form-group">
              <label className="form-label">Notes</label>
              <textarea className="form-textarea" rows={2} placeholder="Optional context..." value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
            </div>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={createProject} disabled={!form.name || !form.company_name}>
                <Sparkles size={16} /> Create Assessment
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
