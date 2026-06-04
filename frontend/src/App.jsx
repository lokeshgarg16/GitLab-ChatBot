import { useEffect, useMemo, useState } from 'react'
import { fetchChat, listUploadedDocs, deleteUploadedDoc, uploadDocument, ingestGitLabPages } from './api'
import { useLocalStorage } from './hooks/useLocalStorage'
import Sidebar from './components/Sidebar'
import ChatInput from './components/ChatInput'
import ChatMessage from './components/ChatMessage'
import SourcePanel from './components/SourcePanel'
import ThemeToggle from './components/ThemeToggle'

const INITIAL_CHAT = {
  title: 'GitLab Handbook Assistant',
  messages: [],
  sources: [],
  chunks: [],
  suggestions: [],
  confidence: 0,
}

function App() {
  const [theme, setTheme] = useLocalStorage('theme', 'dark')
  const [chats, setChats] = useLocalStorage('chats', [INITIAL_CHAT])
  const [activeIndex, setActiveIndex] = useState(0)
  const [loading, setLoading] = useState(false)
  const [uploadedDocs, setUploadedDocs] = useState([])
  const [docsLoading, setDocsLoading] = useState(false)

  const activeChat = chats[activeIndex] || INITIAL_CHAT

  const updateChat = (index, patch) => {
    setChats((current) => {
      const next = [...current]
      next[index] = { ...next[index], ...patch }
      return next
    })
  }

  const loadUploadedDocs = async () => {
    setDocsLoading(true)
    try {
      const data = await listUploadedDocs()
      setUploadedDocs(data.sources || [])
    } catch (error) {
      console.error('Failed to load uploaded docs', error)
    } finally {
      setDocsLoading(false)
    }
  }

  useEffect(() => {
    loadUploadedDocs()
  }, [])

  const handleNewChat = () => {
    const newChat = { ...INITIAL_CHAT, title: `Chat ${chats.length + 1}` }
    setChats([...chats, newChat])
    setActiveIndex(chats.length)
  }

  const handleSelectChat = (index) => {
    setActiveIndex(index)
  }

  const handleSend = async (query) => {
    setLoading(true)
    const userMessage = { role: 'user', text: query }
    updateChat(activeIndex, { messages: [...activeChat.messages, userMessage] })
    try {
      const payload = await fetchChat(query, `session-${activeIndex}`)
      const assistantMessage = { role: 'assistant', text: payload.answer }
      updateChat(activeIndex, {
        messages: [...(activeChat.messages || []), userMessage, assistantMessage],
        sources: payload.sources,
        chunks: payload.retrieved_chunks,
        suggestions: payload.follow_up_suggestions,
        confidence: payload.confidence,
      })
    } catch (error) {
      updateChat(activeIndex, {
        messages: [...activeChat.messages, { role: 'assistant', text: 'Sorry, something went wrong while contacting the API.' }],
      })
    } finally {
      setLoading(false)
    }
  }

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(nextTheme)
    document.documentElement.classList.toggle('light', nextTheme === 'light')
  }

  const relatedQuestions = useMemo(() => activeChat.suggestions || [], [activeChat.suggestions])

  // handle upload input change
  const handleUploadChange = async (event) => {
    const file = event.target.files && event.target.files[0]
    if (!file) return

    setDocsLoading(true)

    try {
      await uploadDocument(file)
      await loadUploadedDocs()
    } catch (err) {
      console.error('Upload failed', err)
      alert('Upload failed. Please try again.')
    } finally {
      setDocsLoading(false)
      event.target.value = ''
    }
  }

  const handleImportGitLabHandbook = async () => {
    setDocsLoading(true)

    try {
      const result = await ingestGitLabPages()
      await loadUploadedDocs()
      alert(`Imported ${result.pages} GitLab pages and ${result.chunks} chunks.`)
    } catch (err) {
      console.error('GitLab handbook ingestion failed', err)
      alert('Failed to import GitLab handbook pages. Please try again.')
    } finally {
      setDocsLoading(false)
    }
  }

  const handleDeleteUploadedDoc = async (source) => {
    const confirmed = window.confirm(
      `Delete '${source}' from the document index? This will remove its vectors from Chroma.`
    )

    if (!confirmed) return

    setDocsLoading(true)

    try {
      await deleteUploadedDoc(source)
      await loadUploadedDocs()
    } catch (err) {
      console.error('Delete uploaded doc failed', err)
      alert('Failed to delete uploaded document.')
    } finally {
      setDocsLoading(false)
    }
  }

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col gap-6 px-4 py-6 lg:px-8">
        <header className="flex flex-col gap-4 rounded-3xl border border-slate-800 bg-slate-950 p-6 shadow-soft sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.36em] text-indigo-300">GitLab Handbook RAG</p>
            <h1 className="mt-2 text-3xl font-semibold">Ask the GitLab Handbook and Direction pages</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-400">Instant answers from indexed policy and direction content with source citations, follow-ups, and chat history.</p>
          </div>
          <div className="flex items-center gap-3">
            <input id="upload-input" type="file" accept=".txt,.md,.html,.pdf,.csv" className="hidden" onChange={handleUploadChange} />
            <button
              onClick={() => document.getElementById('upload-input').click()}
              className="rounded-2xl border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-200 hover:border-indigo-500"
            >
              Upload Document
            </button>
            <button
              onClick={handleImportGitLabHandbook}
              className="rounded-2xl border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-200 hover:border-indigo-500"
            >
              Import GitLab Handbook
            </button>
            <button
              onClick={() => {
                // clear messages for active chat
                updateChat(activeIndex, { messages: [], sources: [], chunks: [], suggestions: [], confidence: 0 })
              }}
              className="rounded-2xl border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-200 hover:border-red-500"
            >
              Clear Chat
            </button>
            <ThemeToggle theme={theme} onToggle={toggleTheme} />
          </div>
        </header>

        <section className="rounded-3xl border border-slate-800 bg-slate-900 p-5 shadow-soft">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-100">Uploaded documents</h2>
              <p className="text-sm text-slate-500">See the files currently indexed in Chroma and remove any uploaded document.</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={loadUploadedDocs}
                className="rounded-2xl border border-slate-700 bg-slate-800 px-3 py-1 text-sm text-slate-200 hover:border-indigo-500"
              >
                Refresh
              </button>
              {docsLoading ? (
                <div className="text-sm text-slate-400">Loading...</div>
              ) : null}
            </div>
          </div>
          <div className="mt-4 space-y-3">
            {uploadedDocs.length > 0 ? (
              uploadedDocs.map((doc) => (
                <div key={doc.source} className="flex flex-col gap-2 rounded-3xl border border-slate-700 bg-slate-950 p-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium text-slate-100">{doc.source}</p>
                    <p className="text-sm text-slate-400">{doc.count} chunk{doc.count === 1 ? '' : 's'}</p>
                  </div>
                  <button
                    onClick={() => handleDeleteUploadedDoc(doc.source)}
                    className="mt-2 rounded-2xl border border-red-600 bg-red-700 px-4 py-2 text-sm text-white hover:bg-red-600 sm:mt-0"
                  >
                    Delete
                  </button>
                </div>
              ))
            ) : (
              <div className="rounded-3xl border border-dashed border-slate-700 bg-slate-950 p-6 text-sm text-slate-400">No uploaded documents found yet.</div>
            )}
          </div>
        </section>

        <div className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
          <Sidebar chats={chats} selectedChatIndex={activeIndex} onSelect={handleSelectChat} onNewChat={handleNewChat} />

          <main className="space-y-6 rounded-3xl border border-slate-800 bg-slate-950 p-6 shadow-soft">
            <div className="flex flex-col gap-3">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h2 className="text-xl font-semibold">{activeChat.title}</h2>
                  <p className="text-sm text-slate-500">Confidence score: {activeChat.confidence || 0.0}</p>
                </div>
                <div className="flex flex-wrap gap-2 text-sm text-slate-400">
                  {relatedQuestions.map((item, index) => (
                    <button key={index} className="rounded-full border border-slate-700 px-3 py-1 hover:border-indigo-500">{item}</button>
                  ))}
                </div>
              </div>
            </div>

            <section className="space-y-4">
              {activeChat.messages.length === 0 ? (
                <div className="rounded-3xl border border-dashed border-slate-700 bg-slate-900 p-10 text-center text-slate-500">Start by asking a question about GitLab's handbook or direction documentation.</div>
              ) : (
                <div className="space-y-4">
                  {activeChat.messages.map((message, index) => (
                    <ChatMessage key={index} message={message} />
                  ))}
                </div>
              )}
            </section>

            <ChatInput onSubmit={handleSend} disabled={loading} />

            <SourcePanel sources={activeChat.sources || []} chunks={activeChat.chunks || []} suggestions={activeChat.suggestions || []} />
          </main>
        </div>
      </div>
    </div>
  )
}

export default App
