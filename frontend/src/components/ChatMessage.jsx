import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export default function ChatMessage({ message }) {
  return (
    <div className={`rounded-3xl border px-5 py-4 shadow-soft ${message.role === 'assistant' ? 'bg-slate-900 border-slate-800' : 'bg-slate-950 border-slate-800'}`}>
      <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-slate-400">
        <span>{message.role === 'assistant' ? 'Assistant' : 'You'}</span>
      </div>
      <div className="prose prose-invert max-w-none text-slate-100">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
      </div>
    </div>
  )
}
