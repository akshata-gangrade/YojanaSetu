export function Footer() {
  return (
    <footer className="mt-auto border-t border-slate-800 bg-slate-900 py-8 text-xs text-slate-400">
      <div className="mx-auto max-w-7xl space-y-4 px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p className="font-semibold text-slate-300">
            YojanaSetu &mdash; Open-source Citizen Scheme Discovery
          </p>
          <p className="font-medium text-amber-400">
            Not an official Government of India website.
          </p>
        </div>
        <p className="max-w-4xl leading-relaxed text-slate-400">
          <strong>Privacy Guarantee:</strong> Zero personal data is persisted. We never
          ask for or store Aadhaar, PAN, phone number, email, address, or bank details.
          Citizen inputs are processed entirely in browser memory per request.
        </p>
        <p className="border-t border-slate-800 pt-2 text-slate-500">
          All scheme information is verified directly against official ministry guidelines
          with source links and verification timestamps.
        </p>
      </div>
    </footer>
  );
}
