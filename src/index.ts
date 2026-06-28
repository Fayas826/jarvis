import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import * as dotenv from 'dotenv';
import mongoose from 'mongoose';
import http from 'http';
import path from 'path';
import { apiRouter } from './api';
import { logger } from './monitoring/logger';
import { initWebSocket } from './monitoring/websocket';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

// Security & Middleware
app.use(helmet({ contentSecurityPolicy: false })); // disable CSP for HUD inline scripts
app.use(cors());
app.use(express.json());
app.use(morgan('combined', { stream: { write: (message) => logger.info(message.trim()) } }));

// Serve the JARVIS HUD static files
app.use('/hud', express.static(path.join(__dirname, '../public/hud')));

// Routes
app.use('/api/v1', apiRouter);

// Root
app.get('/', (req, res) => {
  res.json({ status: 'JARVIS O.M.E.G.A. Enterprise Backend Online', version: '2.0.0', hud: '/hud' });
});

// Create HTTP server (needed to share with WebSocket)
const server = http.createServer(app);

// Boot WebSocket
initWebSocket(server);

// Database Connection
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/jarvis';
mongoose.connect(MONGO_URI)
  .then(() => logger.info('Successfully connected to MongoDB'))
  .catch((err) => logger.error('MongoDB connection error:', err));

if (process.env.NODE_ENV !== 'test') {
  server.listen(PORT, () => {
    logger.info(`JARVIS HUD available at http://localhost:${PORT}/hud`);
    logger.info(`Server is running on port ${PORT}`);
  });
}

export default app;
