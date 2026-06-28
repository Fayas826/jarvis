import { WebSocketServer } from 'ws';
import { Server as HTTPServer } from 'http';
import { logger } from './logger';

let wss: WebSocketServer | null = null;
const OPEN = 1; // WebSocket.OPEN constant

export function initWebSocket(server: HTTPServer): void {
  wss = new WebSocketServer({ server, path: '/ws' });

  wss.on('connection', (ws, req) => {
    logger.info(`[JARVIS HUD] Client connected from ${req.socket.remoteAddress}`);

    ws.send(JSON.stringify({
      type: 'JARVIS_ONLINE',
      timestamp: new Date().toISOString(),
      message: 'Prime Directress connected. All systems nominal.',
    }));

    ws.on('message', (raw: Buffer) => {
      try {
        const msg = JSON.parse(raw.toString());
        logger.info(`[JARVIS HUD] Received: ${JSON.stringify(msg)}`);
        if (msg.type === 'VOICE_COMMAND') {
          broadcast({ type: 'COMMAND_RECEIVED', command: msg.command, timestamp: new Date().toISOString() });
        }
      } catch {
        // ignore malformed messages
      }
    });

    ws.on('close', () => logger.info('[JARVIS HUD] Client disconnected'));
    ws.on('error', (err: Error) => logger.error('[JARVIS HUD] WebSocket error:', err));
  });

  logger.info('[JARVIS HUD] WebSocket server initialized on /ws');
}

export function broadcast(payload: object): void {
  if (!wss) return;
  const msg = JSON.stringify(payload);
  wss.clients.forEach((client) => {
    if (client.readyState === OPEN) {
      client.send(msg);
    }
  });
}

export function emitTaskEvent(
  event: 'TASK_CREATED' | 'TASK_COMPLETED' | 'TASK_FAILED' | 'AGENT_UPDATE' | 'SECURITY_ALERT',
  data: object
): void {
  broadcast({ type: event, timestamp: new Date().toISOString(), ...data });
}
