import { Component } from 'react';
import { Button } from './ui/Button';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Structured client logging without personal data
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an unhandled error:', error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          role="alert"
          className="mx-auto my-12 max-w-lg rounded-[12px] border border-[#F8B4B4] bg-[#FDF2F2] p-8 text-center shadow-soft"
        >
          <div
            className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[#B3261E] text-white text-xl font-bold"
            aria-hidden="true"
          >
            !
          </div>
          <h2 className="text-xl font-bold text-[#B3261E]">
            Something unexpected occurred
          </h2>
          <p className="mt-2 text-sm text-[#55627A]">
            An unexpected error interrupted this page. No personal information was affected.
          </p>

          <div className="mt-6 flex justify-center gap-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => window.location.reload()}
            >
              Reload Page
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={this.handleReset}
            >
              Back to Home
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

