/**
 * Data Preview Component
 * Tabular data display with sorting and filtering
 */

import React, { useState, useMemo } from 'react';

const DataPreview = ({ artifact, isEditing, onUpdate }) => {
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  const [filterText, setFilterText] = useState('');
  
  // Parse data (assuming CSV or JSON)
  const parseData = () => {
    try {
      // Try JSON first
      const parsed = JSON.parse(artifact.content);
      if (Array.isArray(parsed)) {
        return parsed;
      }
      return [parsed];
    } catch {
      // Fall back to CSV
      const lines = artifact.content.split('\n').filter(line => line.trim());
      if (lines.length === 0) return [];
      
      const headers = lines[0].split(',').map(h => h.trim());
      const rows = lines.slice(1).map(line => {
        const values = line.split(',').map(v => v.trim());
        return headers.reduce((obj, header, index) => {
          obj[header] = values[index];
          return obj;
        }, {});
      });
      
      return rows;
    }
  };
  
  const data = useMemo(() => parseData(), [artifact.content]);
  const headers = data.length > 0 ? Object.keys(data[0]) : [];
  
  const filteredData = useMemo(() => {
    if (!filterText) return data;
    
    return data.filter(row =>
      Object.values(row).some(value =>
        String(value).toLowerCase().includes(filterText.toLowerCase())
      )
    );
  }, [data, filterText]);
  
  const sortedData = useMemo(() => {
    if (!sortColumn) return filteredData;
    
    return [...filteredData].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];
      
      if (aVal === bVal) return 0;
      
      const comparison = aVal < bVal ? -1 : 1;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [filteredData, sortColumn, sortDirection]);
  
  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };
  
  const exportCSV = () => {
    const csv = [
      headers.join(','),
      ...sortedData.map(row => headers.map(h => row[h]).join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title}.csv`;
    a.click();
  };
  
  return (
    <div className="data-preview">
      <div className="data-controls">
        <input
          type="text"
          className="data-filter"
          placeholder="Filter data..."
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
        />
        <button className="btn-secondary" onClick={exportCSV}>
          Export CSV
        </button>
        <span className="data-count">
          {sortedData.length} / {data.length} rows
        </span>
      </div>
      
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              {headers.map((header) => (
                <th
                  key={header}
                  onClick={() => handleSort(header)}
                  className={sortColumn === header ? 'sorted' : ''}
                >
                  {header}
                  {sortColumn === header && (
                    <span className="sort-indicator">
                      {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                    </span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, index) => (
              <tr key={index}>
                {headers.map((header) => (
                  <td key={header}>{row[header]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataPreview;
