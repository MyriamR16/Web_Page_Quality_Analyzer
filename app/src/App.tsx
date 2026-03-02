import { useState } from 'react'
import './App.css'

interface AnalysisError {
  type: string
  subtype: string
  message: string
}

interface AnalysisResult {
  url: string
  errors: AnalysisError[]
  total_errors: number
}

interface Report {
  summary: string
  recommendations: string[]
  prioritization: {
    critical: Array<string | AnalysisError>
    warning: Array<string | AnalysisError>
    info: Array<string | AnalysisError>
  }
}

interface ReportResult {
  url: string
  report: Report
}

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [reportLoading, setReportLoading] = useState(false)
  const [report, setReport] = useState<ReportResult | null>(null)
  const [reportError, setReportError] = useState<string | null>(null)

  const filterErrors = (errors: AnalysisError[]): AnalysisError[] => {
    return errors.filter((err) => {
      // Exclure les erreurs HTTPS manquante
      if (err.type === 'security_error' && err.subtype === 'missing_https') {
        return false
      }
      // Exclure les erreurs de ressources non trouvées
      if (err.type === 'javascript_error' && err.message.includes('Failed to load resource')) {
        return false
      }
      return true
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    setReport(null)
    setReportError(null)

    try {
      const response = await fetch(`http://localhost:5000/analyse?url=${encodeURIComponent(url)}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during analysis')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateReport = async () => {
    if (!result) return
    
    setReportLoading(true)
    setReportError(null)
    setReport(null)

    try {
      const filteredErrors = filterErrors(result.errors)
      const response = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: result.url,
          errors: filteredErrors,
        }),
      })
      
      if (!response.ok) {
        let message = `HTTP error! status: ${response.status}`
        try {
          const errorData = await response.json()
          if (errorData?.error) {
            message = errorData.error
          }
        } catch {
        }
        throw new Error(message)
      }
      
      const data = await response.json()
      setReport(data)
    } catch (err) {
      setReportError(err instanceof Error ? err.message : 'An error occurred while generating report')
      console.error('Report generation error:', err)
    } finally {
      setReportLoading(false)
    }
  }

  return (
    <>
      <header className="header"></header>
      <div className="container">
        <h1>Analyze your web page quality</h1>
        <form onSubmit={handleSubmit} className="url-form">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL to analyze..."
            className="url-input"
            required
            disabled={loading}
          />
          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Analyzing...' : 'Validate'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
          </div>
        )}

        {result && (
          <div className="results-container">
            <div className="columns">
              <div className="left-column">
                <h2>Errors Detected</h2>
                <p className="total-errors">Total: {filterErrors(result.errors).length}</p>
                
                {filterErrors(result.errors).length > 0 && (
                  <div className="errors-list">
                    {filterErrors(result.errors).map((err, index) => (
                      <div key={index} className="error-item">
                        <span className="error-type">{err.type}</span>
                        <span className="error-subtype">{err.subtype}</span>
                        <p className="error-message">{err.message}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="right-column">
                <button 
                  onClick={handleGenerateReport} 
                  className="generate-button"
                  disabled={reportLoading}
                >
                  {reportLoading ? 'Generating...' : 'Generate Report'}
                </button>

                {reportError && (
                  <div className="error-message">
                    <p>Error: {reportError}</p>
                  </div>
                )}

                {report && (
                  <div className="report-content">
                    <h3>Summary</h3>
                    <p className="report-summary">{report.report.summary}</p>

                    <h3>Recommendations</h3>
                    <ul className="recommendations-list">
                      {report.report.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>

                    <h3>Prioritization</h3>
                    {report.report.prioritization.critical.length > 0 && (
                      <div className="priority-section critical">
                        <h4>Critical</h4>
                        <ul>
                          {report.report.prioritization.critical.map((item, index) => (
                            <li key={index}>
                              {typeof item === 'string' ? item : `[${item.type}] ${item.message}`}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {report.report.prioritization.warning.length > 0 && (
                      <div className="priority-section warning">
                        <h4>Warning</h4>
                        <ul>
                          {report.report.prioritization.warning.map((item, index) => (
                            <li key={index}>
                              {typeof item === 'string' ? item : `[${item.type}] ${item.message}`}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {report.report.prioritization.info.length > 0 && (
                      <div className="priority-section info">
                        <h4>Info</h4>
                        <ul>
                          {report.report.prioritization.info.map((item, index) => (
                            <li key={index}>
                              {typeof item === 'string' ? item : `[${item.type}] ${item.message}`}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
      <footer className="footer"></footer>
    </>
  )
}

export default App
