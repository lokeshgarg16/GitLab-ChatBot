export default function Sidebar({ chats, selectedChatIndex, onSelect, onNewChat }) {
  return (
    <aside className="w-full max-w-xs shrink-0 space-y-4 rounded-3xl border border-slate-800 bg-slate-950 p-4 shadow-soft md:max-w-sm">
      <div className="flex items-center justify-between gap-2 pb-4">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-400">Conversations</h2>
          <p className="text-xs text-slate-500">Saved chats and context.</p>
        </div>
        <button onClick={onNewChat} className="rounded-2xl bg-indigo-600 px-3 py-2 text-xs font-semibold text-white hover:bg-indigo-500">
          New
        </button>
      </div>
      <div className="space-y-2">
        {chats.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-700 p-4 text-sm text-slate-500">Start a conversation to save history.</div>
        ) : (
          chats.map((chat, index) => (
            <button
              key={index}
              onClick={() => onSelect(index)}
              className={`w-full rounded-3xl px-4 py-3 text-left transition ${selectedChatIndex === index ? 'bg-slate-900 border border-indigo-500 text-white' : 'bg-slate-950 border border-slate-800 text-slate-300 hover:bg-slate-900'}`}
            >
              <div className="text-sm font-semibold">{chat.title || `Chat ${index + 1}`}</div>
              <div className="text-xs text-slate-500">{chat.messages[chat.messages.length - 1]?.text.slice(0, 60)}...</div>
            </button>
          ))
        )}
      </div>
    </aside>
  )
}
