import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ListChecks, Users, FileSpreadsheet, Calculator, Target, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import api from '../api/client';

export default function ProjectDashboard() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [results, setResults] = useState(null);

  useEffect(() => { load(); }, [projectId]);

  const load = async () => {
    try {
      const { data } = await api.get(`/projects/${projectId}`);
      setProject(data);
      try {
        const { data: r } = await api.get(`/projects/${projectId}/ahp-results`);
        setResults(r);
      } catch {}
    } catch(e) { console.error(e); }
  };

  if (!project) return <div className="page-content"><div className="loading-spinner" /></div>;

  const steps = [
    { label: 'Criteria', done: project.criteria_count > 0, path: 'criteria', icon: ListChecks },
    { label: 'Survey', done: project.criteria_count > 0, path: 'survey', icon: FileSpreadsheet },
    { label: 'Upload', done: project.respondent_count > 0, path: 'upload', icon: Users },
    { label: 'Calculate', done: project.status === 'calculated', path: 'ahp', icon: Calculator },
    { label: 'Results', done: !!results, path: 'recommendation', icon: Target },
  ];

  const outcomeLabels = { vendor: 'Strong Vendor Commitment', hybrid: 'Hybrid AI Operating Model', independent: 'Independent AI Control Model' };
  const outcomeColors = { vendor: '#42a5f5', hybrid: '#26a69a', independent: '#7c4dff' };

  return (
    <>
      <div className="page-header">
        <h2>{project.name}</h2>
        <p>{project.company_name} {project.industry ? `· ${project.industry}` : ''}</p>
      </div>
      <div className="page-content">
        {/* Stats */}
        <div className="grid grid-4 mb-6">
          <div className="stat-card">
            <div className="stat-icon"><ListChecks size={22} /></div>
            <div><div className="stat-value">{project.criteria_count}</div><div className="stat-label">Criteria</div></div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{background:'rgba(38,166,154,0.15)',color:'#26a69a'}}><Users size={22} /></div>
            <div><div className="stat-value">{project.respondent_count}</div><div className="stat-label">Respondents</div></div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{background:'rgba(249,168,37,0.15)',color:'#f9a825'}}><Calculator size={22} /></div>
            <div><div className="stat-value">{project.status === 'calculated' ? '✓' : '—'}</div><div className="stat-label">AHP Status</div></div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{background:'rgba(124,77,255,0.15)',color:'#7c4dff'}}><Target size={22} /></div>
            <div>
              <div className="stat-value" style={{fontSize:'1rem'}}>
                {results ? results.recommendation?.recommended_label?.split(' ').slice(0,2).join(' ') : '—'}
              </div>
              <div className="stat-label">Recommendation</div>
            </div>
          </div>
        </div>

        {/* Workflow Steps */}
        <div className="card mb-6">
          <h3 className="card-title mb-4">Assessment Workflow</h3>
          <div className="flex gap-2" style={{alignItems:'center'}}>
            {steps.map((step, i) => (
              <div key={step.label} style={{flex:1, display:'flex', alignItems:'center', gap:8}}>
                <div
                  onClick={() => navigate(`/project/${projectId}/${step.path}`)}
                  style={{
                    flex:1, padding:'14px 16px', borderRadius:'var(--radius-md)',
                    background: step.done ? 'rgba(38,166,154,0.1)' : 'var(--bg-tertiary)',
                    border: `1px solid ${step.done ? 'rgba(38,166,154,0.3)' : 'var(--border-subtle)'}`,
                    cursor:'pointer', transition:'all var(--transition-fast)',
                    display:'flex', alignItems:'center', gap:10,
                  }}
                >
                  {step.done ? <CheckCircle2 size={18} color="#26a69a" /> : <Clock size={18} color="var(--text-tertiary)" />}
                  <div>
                    <div style={{fontSize:'0.85rem', fontWeight:600, color: step.done ? '#26a69a' : 'var(--text-secondary)'}}>{step.label}</div>
                  </div>
                </div>
                {i < steps.length - 1 && <div style={{width:20,height:2,background:'var(--border-subtle)',flexShrink:0}} />}
              </div>
            ))}
          </div>
        </div>

        {/* Results Preview */}
        {results && (
          <div className="card">
            <h3 className="card-title mb-4">Architecture Positioning Result</h3>
            <div className="grid grid-3">
              {Object.entries(outcomeLabels).map(([key, label]) => {
                const score = results.final_scores?.[key] || 0;
                const baseScore = results.outcome_scores?.[key] || 0;
                const isTop = results.recommendation?.recommended_outcome === key;
                return (
                  <div key={key} className="card animate-score" style={{
                    border: isTop ? '1px solid rgba(33,150,243,0.4)' : undefined,
                    boxShadow: isTop ? '0 0 30px rgba(33,150,243,0.15)' : undefined,
                    textAlign: 'center', padding: '32px 20px',
                  }}>
                    {isTop && <span className="badge badge-info mb-4" style={{marginBottom:12,display:'inline-flex'}}>★ Recommended</span>}
                    <div style={{ fontSize: '2.5rem', fontWeight: 800, color: outcomeColors[key], lineHeight: 1, marginBottom: 8 }}>
                      {score.toFixed(0)}
                    </div>
                    <div className="text-xs text-muted" style={{marginBottom:4}}>/ 100</div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: 4 }}>{label}</div>
                    {baseScore !== score && (
                      <div className="text-xs text-muted">Base: {baseScore.toFixed(0)} → Final: {score.toFixed(0)}</div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
