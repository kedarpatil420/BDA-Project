import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Zap,
  Search,
  CheckCircle2,
  XCircle,
  Terminal,
  Activity,
  Layers,
  HelpCircle
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

const BrutalistAlgoTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          backgroundColor: '#FFFFFF',
          border: '2.5px solid #000000',
          boxShadow: '3px 3px 0 #000000',
          padding: '8px 12px',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.8rem',
          fontWeight: 700,
        }}
      >
        <div style={{ color: '#000000', textTransform: 'uppercase', marginBottom: '2px' }}>
          {label}
        </div>
        <div style={{ color: '#000000' }}>
          ESTIMATE: <span style={{ color: '#FF3030' }}>{payload[0].value?.toLocaleString()}</span>
        </div>
        <div style={{ color: '#555555', marginTop: '2px' }}>
          ERROR: {payload[0].payload.error}%
        </div>
      </div>
    );
  }
  return null;
};

export default function Algorithms() {
  // Bloom Filter states
  const [bloomTitle, setBloomTitle] = useState('');
  const [bloomLoading, setBloomLoading] = useState(false);
  const [bloomResult, setBloomResult] = useState(null);
  const [bloomError, setBloomError] = useState(null);

  // Cardinality states
  const [cardinality, setCardinality] = useState(null);
  const [cardLoading, setCardLoading] = useState(true);
  const [cardError, setCardError] = useState(null);

  useEffect(() => {
    async function fetchCardinality() {
      try {
        setCardLoading(true);
        const res = await fetch('/api/cardinality');
        if (!res.ok) throw new Error('Failed to load cardinality results');
        const data = await res.json();
        setCardinality(data);
      } catch (err) {
        console.error(err);
        setCardError(err.message);
      } finally {
        setCardLoading(false);
      }
    }

    fetchCardinality();
  }, []);

  const handleBloomCheck = async (titleToCheck) => {
    const query = (titleToCheck !== undefined ? titleToCheck : bloomTitle).trim();
    if (!query) return;

    if (titleToCheck !== undefined) {
      setBloomTitle(titleToCheck);
    }

    try {
      setBloomLoading(true);
      setBloomError(null);
      const res = await fetch(`/api/bloom-check?title=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error('Bloom filter query failed');
      const data = await res.json();
      setBloomResult(data);
    } catch (err) {
      console.error(err);
      setBloomError(err.message);
    } finally {
      setBloomLoading(false);
    }
  };

  const sampleTitles = [
    { title: 'Squid Game', expected: 'present' },
    { title: 'Stranger Things', expected: 'present' },
    { title: 'Breaking Bad', expected: 'present' },
    { title: 'The Crown', expected: 'present' },
    { title: 'FakeShow_BDA_2099', expected: 'absent' },
    { title: 'NotANetflixTitle_XYZ', expected: 'absent' },
  ];

  const chartData = cardinality?.methods?.map((m) => ({
    name: m.method.replace('Flajolet-Martin', 'FM'),
    estimate: m.estimate,
    error: m.error_pct,
  })) || [];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">
          ALGORITHMS
        </h1>
        <p className="page-description">
          // PROBABILISTIC MEMBERSHIP TESTING & STREAM CARDINALITY ESTIMATION
        </p>
      </div>

      {/* SECTION 1: BLOOM FILTER */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <div className="algo-badge bloom">ALGO_01 // MEMBERSHIP TESTING</div>
            <h2 className="panel-title">
              <ShieldCheck size={20} strokeWidth={2.5} />
              BLOOM FILTER (DOUBLE HASHING)
            </h2>
            <div className="panel-subtitle">
              SPACE-EFFICIENT PROBABILISTIC SET MEMBERSHIP WITH ZERO FALSE NEGATIVES
            </div>
          </div>
        </div>

        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: '#222222', lineHeight: '1.6' }}>
          Queries whether a title is a member of the Netflix catalog using double hashing:
          <br />
          <code
            style={{
              display: 'inline-block',
              marginTop: '6px',
              backgroundColor: '#000000',
              color: '#00C781',
              padding: '6px 12px',
              border: '1.5px solid #000000',
              fontWeight: 700,
            }}
          >
            h_i(x) = (SHA256(x) + i * MD5(x)) mod m  &nbsp;[for i = 0 ... k-1]
          </code>
        </p>

        {/* Input bar */}
        <div className="search-box-group">
          <input
            type="text"
            className="input-primary"
            placeholder="ENTER TITLE TO QUERY (E.G. SQUID GAME, INCEPTION)..."
            value={bloomTitle}
            onChange={(e) => setBloomTitle(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleBloomCheck()}
          />
          <button
            className="btn-primary"
            onClick={() => handleBloomCheck()}
            disabled={bloomLoading || !bloomTitle.trim()}
          >
            <Search size={16} strokeWidth={2.5} />
            {bloomLoading ? 'TESTING...' : 'TEST BLOOM FILTER'}
          </button>
        </div>

        {/* Quick test buttons */}
        <div className="quick-tags">
          <span style={{ fontWeight: 800 }}>QUICK PRESETS:</span>
          {sampleTitles.map((item, idx) => (
            <button
              key={idx}
              className="quick-tag-btn"
              onClick={() => handleBloomCheck(item.title)}
            >
              {item.title} [{item.expected === 'present' ? '✓ IN CATALOG' : '✗ ABSENT'}]
            </button>
          ))}
        </div>

        {/* Live Result Display */}
        {bloomResult && (
          <div
            className={`result-box ${
              bloomResult.bloom_result ? 'probably-present' : 'definitely-absent'
            }`}
          >
            <div className="result-header">
              <div className="result-status">
                {bloomResult.bloom_result ? (
                  <>
                    <CheckCircle2 size={24} strokeWidth={2.5} className="status-present" />
                    <span className="status-present">
                      RESULT: POSSIBLY PRESENT (PROBABLY IN SET)
                    </span>
                  </>
                ) : (
                  <>
                    <XCircle size={24} strokeWidth={2.5} className="status-absent" />
                    <span className="status-absent">
                      RESULT: DEFINITELY ABSENT (NOT IN SET)
                    </span>
                  </>
                )}
              </div>
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.75rem',
                  fontWeight: 800,
                  padding: '4px 8px',
                  border: '1.5px solid #000000',
                  backgroundColor: '#FFFFFF',
                  boxShadow: '2px 2px 0 #000'
                }}
              >
                GROUND_TRUTH: {bloomResult.exact_in_dataset ? 'FOUND IN CATALOG' : 'NOT IN CATALOG'}
              </div>
            </div>

            <p className="result-explanation">
              <strong>QUERY_TITLE:</strong> "{bloomResult.title}"
              <br />
              <strong>INTERPRETATION:</strong> {bloomResult.explanation}
            </p>

            {/* Filter Specs */}
            {bloomResult.filter_info && (
              <div className="meta-grid" style={{ marginTop: '16px' }}>
                <div className="meta-item">
                  <div className="meta-label">BIT ARRAY SIZE (m)</div>
                  <div className="meta-val">{bloomResult.filter_info.bit_array_size_bits.toLocaleString()} BITS</div>
                </div>
                <div className="meta-item">
                  <div className="meta-label">MEMORY FOOTPRINT</div>
                  <div className="meta-val">{(bloomResult.filter_info.bit_array_size_bytes / 1024).toFixed(1)} KB</div>
                </div>
                <div className="meta-item">
                  <div className="meta-label">HASH FUNCTIONS (k)</div>
                  <div className="meta-val">{bloomResult.filter_info.num_hash_functions} HASHES</div>
                </div>
                <div className="meta-item">
                  <div className="meta-label">TARGET / ACTUAL FPR</div>
                  <div className="meta-val">
                    {bloomResult.filter_info.target_fpr_pct}% / {bloomResult.filter_info.actual_fpr_pct}%
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* SECTION 2: CARDINALITY ESTIMATION */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <div className="algo-badge cardinality">ALGO_02 // STREAM CARDINALITY</div>
            <h2 className="panel-title">
              <Zap size={20} strokeWidth={2.5} />
              CARDINALITY ESTIMATION (FLAJOLET-MARTIN & HYPERLOGLOG)
            </h2>
            <div className="panel-subtitle">
              DISTINCT COUNT ESTIMATION OVER STREAMING DATA WITHOUT SET STORAGE
            </div>
          </div>
        </div>

        {cardLoading ? (
          <div className="loading-box">
            <div className="spinner"></div>
            <p>[COMPUTING HASH RUNS & REGISTER AGGREGATIONS...]</p>
          </div>
        ) : cardError ? (
          <p style={{ color: 'var(--accent-red)', fontFamily: 'var(--font-mono)' }}>ERROR: {cardError}</p>
        ) : (
          <>
            {/* Comparison Cards */}
            <div className="cardinality-grid">
              {cardinality?.methods?.map((m, idx) => {
                const isExact = idx === 0;

                return (
                  <div
                    key={idx}
                    className={`cardinality-card ${isExact ? 'highlight' : ''}`}
                  >
                    <div className="cardinality-method">{m.method}</div>
                    <div className="cardinality-estimate">
                      {m.estimate?.toLocaleString()}
                    </div>
                    <div>
                      {isExact ? (
                        <span className="cardinality-error error-zero">
                          GROUND TRUTH (0.00% ERROR)
                        </span>
                      ) : (
                        <span
                          className={`cardinality-error ${
                            m.error_pct < 10 ? 'error-low' : 'error-high'
                          }`}
                        >
                          ERROR: {m.error_pct}%
                        </span>
                      )}
                    </div>
                    <div className="cardinality-desc">{m.description}</div>
                  </div>
                );
              })}
            </div>

            {/* Visual Comparison Chart */}
            <div style={{ marginTop: '28px' }}>
              <div className="panel-header" style={{ marginBottom: '14px' }}>
                <h3 className="panel-title" style={{ fontSize: '1rem' }}>
                  ACCURACY BENCHMARK (GROUND TRUTH VS APPROXIMATIONS)
                </h3>
              </div>
              <div style={{ height: 280, width: '100%' }}>
                <ResponsiveContainer>
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="2 2" stroke="#CCCCCC" />
                    <XAxis
                      dataKey="name"
                      stroke="#000000"
                      strokeWidth={1.5}
                      tick={{ fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 700 }}
                    />
                    <YAxis
                      stroke="#000000"
                      strokeWidth={1.5}
                      tick={{ fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 700 }}
                      domain={[0, (dataMax) => Math.max(dataMax + 1000, 10000)]}
                    />
                    <Tooltip content={<BrutalistAlgoTooltip />} />
                    <Bar dataKey="estimate" stroke="#000000" strokeWidth={1.5}>
                      {chartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={
                            index === 0
                              ? '#00C781' // Ground truth green
                              : index === 1
                              ? '#FF3030' // Single run high variance red
                              : index === 2
                              ? '#A78BFA' // Multi run purple
                              : '#38BDF8' // HLL blue
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Academic Analysis Note */}
            <div
              style={{
                marginTop: '24px',
                padding: '16px 20px',
                backgroundColor: '#000000',
                color: '#FFFFFF',
                border: 'var(--border-thick)',
                boxShadow: 'var(--shadow-standard)',
                fontSize: '0.8rem',
                fontFamily: 'var(--font-mono)',
                lineHeight: '1.6'
              }}
            >
              <div style={{ color: '#00C781', fontWeight: 800, marginBottom: '6px' }}>
                [THEORETICAL ANALYSIS // BIAS CORRECTION IN LOG-SPACE]
              </div>
              Notice how the <strong>Single-Run Flajolet-Martin</strong> estimator suffers from high discrete variance because its estimate is strictly constrained to powers of two (&phi; &times; 2<sup>R</sup>). In contrast, the <strong>Multi-Run FM</strong> leverages 32 independent trials with <em>log-space averaging</em> across groups of trials:
              <br />
              <code style={{ backgroundColor: '#222', color: '#FCD34D', padding: '2px 6px', display: 'inline-block', marginTop: '4px' }}>
                R* = median(mean(R_i))
              </code> followed by single exponentiation &phi; &times; 2<sup>R*</sup>. This eliminates exponential outlier skew, reducing the estimation error to just a few percent!
            </div>
          </>
        )}
      </div>
    </div>
  );
}
