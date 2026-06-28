import mongoose, { Schema, Document } from 'mongoose';

export interface IAuditLog extends Document {
  action: string;
  details: any;
  environment: string;
  status: string;
  createdAt: Date;
}

const AuditLogSchema: Schema = new Schema({
  action: { type: String, required: true },
  details: { type: Schema.Types.Mixed },
  environment: { type: String, default: 'unknown' },
  status: { type: String, required: true }
}, { timestamps: true });

export default mongoose.model<IAuditLog>('AuditLog', AuditLogSchema);
