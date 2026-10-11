import React, { useState, useEffect } from 'react';
import { FileText, Download, AlertTriangle, BookOpen, CheckCircle, Terminal } from 'lucide-react';

export default function Reports() {
  const [reportInfo, setReportInfo] = useState({ available: false, size_bytes: 0 });
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    async function checkReport() {
      try {
        setChecking(true);
        // Dedicated lightweight status check
        const statusRes = await fetch('/api/report/status');
        if (statusRes.ok) {
          const data = await statusRes.json();
          setReportInfo({
            available: Boolean(data.available),
            size_bytes: data.size_bytes || 0,
          });
          return;
        }

        // Fallback: check HEAD on /api/report
        const headRes = await fetch('/api/report', { method: 'HEAD' });
        const contentLength = parseInt(headRes.headers.get('content-length') || '0', 10);
        setReportInfo({
          available: headRes.ok,
          size_bytes: contentLength,
        });
      } catch (err) {
        try {
          const headRes = await fetch('/api/report', { method: 'HEAD' });
          setReportInfo({
            available: headRes.ok,
            size_bytes: 0,
          });
        } catch {
          setReportInfo({ available: false, size_bytes: 0 });
        }
      } finally {
        setChecking(false);
      }
    }

    checkReport();
  }, []);

  const chapters = [
    { num: 1, title: 'Introduction & Project Overview', desc: 'Background of Big Data streaming challenges and algorithm objectives.' },
    { num: 2, title: 'Dataset Description & Preprocessing', desc: 'Netflix catalog hygiene, duration parsing, rating swapping corrections.' },
    { num: 3, title: 'BDA Algorithm Design', desc: 'Mathematical formulations for Bloom Filters, Flajolet-Martin, and HyperLogLog.' },
    { num: 4, title: 'Results & Empirical Analysis', desc: 'Accuracy benchmarks, error convergence, and distribution visualisations.' },
    { num: 5, title: 'Conclusion & Future Scope', desc: 'Key insights and trade-offs between space complexity and estimation error.' }
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">
          REPORTS & PDF
        </h1>
        <p className="page-description">
          // PUBLICATION-GRADE TECHNICAL COMPILATION & ARCHITECTURAL DOCUMENTATION
        </p>
      </div>

      <div className="panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  backgroundColor: '#FF3030',
                  color: '#FFFFFF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: 'var(--border-standard)',
                  boxShadow: '2px 2px 0 #000'
                }}
              >
                <FileText size={24} strokeWidth={2.5} />
              </div>
              <div>
                <h2 style={{ fontSize: '1.3rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '-0.01em' }}>
                  NETFLIX BDA FINAL ACADEMIC REPORT (PDF)
                </h2>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#555555', marginTop: '4px' }}>
                  FILE_PATH: <code style={{ backgroundColor: '#000000', color: '#38BDF8', padding: '2px 6px' }}>output/netflix_report.pdf</code>
                  {reportInfo.size_bytes > 0 && (
                    <span
                      style={{
                        marginLeft: '8px',
                        backgroundColor: '#00C781',
                        color: '#000000',
                        fontWeight: 800,
                        padding: '2px 6px',
                        border: '1px solid #000'
                      }}
                    >
                      [SIZE: {(reportInfo.size_bytes / 1024).toFixed(0)} KB]
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div>
            {checking ? (
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 700 }}>
                [CHECKING PDF TELEMETRY...]
              </span>
            ) : reportInfo.available ? (
              <a
                href="/api/report"
                download="netflix_report.pdf"
                className="btn-primary"
                style={{
                  backgroundColor: '#FF3030',
                  color: '#FFFFFF',
                  fontSize: '0.9rem',
                  padding: '14px 24px',
                  boxShadow: 'var(--shadow-standard)'
                }}
              >
                <Download size={18} strokeWidth={2.5} />
                DOWNLOAD PDF REPORT
              </a>
            ) : (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  backgroundColor: '#FEF3C7',
                  border: '2px solid #000000',
                  padding: '8px 14px',
                  boxShadow: '2px 2px 0 #000',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.8rem',
                  fontWeight: 800
                }}
              >
                <AlertTriangle size={18} color="#D97706" strokeWidth={2.5} />
                <span>REPORT NOT GENERATED YET. RUN <code>python main.py</code></span>
              </div>
            )}
          </div>
        </div>

        <hr style={{ border: 'none', borderTop: 'var(--border-standard)', margin: '24px 0' }} />

        <div className="panel-header" style={{ marginBottom: '16px' }}>
          <h3 className="panel-title" style={{ fontSize: '1.05rem' }}>
            REPORT CHAPTER COMPILATION (REPORTLAB PLATYPUS ENGINE)
          </h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {chapters.map((ch) => (
            <div
              key={ch.num}
              style={{
                backgroundColor: '#FFFFFF',
                border: 'var(--border-standard)',
                boxShadow: 'var(--shadow-small)',
                padding: '18px',
                transition: 'all 0.15s ease'
              }}
            >
              <div
                style={{
                  display: 'inline-block',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.7rem',
                  fontWeight: 800,
                  backgroundColor: ch.num === 1 ? '#FCD34D' : ch.num === 2 ? '#38BDF8' : ch.num === 3 ? '#A78BFA' : ch.num === 4 ? '#FF3030' : '#00C781',
                  color: ch.num === 4 ? '#FFFFFF' : '#000000',
                  padding: '2px 6px',
                  border: '1.5px solid #000000',
                  boxShadow: '1.5px 1.5px 0 #000',
                  marginBottom: '8px'
                }}
              >
                CHAPTER 0{ch.num}
              </div>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1rem', fontWeight: 800, color: '#000000', margin: '4px 0', textTransform: 'uppercase' }}>
                {ch.title}
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: '#555555', lineHeight: '1.5', marginTop: '6px' }}>
                {ch.desc}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
