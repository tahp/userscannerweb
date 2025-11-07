import React, { useState } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleScan = () => {
    setLoading(true);
    fetch(`/api/scan/${username}`)
      .then(response => response.json())
      .then(data => {
        setResults(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
        setLoading(false);
      });
  };

  return (
    <div className="container mt-5">
      <h1 className="text-center">User Scanner</h1>
      <div className="input-group mb-3">
        <input
          type="text"
          className="form-control"
          placeholder="Enter username"
          value={username}
          onChange={e => setUsername(e.target.value)}
        />
        <div className="input-group-append">
          <button
            className="btn btn-primary"
            type="button"
            onClick={handleScan}
            disabled={loading}
          >
            {loading ? 'Scanning...' : 'Scan'}
          </button>
        </div>
      </div>

      {results && (
        <div>
          {Object.keys(results).map(category => (
            <div key={category} className="card mb-3">
              <div className="card-header">{category}</div>
              <ul className="list-group list-group-flush">
                {results[category].map(result => (
                  <li key={result.site} className="list-group-item d-flex justify-content-between align-items-center">
                    <a href={result.url} target="_blank" rel="noopener noreferrer">{result.site}</a>
                    <span
                      className={`badge badge-${result.status === 'Available' ? 'success' : result.status === 'Taken' ? 'danger' : 'warning'}`}>
                      {result.status}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;