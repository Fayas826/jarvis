import mongoose, { Schema, Document } from 'mongoose';

export type StrategyStatus = 'planned' | 'in_progress' | 'completed' | 'blocked' | 'deprecated';
export type StrategyType =
  | 'refactor'
  | 'security'
  | 'performance'
  | 'feature'
  | 'dependency_upgrade'
  | 'release'
  | 'architectural_evolution';

export interface IStrategyItem {
  title: string;
  description: string;
  priority: 1 | 2 | 3; // 1=high
  estimatedHours: number;
  status: StrategyStatus;
  assignedAgent?: string;
  completedAt?: Date;
}

export interface IStrategy extends Document {
  title: string;
  type: StrategyType;
  goal: string;
  weekOf: Date;
  items: IStrategyItem[];
  overallStatus: StrategyStatus;
  generatedBy: 'council' | 'user' | 'auto';
  notes: string;
  createdAt: Date;
  updatedAt: Date;
}

const StrategyItemSchema = new Schema<IStrategyItem>({
  title: { type: String, required: true },
  description: { type: String, required: true },
  priority: { type: Number, enum: [1, 2, 3], default: 2 },
  estimatedHours: { type: Number, default: 1 },
  status: {
    type: String,
    enum: ['planned', 'in_progress', 'completed', 'blocked', 'deprecated'],
    default: 'planned',
  },
  assignedAgent: { type: String },
  completedAt: { type: Date },
});

const StrategySchema = new Schema<IStrategy>(
  {
    title: { type: String, required: true },
    type: {
      type: String,
      enum: [
        'refactor',
        'security',
        'performance',
        'feature',
        'dependency_upgrade',
        'release',
        'architectural_evolution',
      ],
      required: true,
      index: true,
    },
    goal: { type: String, required: true },
    weekOf: { type: Date, required: true, index: true },
    items: { type: [StrategyItemSchema], default: [] },
    overallStatus: {
      type: String,
      enum: ['planned', 'in_progress', 'completed', 'blocked', 'deprecated'],
      default: 'planned',
    },
    generatedBy: { type: String, enum: ['council', 'user', 'auto'], default: 'auto' },
    notes: { type: String, default: '' },
  },
  { timestamps: true }
);

export default mongoose.model<IStrategy>('Strategy', StrategySchema);
