import { Request, Response, NextFunction } from 'express';
import { UserRole } from '../models/User';

// Extending Express Request to hold our decoded user info
export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    role: UserRole;
    email: string;
  };
}

/**
 * Gatekeeper Middleware to enforce strict Role-Based Access Control (RBAC).
 * Compares the required hierarchy level with the user's actual role.
 */
export const requireRole = (minimumRole: UserRole) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Unauthorized: No valid session token.' });
    }

    const roleHierarchy = {
      [UserRole.USER]: 1,
      [UserRole.TEAM_ADMIN]: 2,
      [UserRole.SUPER_ADMIN]: 3
    };

    const userLevel = roleHierarchy[req.user.role];
    const requiredLevel = roleHierarchy[minimumRole];

    if (userLevel < requiredLevel) {
      return res.status(403).json({ 
        error: 'Forbidden: Security clearance level insufficient.',
        required: minimumRole,
        actual: req.user.role
      });
    }

    // Clearance granted
    next();
  };
};
