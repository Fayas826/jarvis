import * as vscode from 'vscode';
import axios from 'axios';

// The endpoint where the JARVIS Meta-Architect FastAPI backend listens for diagnostics
const JARVIS_BACKEND_URL = 'http://127.0.0.1:8000/api/ide/diagnostics';

export function activate(context: vscode.ExtensionContext) {
    console.log('JARVIS Omnipresent Eye is now active!');

    // Listen for diagnostic changes (the yellow and red squiggles)
    const diagnosticListener = vscode.languages.onDidChangeDiagnostics((e: vscode.DiagnosticChangeEvent) => {
        const diagnosticsPayload = [];
        
        for (const uri of e.uris) {
            const diagnostics = vscode.languages.getDiagnostics(uri);
            if (diagnostics.length > 0) {
                diagnosticsPayload.push({
                    file: uri.fsPath,
                    issues: diagnostics.map((d: vscode.Diagnostic) => ({
                        severity: d.severity === vscode.DiagnosticSeverity.Error ? 'ERROR' : 'WARNING',
                        message: d.message,
                        line: d.range.start.line + 1,
                        source: d.source || 'VSCode'
                    }))
                });
            }
        }

        // Only send if we found something
        if (diagnosticsPayload.length > 0) {
            sendToJarvis(diagnosticsPayload);
        }
    });

    context.subscriptions.push(diagnosticListener);
}

async function sendToJarvis(payload: any) {
    try {
        await axios.post(JARVIS_BACKEND_URL, { diagnostics: payload });
        console.log('Streamed diagnostics to JARVIS Meta-Architect.');
    } catch (error) {
        // Backend might be offline; silent fail is fine for this daemon
        console.error('JARVIS offline. Could not send diagnostics.', error);
    }
}

export function deactivate() {}
