import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(_error) {
    // 🧠 NEURAL SENTINEL: ERROR DETECTED
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("OS_CRASH_LOG:", error, errorInfo);
    // Automatic Reset Attempt after 1.5s
    setTimeout(() => this.setState({ hasError: false }), 1500);
  }

  render() {
    if (this.state.hasError) {
      // 🛡️ RECOVERY MANIFEST: SYSTEM_RECOVERY_ACTIVE
      return (
        <div className="w-full h-full flex flex-col items-center justify-center bg-black/80 backdrop-blur-md rounded-3xl border border-red-500/20">
          <div className="text-red-500 font-mono text-[10px] tracking-[0.5em] animate-pulse">
            CRITICAL_RENDER_FAILURE // RECOVERY_ACTIVE
          </div>
          <div className="w-48 h-[2px] bg-red-900/40 mt-4 relative overflow-hidden">
             <div className="absolute inset-0 bg-red-500 animate-[reboot_1.5s_linear_infinite]" />
          </div>
          <style>{`
            @keyframes reboot {
              0% { transform: translateX(-100%); }
              100% { transform: translateX(100%); }
            }
          `}</style>
        </div>
      );
    }

    return this.props.children; 
  }
}
