export function IntakeForm() {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-2 text-lg font-semibold text-slate-800">
        Find Qualified Schemes
      </h2>
      <p className="mb-4 text-sm text-slate-500">
        Describe your family situation, occupation, state, and income in plain words.
      </p>
      <div className="rounded-lg border border-emerald-100 bg-emerald-50 p-3 text-xs text-emerald-700">
        🔒 Profiles stay in browser memory. No Aadhaar, phone, or bank details collected.
      </div>
    </div>
  );
}
