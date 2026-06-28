import express from 'express';
import { createProject, getProject } from '../controllers/project.controller';

const router = express.Router();

router.post('/', createProject);
router.get('/:projectId', getProject);

export { router as projectRouter };
