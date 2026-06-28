import express from 'express';
import { projectRouter } from './projects';
import { taskRouter } from './tasks';
import memoryRouter from './memory';
import { apiKeyAuth } from '../security/auth';

const router = express.Router();

// Apply Auth to all enterprise routes
router.use(apiKeyAuth);

router.use('/projects', projectRouter);
router.use('/tasks', taskRouter);
router.use('/memory', memoryRouter);

export { router as apiRouter };
