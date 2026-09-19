import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from "@/App.jsx"

const showError = (msg, stack) => {
  // Use DOM API instead of innerHTML to prevent XSS via error message content
  const overlay = document.createElement('div');
  Object.assign(overlay.style, {
    background: 'red', color: 'white', padding: '20px',
    fontFamily: 'monospace', zIndex: '999999',
    position: 'fixed', inset: '0', overflow: 'auto'
  });
  const h1 = document.createElement('h1');
  h1.textContent = 'CRITICAL ERROR';
  const p = document.createElement('p');
  p.textContent = msg;
  const pre = document.createElement('pre');
  pre.textContent = stack;
  overlay.appendChild(h1);
  overlay.appendChild(p);
  overlay.appendChild(pre);
  document.body.innerHTML = '';
  document.body.appendChild(overlay);
};
window.addEventListener('error', (e) => showError(e.message || JSON.stringify(e), e.error?.stack || 'No stack'));
window.addEventListener('unhandledrejection', (e) => showError(e.reason?.message || JSON.stringify(e.reason), e.reason?.stack || 'No stack'));


import React from 'react';
class GlobalErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ background: 'red', color: 'white', padding: '20px', fontFamily: 'monospace', position: 'fixed', inset: 0, overflow: 'auto', zIndex: 999999 }}>
          <h1>REACT CRITICAL ERROR</h1>
          <p>{this.state.error && this.state.error.toString()}</p>
          <pre>{this.state.errorInfo && this.state.errorInfo.componentStack}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <GlobalErrorBoundary>
    <App />
  </GlobalErrorBoundary>
)
