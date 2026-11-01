import { isOfficialGovDomain } from '../../lib/urlHelper';

/**
 * Component that safely renders external links only if the domain is allowlisted (.gov.in / .nic.in).
 * If domain is not an official domain, it renders as safe plain text with no anchor.
 */
export function GovLink({
  href,
  children,
  className = '',
  plainTextClassName = '',
  showExternalIcon = true,
  ...props
}) {
  const isOfficial = isOfficialGovDomain(href);

  if (!isOfficial) {
    return (
      <span className={plainTextClassName || 'text-text-muted break-all'} role="text">
        {children || href}
      </span>
    );
  }

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={className}
      {...props}
    >
      <span>{children || href}</span>
      {showExternalIcon && (
        <span aria-hidden="true" className="ml-1 inline-block shrink-0">
          ↗
        </span>
      )}
      <span className="sr-only"> (opens in new official government tab)</span>
    </a>
  );
}

export default GovLink;

