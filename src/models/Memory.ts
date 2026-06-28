import mongoose, { Schema, Document } from 'mongoose';

export type MemoryCategory =
  | 'architecture_decision'
  | 'bug_fix'
  | 'deployment_event'
  | 'security_patch'
  | 'team_preference'
  | 'project_decision'
  | 'performance_insight'
  | 'dependency_change';

export interface IMemory extends Document {
  category: MemoryCategory;
  summary: string;
  detail: string;
  tags: string[];
  relatedFiles: string[];
  importance: 1 | 2 | 3 | 4 | 5; // 5 = critical
  source: 'council' | 'agent' | 'user' | 'auto';
  expiresAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

const MemorySchema = new Schema<IMemory>(
  {
    category: {
      type: String,
      enum: [
        'architecture_decision',
        'bug_fix',
        'deployment_event',
        'security_patch',
        'team_preference',
        'project_decision',
        'performance_insight',
        'dependency_change',
      ],
      required: true,
      index: true,
    },
    summary: { type: String, required: true },
    detail: { type: String, required: true },
    tags: { type: [String], default: [], index: true },
    relatedFiles: { type: [String], default: [] },
    importance: { type: Number, enum: [1, 2, 3, 4, 5], default: 3, index: true },
    source: {
      type: String,
      enum: ['council', 'agent', 'user', 'auto'],
      default: 'auto',
    },
    expiresAt: { type: Date, default: null },
  },
  { timestamps: true }
);

// TTL index — auto-expire low-importance memories
MemorySchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0, sparse: true });

export default mongoose.model<IMemory>('Memory', MemorySchema);
