export default function ThemeToggle({ theme, onToggle }) {
  return (
    <button
      onClick={onToggle}
      className="rounded-3xl border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-200 transition hover:border-indigo-500"
    >
      {theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'}
    </button>
  )
}
