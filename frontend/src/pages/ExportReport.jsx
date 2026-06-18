import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Download, FileText, Table, FileJson, CheckCircle } from 'lucide-react';

export default function ExportReport() {
  const { projectId } = useParams();
  const [exporting, setExporting] = useState(null);

  const exportFile = async (format) => {
    setExporting(format);
    try {
      const response = await fetch(`/api/projects/${projectId}/export/${format}`);
      if (format === 'json') {
        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        downloadBlob(blob, `AlphaAlign_Export.json`);
      } else {
        const blob = await response.blob();
        const ext = format === 'pdf' ? 'pdf' : 'xlsx';
        downloadBlob(blob, `AlphaAlign_Report.${ext}`);
      }
    } catch(e) { alert('Export failed'); }
    setExporting(null);
  };

  const downloadBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
  };

  const formats = [
    { key: 'pdf', label: 'PDF Report', desc: 'Professional report with scoring tables, criteria weights, and recommendations.', icon: FileText, color: '#ef5350' },
    { key: 'excel', label: 'Excel Workbook', desc: 'Multi-tab workbook with raw data, scores, weights, and analysis results.', icon: Table, color: '#26a69a' },
    { key: 'json', label: 'JSON Archive', desc: 'Full project data export for backup, import, or integration.', icon: FileJson, color: '#42a5f5' },
  ];

  return (
    <>
      <div className="page-header">
        <h2>Export Report</h2>
        <p>Download assessment results in various formats</p>
      </div>
      <div className="page-content">
        <div className="grid grid-3">
          {formats.map((f, i) => (
            <div key={f.key} className="card animate-in" style={{ textAlign: 'center', padding: '40px 24px', animationDelay: `${i * 80}ms` }}>
              <div style={{
                width: 64, height: 64, borderRadius: 'var(--radius-lg)', margin: '0 auto 16px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: `${f.color}15`, color: f.color,
              }}>
                <f.icon size={28} />
              </div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 8 }}>{f.label}</h3>
              <p className="text-sm text-muted" style={{ marginBottom: 20, minHeight: 48 }}>{f.desc}</p>
              <button className="btn btn-primary w-full" onClick={() => exportFile(f.key)} disabled={exporting === f.key}>
                {exporting === f.key ? <div className="loading-spinner" /> : <Download size={16} />}
                {exporting === f.key ? 'Exporting...' : 'Download'}
              </button>
            </div>
          ))}
        </div>

        <div className="card mt-6">
          <h4 className="card-title mb-2">Report Contents</h4>
          <p className="text-sm text-muted mb-4">The PDF and Excel reports include:</p>
          <div className="grid grid-2">
            {[
              'Executive Summary', 'Architecture Positioning Result',
              'Criteria Weighting Table', 'Leadership Alignment Analysis',
              'Strategic Importance Appendix', 'Recommended Roadmap',
              'Respondent Consistency Ratios', 'Methodology Notes'
            ].map(item => (
              <div key={item} className="flex items-center gap-2" style={{padding:'6px 0'}}>
                <CheckCircle size={14} color="var(--success)" /> <span className="text-sm">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
