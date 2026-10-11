import React, { useState, useEffect } from 'react';
import {
  Film,
  Tv,
  Layers,
  Sparkles,
  Globe,
  Calendar,
  Terminal,
  Activity,
  Sliders
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  AreaChart,
  Area,
  Legend
} from 'recharts';

const TYPE_COLORS = ['#FF3030', '#A78BFA'];
const BAR_COUNTRY_COLOR = '#FF3030';
const BAR_GENRE_COLOR = '#A78BFA';

// Neo-Brutalist Custom Tooltip
const BrutalistTooltip = ({ active, payload, label }) => {
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
        <div style={{ color: '#000000', marginBottom: '2px', textTransform: 'uppercase' }}>
          {label || payload[0].name}
        </div>
        <div style={{ color: '#FF3030' }}>
          COUNT: {payload[0].value?.toLocaleString()}
        </div>
      </div>
    );
  }
  return null;
};

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [sumRes, anaRes] = await Promise.all([
          fetch('/api/summary'),
          fetch('/api/analytics'),
        ]);

        if (!sumRes.ok || !anaRes.ok) {
          throw new Error('Failed to fetch data from API');
        }

        const sumData = await sumRes.json();
        const anaData = await anaRes.json();

        setSummary(sumData);
        setAnalytics(anaData);
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="loading-box">
        <div className="spinner"></div>
        <p>[FETCHING CATALOG DATA & RUNNING BDA ENGINE...]</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel" style={{ border: '3px solid #FF3030', backgroundColor: '#FEEEEE' }}>
        <h3 style={{ color: '#FF3030', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>
          [ERROR: BACKEND_CONNECTION_FAILED]
        </h3>
        <p style={{ marginTop: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
          Could not communicate with FastAPI server. Ensure `python backend/api.py` is active on port 8000.
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Prominent Heading */}
      <div className="page-header">
        <h1 className="page-title">
          NETFLIX CONTENT ANALYTICS
        </h1>
        <p className="page-description">
          // PROBABILISTIC STREAMING & HIGH-DIMENSIONAL CATALOG TELEMETRY
        </p>
      </div>

      {/* Terminal-style status strip */}
      <div className="terminal-strip">
        <span>
          <Terminal size={14} color="#00C781" />
          SYSTEM_STATUS: <span className="strip-tag">ONLINE</span>
        </span>
        <span>
          HOST: <span className="strip-tag">127.0.0.1:8000</span>
        </span>
        <span>
          DATASET: <span className="strip-tag yellow">NETFLIX_TITLES.CSV</span>
        </span>
        <span>
          TOTAL_RECORDS: <span className="strip-tag purple">{summary?.total_titles?.toLocaleString()}</span>
        </span>
        <span>
          YEAR_RANGE: <span className="strip-tag">{summary?.min_year} - {summary?.max_year}</span>
        </span>
      </div>

      {/* Metric Cards */}
      <div className="kpi-grid">
        {/* Total Titles */}
        <div className="kpi-card dark">
          <div className="kpi-header">
            <span className="kpi-title">TOTAL TITLES</span>
            <div className="kpi-icon-wrapper">
              <Layers size={18} strokeWidth={2.5} />
            </div>
          </div>
          <div className="kpi-value">{summary?.total_titles?.toLocaleString()}</div>
          <div className="kpi-subtitle">CLEANED CATALOG RECORDS</div>
        </div>

        {/* Movies */}
        <div className="kpi-card red">
          <div className="kpi-header">
            <span className="kpi-title">MOVIES</span>
            <div className="kpi-icon-wrapper" style={{ backgroundColor: '#FF3030', color: '#FFF' }}>
              <Film size={18} strokeWidth={2.5} />
            </div>
          </div>
          <div className="kpi-value" style={{ color: '#FF3030' }}>
            {summary?.num_movies?.toLocaleString()}
          </div>
          <div className="kpi-subtitle">
            {summary?.total_titles ? ((summary.num_movies / summary.total_titles) * 100).toFixed(1) : 0}% OF ALL CONTENT
          </div>
        </div>

        {/* TV Shows */}
        <div className="kpi-card purple">
          <div className="kpi-header">
            <span className="kpi-title">TV SHOWS</span>
            <div className="kpi-icon-wrapper" style={{ backgroundColor: '#A78BFA', color: '#000' }}>
              <Tv size={18} strokeWidth={2.5} />
            </div>
          </div>
          <div className="kpi-value" style={{ color: '#7C3AED' }}>
            {summary?.num_tv_shows?.toLocaleString()}
          </div>
          <div className="kpi-subtitle">
            {summary?.total_titles ? ((summary.num_tv_shows / summary.total_titles) * 100).toFixed(1) : 0}% OF ALL CONTENT
          </div>
        </div>

        {/* Unique Titles */}
        <div className="kpi-card green">
          <div className="kpi-header">
            <span className="kpi-title">UNIQUE TITLES</span>
            <div className="kpi-icon-wrapper" style={{ backgroundColor: '#00C781', color: '#000' }}>
              <Sparkles size={18} strokeWidth={2.5} />
            </div>
          </div>
          <div className="kpi-value" style={{ color: '#00875A' }}>
            {summary?.unique_titles?.toLocaleString()}
          </div>
          <div className="kpi-subtitle">EXACT CARDINALITY GROUND TRUTH</div>
        </div>
      </div>

      {/* Row 1: Content Type Breakdown & Release Year Distribution */}
      <div className="charts-grid-2">
        {/* Movies vs TV Shows */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">
                <Film size={18} strokeWidth={2.5} />
                MOVIES VS TV SHOWS
              </h2>
              <div className="panel-subtitle">VOLUME SPLIT BY CONTENT TYPE</div>
            </div>
          </div>
          <div style={{ height: 280, width: '100%' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={analytics?.type_split || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={95}
                  paddingAngle={3}
                  stroke="#000000"
                  strokeWidth={2}
                  dataKey="value"
                  label={({ name, percent }) => `${name.toUpperCase()} ${(percent * 100).toFixed(0)}%`}
                >
                  {(analytics?.type_split || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={TYPE_COLORS[index % TYPE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<BrutalistTooltip />} />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  wrapperStyle={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.8rem',
                    fontWeight: 700,
                    textTransform: 'uppercase'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Release-Year Distribution */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">
                <Calendar size={18} strokeWidth={2.5} />
                RELEASE-YEAR DISTRIBUTION
              </h2>
              <div className="panel-subtitle">TITLES BY PRODUCTION YEAR (1990 - 2021)</div>
            </div>
          </div>
          <div style={{ height: 280, width: '100%' }}>
            <ResponsiveContainer>
              <AreaChart data={analytics?.release_year_distribution || []}>
                <CartesianGrid strokeDasharray="2 2" stroke="#CCCCCC" />
                <XAxis
                  dataKey="year"
                  stroke="#000000"
                  strokeWidth={1.5}
                  tick={{ fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 700 }}
                />
                <YAxis
                  stroke="#000000"
                  strokeWidth={1.5}
                  tick={{ fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 700 }}
                />
                <Tooltip content={<BrutalistTooltip />} />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#000000"
                  strokeWidth={2.5}
                  fill="#FF3030"
                  fillOpacity={0.65}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Top Countries & Top Genres */}
      <div className="charts-grid-2">
        {/* Top Countries */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">
                <Globe size={18} strokeWidth={2.5} />
                TOP 10 PRODUCING COUNTRIES
              </h2>
              <div className="panel-subtitle">GEOGRAPHIC DISTRIBUTION OF TITLES</div>
            </div>
          </div>
          <div style={{ height: 320, width: '100%' }}>
            <ResponsiveContainer>
              <BarChart
                data={(analytics?.top_countries || []).slice(0, 10)}
                layout="vertical"
                margin={{ left: 20, right: 20 }}
              >
                <CartesianGrid strokeDasharray="2 2" stroke="#CCCCCC" />
                <XAxis
                  type="number"
                  stroke="#000000"
                  strokeWidth={1.5}
                  tick={{ fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 700 }}
                />
                <YAxis
                  dataKey="country"
                  type="category"
                  stroke="#000000"
                  strokeWidth={1.5}
                  width={110}
                  tick={{ fontFamily: 'var(--font-mono)', fontSize: 10, fontWeight: 700 }}
                />
                <Tooltip content={<BrutalistTooltip />} />
                <Bar
                  dataKey="count"
                  fill={BAR_COUNTRY_COLOR}
                  stroke="#000000"
                  strokeWidth={1.5}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Genres */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">
                <Sliders size={18} strokeWidth={2.5} />
                TOP 10 CONTENT GENRES
              </h2>
              <div className="panel-subtitle">EXPLODED CATEGORY FREQUENCY</div>
            </div>
          </div>
          <div style={{ height: 320, width: '100%' }}>
            <ResponsiveContainer>
              <BarChart
                data={(analytics?.top_genres || []).slice(0, 10)}
                layout="vertical"
                margin={{ left: 25, right: 20 }}
              >
                <CartesianGrid strokeDasharray="2 2" stroke="#CCCCCC" />
                <XAxis
                  type="number"
                  stroke="#000000"
                  strokeWidth={1.5}
                  tick={{ fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 700 }}
                />
                <YAxis
                  dataKey="genre"
                  type="category"
                  stroke="#000000"
                  strokeWidth={1.5}
                  width={130}
                  tick={{ fontFamily: 'var(--font-mono)', fontSize: 10, fontWeight: 700 }}
                />
                <Tooltip content={<BrutalistTooltip />} />
                <Bar
                  dataKey="count"
                  fill={BAR_GENRE_COLOR}
                  stroke="#000000"
                  strokeWidth={1.5}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Dataset Technical Metadata */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title">
            <Activity size={18} strokeWidth={2.5} />
            TECHNICAL TELEMETRY & RUNTIME METRICS
          </h2>
          <div className="brand-badge" style={{ margin: 0, backgroundColor: '#000000' }}>
            ENGINE_INFO
          </div>
        </div>
        <div className="meta-grid">
          <div className="meta-item">
            <div className="meta-label">CATALOG SPAN</div>
            <div className="meta-val">{summary?.min_year} - {summary?.max_year}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">UNIQUE COUNTRIES</div>
            <div className="meta-val">{summary?.num_countries}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">CONTENT RATINGS</div>
            <div className="meta-val">{summary?.num_ratings} DISTINCT</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">MEAN MOVIE RUNTIME</div>
            <div className="meta-val">{analytics?.movie_duration_stats?.mean} MIN</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">MEDIAN RUNTIME</div>
            <div className="meta-val">{analytics?.movie_duration_stats?.median} MIN</div>
          </div>
        </div>
      </div>
    </div>
  );
}
