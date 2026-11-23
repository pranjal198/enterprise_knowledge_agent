
import { useState } from 'react'
import './App.css'

function App() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')

  async function handleFileUpload(e) {
    const file = e.target.files[0]

    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    setUploadMessage('')

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Upload failed')
      }

      setUploadMessage(
        `Successfully indexed ${data.filename} (${data.chunks} chunks)`
      )
    } catch (error) {
      setUploadMessage(error.message)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  async function sendMessage(e) {
    e.preventDefault()

    const userQuestion = question.trim()
    if (!userQuestion || loading) return

    setMessages(prev => [
      ...prev,
      { role: 'user', content: userQuestion }
    ])
    setQuestion('')
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userQuestion }),
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          sources: data.sources || [],
        },
      ])
    } catch (err) {
      setError(
        'Could not connect to the backend. Make sure FastAPI is running.'
      )
    } finally {
      setLoading(false)
    }
  }

  function newConversation() {
    setMessages([])
    setQuestion('')
    setError('')
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">K</div>
          <div>
            <h2>Knowledge AI</h2>
            <span>Enterprise Assistant</span>
          </div>
        </div>

        <button className="new-chat" onClick={newConversation}>
          + New conversation
        </button>

        <label className="upload-button">
          + Upload PDF
          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileUpload}
            hidden
          />
        </label>
        {uploading && (
          <div className="upload-status">
            Uploading and indexing PDF...
          </div>
        )}

        {uploadMessage && (
          <div className="upload-status">
            {uploadMessage}
          </div>
        )}

        <div className="sidebar-footer">
          <div className="avatar">AI</div>
          <div>
            <strong>Knowledge Assistant</strong>
            <span>Document Intelligence</span>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h3>Knowledge Assistant</h3>
            <p>Ask questions about your company documents</p>
          </div>
          <span className="status">
            <span className="status-dot"></span>
            AI Assistant
          </span>
        </header>

        <section className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-icon">✦</div>
              <h1>How can I help you today?</h1>
              <p>
                Ask questions about your company policies and documents.
                I'll find relevant information and provide source references.
              </p>

              <div className="suggestions">
                <button onClick={() => setQuestion('What are the different types of leave?')}>
                  What are the different types of leave?
                </button>
                <button onClick={() => setQuestion('How many casual leaves are employees entitled to?')}>
                  How many casual leaves are employees entitled to?
                </button>
                <button onClick={() => setQuestion('Explain the earned leave policy.')}>
                  Explain the earned leave policy.
                </button>
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((message, index) => (
                <div className={`message ${message.role}`} key={index}>
                  <div className="message-avatar">
                    {message.role === 'user' ? 'You' : 'AI'}
                  </div>

                  <div className="message-content">
                    <strong>
                      {message.role === 'user' ? 'You' : 'Assistant'}
                    </strong>
                    <p>{message.content}</p>

                    {message.sources?.length > 0 && (
                      <div className="sources">
                        <strong>Sources</strong>
                        {message.sources.map((source, i) => (
                          <div className="source-item" key={i}>
                            📄 {source.source.split(/[\\/]/).pop()}
                            <span>Page {source.page + 1}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="loading">
                  <span></span>
                  <span></span>
                  <span></span>
                  <p>Searching your documents...</p>
                </div>
              )}
            </div>
          )}

          {error && <div className="error">{error}</div>}
        </section>

        <form className="input-area" onSubmit={sendMessage}>
          <div className="input-container">
            <textarea
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  sendMessage(e)
                }
              }}
              placeholder="Ask anything about your documents..."
              rows="1"
            />
            <button type="submit" disabled={loading || !question.trim()}>
              {loading ? '...' : '↑'}
            </button>
          </div>
          <p>AI-generated answers may contain errors. Verify important information against the sources.</p>
        </form>
      </main>
    </div>
  )
}

export default App
