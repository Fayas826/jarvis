import mongoose, { Schema, Document } from 'mongoose';

export enum UserRole {
  USER = 'USER',
  TEAM_ADMIN = 'TEAM_ADMIN',
  SUPER_ADMIN = 'SUPER_ADMIN'
}

export interface IUser extends Document {
  email: string;
  passwordHash: string;
  role: UserRole;
  biometricId?: string; // Optional: Used for SuperAdmin physical scan matching
  stripeCustomerId?: string; // Optional: For OpenAI-style billing
  createdAt: Date;
  updatedAt: Date;
}

const UserSchema: Schema = new Schema(
  {
    email: { type: String, required: true, unique: true, index: true },
    passwordHash: { type: String, required: true },
    role: { 
      type: String, 
      enum: Object.values(UserRole), 
      default: UserRole.USER,
      required: true
    },
    biometricId: { type: String, required: false },
    stripeCustomerId: { type: String, required: false }
  },
  { timestamps: true }
);

export const UserModel = mongoose.model<IUser>('User', UserSchema);
