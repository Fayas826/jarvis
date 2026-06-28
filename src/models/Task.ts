import mongoose, { Schema, Document } from 'mongoose';

export enum TaskStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export interface ITask extends Document {
  projectId: mongoose.Types.ObjectId;
  type: 'generate_code' | 'analyze_files' | 'run_build' | 'fix_errors' | 'search_files' | 'search_code' | 'commit_changes' | 'run_tests' | 'deploy_release' | 'council_task';
  status: TaskStatus;
  input: any;
  output: any;
  error?: string;
  artifacts: string[];
  createdAt: Date;
  updatedAt: Date;
}

const TaskSchema: Schema = new Schema({
  projectId: { type: Schema.Types.ObjectId, ref: 'Project', required: true },
  type: { 
    type: String, 
    enum: ['generate_code', 'analyze_files', 'run_build', 'fix_errors', 'search_files', 'search_code', 'commit_changes', 'run_tests', 'deploy_release', 'council_task'], 
    required: true 
  },
  status: { type: String, enum: Object.values(TaskStatus), default: TaskStatus.PENDING },
  input: { type: Schema.Types.Mixed },
  output: { type: Schema.Types.Mixed },
  error: { type: String },
  artifacts: [{ type: String }],
}, { timestamps: true });

export default mongoose.model<ITask>('Task', TaskSchema);
