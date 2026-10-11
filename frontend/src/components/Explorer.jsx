import React, { useState, useEffect } from 'react';
import { Search, ChevronLeft, ChevronRight, Film, Tv, Database, Filter } from 'lucide-react';

export default function Explorer() {
  const [titles, setTitles] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [limit] = useState(15);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isCancelled = false;

    async function loadTitles() {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          page: page.toString(),
          limit: limit.toString(),
        });

        if (searchTerm.trim()) {
          params.append('search', searchTerm.trim());
        }

        if (selectedType !== 'all') {
          params.append('type', selectedType);
        }

        const res = await fetch(`/api/titles?${params.toString()}`);
        if (!res.ok) throw new Error('Failed to fetch titles');
        const data = await res.json();

        if (!isCancelled) {
          setTitles(data.items);
          setTotalPages(data.total_pages);
          setTotalItems(data.total_items);
        }
      } catch (err) {
        console.error(err);
      } finally {
        if (!isCancelled) setLoading(false);
      }
    }

    const timer = setTimeout(() => {
      loadTitles();
    }, 250);

    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [page, searchTerm, selectedType, limit]);

  const handleTypeChange = (type) => {
    setSelectedType(type);
    setPage(1);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setPage(1);
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">
          CONTENT EXPLORER
        </h1>
        <p className="page-description">
          // RELATIONAL CATALOG QUERY & MULTI-ATTRIBUTE METADATA BROWSER
        </p>
      </div>

      <div className="panel">
        {/* Filters and Search Bar */}
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '20px' }}>
          <div style={{ position: 'relative', flex: '1', minWidth: '280px' }}>
            <input
              type="text"
              className="input-primary"
              style={{ width: '100%', paddingLeft: '42px' }}
              placeholder="SEARCH CATALOG BY TITLE (E.G. STRANGER THINGS, INCEPTION)..."
              value={searchTerm}
              onChange={handleSearchChange}
            />
            <Search
              size={18}
              strokeWidth={2.5}
              style={{
                position: 'absolute',
                left: '14px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#000000'
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => handleTypeChange('all')}
              className="btn-secondary"
              style={{
                backgroundColor: selectedType === 'all' ? '#000000' : '#FFFFFF',
                color: selectedType === 'all' ? '#FFFFFF' : '#000000',
                border: '2px solid #000000',
                boxShadow: selectedType === 'all' ? '3px 3px 0 var(--accent-red)' : '2px 2px 0 #000',
              }}
            >
              ALL TYPES
            </button>
            <button
              onClick={() => handleTypeChange('Movie')}
              className="btn-secondary"
              style={{
                backgroundColor: selectedType === 'Movie' ? '#FF3030' : '#FFFFFF',
                color: selectedType === 'Movie' ? '#FFFFFF' : '#000000',
                border: '2px solid #000000',
                boxShadow: selectedType === 'Movie' ? '3px 3px 0 #000000' : '2px 2px 0 #000',
              }}
            >
              MOVIES ONLY
            </button>
            <button
              onClick={() => handleTypeChange('TV Show')}
              className="btn-secondary"
              style={{
                backgroundColor: selectedType === 'TV Show' ? '#A78BFA' : '#FFFFFF',
                color: selectedType === 'TV Show' ? '#000000' : '#000000',
                border: '2px solid #000000',
                boxShadow: selectedType === 'TV Show' ? '3px 3px 0 #000000' : '2px 2px 0 #000',
              }}
            >
              TV SHOWS ONLY
            </button>
          </div>
        </div>

        {/* Results telemetry tag */}
        <div
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.8rem',
            fontWeight: 800,
            marginBottom: '16px',
            color: '#000000'
          }}
        >
          QUERY_RESULTS: <span style={{ color: '#FF3030' }}>{totalItems.toLocaleString()}</span> MATCHING TITLES
        </div>

        {/* Data Table */}
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>TITLE</th>
                <th>TYPE</th>
                <th>RELEASE YEAR</th>
                <th>RATING</th>
                <th>COUNTRY</th>
                <th>GENRES</th>
                <th>DURATION</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '40px' }}>
                    <div className="spinner" style={{ margin: '0 auto 12px auto' }}></div>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                      [EXECUTING SLICED CATALOG QUERY...]
                    </span>
                  </td>
                </tr>
              ) : titles.length === 0 ? (
                <tr>
                  <td
                    colSpan={7}
                    style={{
                      textAlign: 'center',
                      padding: '40px',
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 700,
                      color: '#555555'
                    }}
                  >
                    [NO CATALOG ENTRIES MATCHED CURRENT QUERY PARAMETERS]
                  </td>
                </tr>
              ) : (
                titles.map((item, idx) => (
                  <tr key={item.show_id || idx}>
                    <td style={{ fontWeight: 800, color: '#000000' }}>{item.title}</td>
                    <td>
                      <span className={`badge ${item.type === 'Movie' ? 'badge-movie' : 'badge-tv'}`}>
                        {item.type}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{item.release_year}</td>
                    <td>
                      <span className="badge badge-rating">{item.rating || 'NR'}</span>
                    </td>
                    <td
                      style={{
                        maxWidth: '160px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.8rem'
                      }}
                      title={item.country}
                    >
                      {item.country || 'UNKNOWN'}
                    </td>
                    <td
                      style={{
                        maxWidth: '220px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        fontSize: '0.85rem'
                      }}
                      title={item.listed_in}
                    >
                      {item.listed_in}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{item.duration}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination controls */}
        <div className="pagination">
          <div style={{ fontSize: '0.8rem', fontWeight: 800 }}>
            PAGE {page} OF {totalPages} &nbsp;[LIMIT: {limit}/PAGE]
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              className="pagination-btn"
              disabled={page <= 1 || loading}
              onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
            >
              <ChevronLeft size={16} strokeWidth={2.5} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
              PREVIOUS
            </button>
            <button
              className="pagination-btn"
              disabled={page >= totalPages || loading}
              onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}
            >
              NEXT
              <ChevronRight size={16} strokeWidth={2.5} style={{ verticalAlign: 'middle', marginLeft: '4px' }} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
