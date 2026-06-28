import { Request, Response } from 'express';
import Memory, { MemoryCategory } from '../models/Memory';
import Strategy from '../models/Strategy';

// ─── MEMORY ────────────────────────────────────────────────────────────────

/** Store a new memory entry */
export const storeMemory = async (req: Request, res: Response) => {
  try {
    const { category, summary, detail, tags, relatedFiles, importance, source, expiresAt } = req.body;
    const memory = await Memory.create({
      category,
      summary,
      detail,
      tags: tags || [],
      relatedFiles: relatedFiles || [],
      importance: importance || 3,
      source: source || 'auto',
      expiresAt: expiresAt || null,
    });
    res.status(201).json({ success: true, memory });
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
};

/** Recall memories — optionally filter by category, tags, importance */
export const recallMemories = async (req: Request, res: Response) => {
  try {
    const { category, tags, importance, limit = 50 } = req.query;
    const filter: any = {};
    if (category) filter.category = category;
    if (importance) filter.importance = { $gte: Number(importance) };
    if (tags) filter.tags = { $in: (tags as string).split(',') };

    const memories = await Memory.find(filter)
      .sort({ importance: -1, createdAt: -1 })
      .limit(Number(limit));

    res.json({ success: true, count: memories.length, memories });
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
};

/** Get a full memory snapshot — the brain dump */
export const getMemorySnapshot = async (_req: Request, res: Response) => {
  try {
    const [total, critical, recent, byCategory] = await Promise.all([
      Memory.countDocuments(),
      Memory.find({ importance: 5 }).sort({ createdAt: -1 }).limit(10),
      Memory.find().sort({ createdAt: -1 }).limit(5),
      Memory.aggregate([{ $group: { _id: '$category', count: { $sum: 1 } } }]),
    ]);
    res.json({ success: true, total, critical, recent, byCategory });
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
};

// ─── STRATEGY ──────────────────────────────────────────────────────────────

/** Generate a new weekly strategy roadmap */
export const generateStrategy = async (req: Request, res: Response) => {
  try {
    const { title, type, goal, weekOf, items, notes } = req.body;

    // Auto-seed from critical memories if no items provided
    let strategyItems = items;
    if (!strategyItems || strategyItems.length === 0) {
      const criticalMemories = await Memory.find({ importance: { $gte: 4 } })
        .sort({ createdAt: -1 })
        .limit(5);

      strategyItems = criticalMemories.map((m, i) => ({
        title: `Address: ${m.summary}`,
        description: m.detail,
        priority: m.importance >= 5 ? 1 : 2,
        estimatedHours: 2,
        status: 'planned',
      }));
    }

    const strategy = await Strategy.create({
      title,
      type: type || 'architectural_evolution',
      goal,
      weekOf: weekOf ? new Date(weekOf) : new Date(),
      items: strategyItems,
      generatedBy: req.body.generatedBy || 'auto',
      notes: notes || '',
    });

    // Store as a memory too
    await Memory.create({
      category: 'architecture_decision',
      summary: `Strategy Created: ${title}`,
      detail: goal,
      tags: ['strategy', type || 'architectural_evolution'],
      importance: 4,
      source: 'auto',
    });

    res.status(201).json({ success: true, strategy });
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
};

/** Get all active strategies */
export const getStrategies = async (req: Request, res: Response) => {
  try {
    const { status, type } = req.query;
    const filter: any = {};
    if (status) filter.overallStatus = status;
    if (type) filter.type = type;

    const strategies = await Strategy.find(filter).sort({ weekOf: -1 });
    res.json({ success: true, count: strategies.length, strategies });
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
};

/** Update a strategy item's status */
export const updateStrategyItem = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { itemIndex, status, assignedAgent } = req.body;
    const strategy = await Strategy.findById(id);
    if (!strategy) return res.status(404).json({ error: 'Strategy not found' });

    strategy.items[itemIndex].status = status;
    if (assignedAgent) strategy.items[itemIndex].assignedAgent = assignedAgent;
    if (status === 'completed') strategy.items[itemIndex].completedAt = new Date();

    const allDone = strategy.items.every(i => i.status === 'completed');
    if (allDone) strategy.overallStatus = 'completed';

    await strategy.save();
    res.json({ success: true, strategy });
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
};
