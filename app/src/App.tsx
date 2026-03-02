import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('URL submitted:', url)
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
          />
          <button type="submit" className="submit-button">
            Validate
          </button>
        </form>
      </div>
      <footer className="footer"></footer>
    </>
  )
}

export default App
