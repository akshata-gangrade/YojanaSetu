export function SchemeDetail({ scheme }) {
  if (!scheme) return null;
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-bold text-slate-900">{scheme.name}</h2>
      <div className="mt-2 text-xs text-slate-500">
        Last verified: {scheme.lastVerified || 'Pending'}
      </div>
      <a
        href={scheme.officialSourceUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-4 inline-block text-sm font-medium text-emerald-600 hover:underline"
      >
        View Official Ministry Source &rarr;
      </a>
    </article>
  );
}
