import { Router } from 'express';
import {
  storeMemory,
  recallMemories,
  getMemorySnapshot,
  generateStrategy,
  getStrategies,
  updateStrategyItem,
} from '../controllers/memory.controller';

const router = Router();

// ── Memory Routes ──────────────────────────────────────────────────
/** POST /api/memory — Store a new memory */
router.post('/', storeMemory);

/** GET /api/memory — Recall memories with optional filters */
router.get('/', recallMemories);

/** GET /api/memory/snapshot — Full brain dump */
router.get('/snapshot', getMemorySnapshot);

// ── Strategy Routes ────────────────────────────────────────────────
/** POST /api/memory/strategy — Generate a new roadmap */
router.post('/strategy', generateStrategy);

/** GET /api/memory/strategy — List all strategies */
router.get('/strategy', getStrategies);

/** PATCH /api/memory/strategy/:id/item — Update a strategy item */
router.patch('/strategy/:id/item', updateStrategyItem);

export default router;
