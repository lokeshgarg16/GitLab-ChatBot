import { useState } from 'react'

export default function ChatInput({ onSubmit, disabled }) {
  const [message, setMessage] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!message.trim()) return
    onSubmit(message.trim())
    setMessage('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 p-4 bg-slate-900 rounded-2xl shadow-soft">
      <input
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        placeholder="Ask anything about GitLab Handbook or Direction pages..."
        className="flex-1 rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-indigo-500"
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled}
        className="rounded-2xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
      >
        Send
      </button>
    </form>
  )
}
