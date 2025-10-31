import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [satellites, setSatellites] = useState([]);
  const [selectedSatellite, setSelectedSatellite] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSatellites();
  }, []);

  const fetchSatellites = async () => {
    try {
      const response = await axios.get('http://localhost:8000/satellites');
      setSatellites(response.data);
    } catch (err) {
      setError('Failed to fetch satellites');
      console.error(err);
    }
  };

  const generateReport = async () => {
    if (!selectedSatellite || !selectedLanguage) {
      setError('Please select both satellite and language');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const response = await axios.post('http://localhost:8000/reports/generate', {
        satellite: selectedSatellite,
        language: selectedLanguage
      });
      setReport(response.data);
    } catch (err) {
      setError('Failed to generate report');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generateAllReports = async () => {
    setLoading(true);
    setError('');
    try {
      await axios.post('http://localhost:8000/reports/generate-all');
      alert('All reports generated successfully!');
      // Refresh satellites data
      fetchSatellites();
    } catch (err) {
      setError('Failed to generate all reports');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSatelliteChange = (satelliteName) => {
    setSelectedSatellite(satelliteName);
    setSelectedLanguage('');
    setReport(null);
  };

  const currentSatellite = satellites.find(s => s.name === selectedSatellite);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Team Persia Reports</h1>
        <p>Automated Code Analysis System</p>
      </header>

      <main className="App-main">
        <div className="controls">
          <div className="control-group">
            <label>Select Satellite:</label>
            <select
              value={selectedSatellite}
              onChange={(e) => handleSatelliteChange(e.target.value)}
            >
              <option value="">Choose satellite...</option>
              {satellites.map(satellite => (
                <option key={satellite.name} value={satellite.name}>
                  {satellite.name} ({satellite.languages.length} languages)
                </option>
              ))}
            </select>
          </div>

          {currentSatellite && (
            <div className="control-group">
              <label>Select Language:</label>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
              >
                <option value="">Choose language...</option>
                {currentSatellite.languages.map(language => (
                  <option key={language} value={language}>
                    {language}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="buttons">
            <button
              onClick={generateReport}
              disabled={loading || !selectedSatellite || !selectedLanguage}
            >
              {loading ? 'Generating...' : 'Generate Report'}
            </button>
            <button
              onClick={generateAllReports}
              disabled={loading}
              className="secondary"
            >
              {loading ? 'Generating...' : 'Generate All Reports'}
            </button>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        {report && (
          <div className="report">
            <h2>Report: {report.satellite} - {report.language}</h2>
            <div className="report-meta">
              <span>Status: {report.status}</span>
              <span>Files: {report.file_count}</span>
              <span>Generated: {new Date(report.timestamp).toLocaleString()}</span>
            </div>
            <div className="report-content">
              <pre>{report.content}</pre>
            </div>
          </div>
        )}

        <div className="satellites-overview">
          <h2>Available Satellites</h2>
          <div className="satellites-grid">
            {satellites.map(satellite => (
              <div key={satellite.name} className="satellite-card">
                <h3>{satellite.name}</h3>
                <p>Languages: {satellite.languages.join(', ')}</p>
                <span className={`status ${satellite.enabled ? 'enabled' : 'disabled'}`}>
                  {satellite.enabled ? 'Active' : 'Inactive'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
