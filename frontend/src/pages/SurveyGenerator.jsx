import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Download, FileSpreadsheet, Users, CheckCircle } from 'lucide-react';
import api from '../api/client';

export default function SurveyGenerator() {
  const { projectId } = useParams();
  const [criteria, setCriteria] = useState([]);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    api.get(`/projects/${projectId}/criteria`).then(r => setCriteria(r.data)).catch(console.error);
  }, [projectId]);

  const downloadTemplate = async () => {
    setDownloading(true);
    try {
      const response = await fetch(`/api/projects/${projectId}/generate-survey-template`, { method: 'POST' });
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AlphaAlign_Survey_Template.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch(e) { console.error(e); alert('Failed to generate template'); }
    setDownloading(false);
  };

  const tabs = ['Instructions', 'Respondent Profile', 'Pairwise Comparison', 'Alternative Scoring', 'Strategic Importance', 'Comments', 'Metadata'];

  return (
    <>
      <div className="page-header">
        <h2>Survey Template Generator</h2>
        <p>Generate an Excel survey template for leadership respondents</p>
      </div>
      <div className="page-content">
        <div className="card mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="card-title">Generate Excel Survey Template</h3>
              <p className="text-sm text-muted mt-2">
                The template includes all criteria and scoring sections. Send it to leadership respondents for completion.
              </p>
            </div>
            <button className="btn btn-primary btn-lg" onClick={downloadTemplate} disabled={criteria.length < 2 || downloading}>
              {downloading ? <div className="loading-spinner" /> : <Download size={20} />}
              {downloading ? 'Generating...' : 'Download Template'}
            </button>
          </div>
        </div>

        {criteria.length < 2 && (
          <div className="alert alert-warning mb-4">
            <AlertTriangle size={18} /> At least 2 criteria are required before generating a template. Go to the Criteria Builder first.
          </div>
        )}

        {/* Template Structure Preview */}
        <div className="card mb-6">
          <h3 className="card-title mb-4">Template Structure</h3>
          <p className="text-sm text-muted mb-4">The generated Excel file will contain {tabs.length} tabs:</p>
          <div className="flex flex-col gap-2">
            {tabs.map((tab, i) => (
              <div key={tab} className="flex items-center gap-3 animate-in" style={{ padding: '10px 14px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', animationDelay: `${i * 50}ms` }}>
                <span style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--accent-glow)', color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700 }}>{i+1}</span>
                <span style={{ fontWeight: 500 }}>{tab}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Criteria included */}
        <div className="card">
          <h3 className="card-title mb-4">
            <FileSpreadsheet size={18} style={{ display: 'inline', marginRight: 8 }} />
            Criteria Included ({criteria.length})
          </h3>
          <div className="table-container">
            <table>
              <thead><tr><th>#</th><th>Criterion</th><th>Category</th><th>Description</th></tr></thead>
              <tbody>
                {criteria.map((c, i) => (
                  <tr key={c.id}>
                    <td>{i+1}</td>
                    <td style={{fontWeight:500}}>{c.name}</td>
                    <td><span className="badge badge-neutral">{c.category || '—'}</span></td>
                    <td className="text-sm text-muted">{c.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Target Respondents */}
        <div className="card mt-4">
          <h3 className="card-title mb-4"><Users size={18} style={{display:'inline',marginRight:8}} /> Recommended Respondents</h3>
          <div className="grid grid-3">
            {['CEO', 'CFO', 'CIO / CTO', 'CISO', 'COO', 'CHRO', 'Business Unit Leaders', 'Data & AI Leaders', 'Enterprise Architects'].map(role => (
              <div key={role} className="flex items-center gap-2" style={{padding:'8px 12px', background:'var(--bg-tertiary)', borderRadius:'var(--radius-sm)'}}>
                <CheckCircle size={14} color="var(--success)" /> <span className="text-sm">{role}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

function AlertTriangle(props) {
  return <svg xmlns="http://www.w3.org/2000/svg" width={props.size||24} height={props.size||24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>;
}
