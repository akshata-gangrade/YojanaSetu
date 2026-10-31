export function Header({ lang, onToggleLang }) {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-600 text-lg font-bold text-white shadow-sm">
            YS
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-slate-900">
              Yojana<span className="text-emerald-600">Setu</span>
            </span>
            <p className="hidden text-xs text-slate-500 sm:block">
              Independent Scheme Navigator
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={onToggleLang}
            type="button"
            className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            {lang === 'en' ? 'हिंदी' : 'English'}
          </button>
        </div>
      </div>
    </header>
  );
}
