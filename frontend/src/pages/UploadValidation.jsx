import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Upload, CheckCircle2, XCircle, AlertTriangle, FileSpreadsheet, Trash2 } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import api from '../api/client';

export default function UploadValidation() {
  const { projectId } = useParams();
  const [surveys, setSurveys] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  useEffect(() => { loadSurveys(); }, [projectId]);

  const loadSurveys = async () => {
    try { const { data } = await api.get(`/projects/${projectId}/surveys`); setSurveys(data); } catch(e) { console.error(e); }
  };

  const onDrop = useCallback(async (files) => {
    for (const file of files) {
      setUploading(true);
      setUploadResult(null);
      const formData = new FormData();
      formData.append('file', file);
      try {
        const { data } = await api.post(`/projects/${projectId}/upload-survey`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setUploadResult(data);
        loadSurveys();
      } catch(e) {
        setUploadResult({ status: 'error', errors: [e.response?.data?.detail || 'Upload failed'] });
      }
      setUploading(false);
    }
  }, [projectId]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'] },
    multiple: true,
  });

  const deleteRespondent = async (id) => {
    if (!confirm('Remove this respondent and their data?')) return;
    try { await api.delete(`/projects/${projectId}/respondents/${id}`); loadSurveys(); } catch(e) { console.error(e); }
  };

  const statusIcon = (status) => {
    if (status === 'valid') return <CheckCircle2 size={16} color="#26a69a" />;
    if (status === 'invalid') return <XCircle size={16} color="#ef5350" />;
    return <AlertTriangle size={16} color="#f9a825" />;
  };

  return (
    <>
      <div className="page-header">
        <h2>Upload & Validation</h2>
        <p>Upload completed survey files and validate responses</p>
      </div>
      <div className="page-content">
        {/* Upload Zone */}
        <div {...getRootProps()} className={`upload-zone mb-6 ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} />
          {uploading ? (
            <><div className="loading-spinner" style={{margin:'0 auto 12px'}} /><p>Processing survey file...</p></>
          ) : (
            <>
              <Upload size={48} />
              <p><span className="upload-highlight">Click to upload</span> or drag and drop completed survey files</p>
              <p className="text-xs text-muted mt-2">Accepts .xlsx files</p>
            </>
          )}
        </div>

        {/* Upload Result */}
        {uploadResult && (
          <div className={`alert mb-4 ${uploadResult.status === 'valid' ? 'alert-success' : uploadResult.status === 'error' ? 'alert-error' : 'alert-warning'}`}>
            <div>
              {uploadResult.status === 'valid' && (
                <><strong>✓ Survey accepted:</strong> {uploadResult.respondent_name} ({uploadResult.respondent_role || 'No role'}) — {uploadResult.pairwise_count} pairwise comparisons, {uploadResult.alternative_score_count} alternative scores</>
              )}
              {uploadResult.status === 'invalid' && (
                <><strong>✗ Validation failed:</strong><ul style={{marginTop:4}}>{uploadResult.errors?.map((e,i) => <li key={i}>{e}</li>)}</ul></>
              )}
              {uploadResult.status === 'error' && (
                <><strong>Error:</strong> {uploadResult.errors?.join(', ')}</>
              )}
              {uploadResult.warnings?.length > 0 && (
                <div style={{marginTop:8,opacity:0.8}}><strong>Warnings:</strong><ul>{uploadResult.warnings.map((w,i) => <li key={i}>{w}</li>)}</ul></div>
              )}
            </div>
          </div>
        )}

        {/* Uploaded Surveys */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title"><FileSpreadsheet size={18} style={{display:'inline',marginRight:8}} /> Uploaded Surveys ({surveys.length})</h3>
          </div>
          {surveys.length === 0 ? (
            <div className="empty-state" style={{padding:'32px 16px'}}>
              <p className="text-muted">No surveys uploaded yet. Upload completed Excel files above.</p>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead><tr><th>Status</th><th>Respondent</th><th>Role</th><th>File</th><th>CR</th><th>Uploaded</th><th></th></tr></thead>
                <tbody>
                  {surveys.map(s => (
                    <tr key={s.id}>
                      <td>{statusIcon(s.status)}</td>
                      <td style={{fontWeight:500}}>{s.name}</td>
                      <td><span className="badge badge-neutral">{s.role || '—'}</span></td>
                      <td className="text-sm text-muted">{s.file}</td>
                      <td>
                        {s.consistency_ratio !== null ? (
                          <span className={`badge ${s.consistency_ratio <= 0.1 ? 'badge-success' : s.consistency_ratio <= 0.2 ? 'badge-warning' : 'badge-error'}`}>
                            {s.consistency_ratio?.toFixed(3)}
                          </span>
                        ) : '—'}
                      </td>
                      <td className="text-sm text-muted">{new Date(s.created_at).toLocaleDateString()}</td>
                      <td><button className="btn btn-icon btn-ghost" onClick={() => deleteRespondent(s.id)}><Trash2 size={14} /></button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
