import mongoose, { Schema, Document } from 'mongoose';

export interface IProject extends Document {
  name: string;
  githubRepo?: string;
  createdAt: Date;
}

const ProjectSchema: Schema = new Schema({
  name: { type: String, required: true },
  githubRepo: { type: String },
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model<IProject>('Project', ProjectSchema);
