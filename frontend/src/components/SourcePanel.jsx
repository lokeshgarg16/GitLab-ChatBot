export default function SourcePanel({ sources, chunks, suggestions }) {
  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-950 p-5 shadow-soft">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.24em] text-slate-400">Transparency Panel</h3>
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-slate-100">Cited Sources</h4>
          <ul className="mt-2 space-y-2 text-sm text-slate-300">
            {sources.map((source, index) => (
              <li key={index} className="rounded-2xl bg-slate-900 px-3 py-2">{source}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-slate-100">Related Chunks</h4>
          <div className="mt-2 space-y-2 text-sm text-slate-300">
            {chunks.slice(0, 3).map((chunk, index) => (
              <div key={index} className="rounded-2xl bg-slate-900 p-3">{chunk.slice(0, 200)}...</div>
            ))}
          </div>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-slate-100">Suggested Follow-ups</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <span key={index} className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-xs text-slate-300">
                {suggestion}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
