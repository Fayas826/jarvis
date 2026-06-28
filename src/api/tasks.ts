import express from 'express';
import { createTask, getTasks, getTask, cancelTask, getTaskArtifacts } from '../controllers/task.controller';

const router = express.Router();

router.post('/', createTask);
router.get('/', getTasks);
router.get('/:taskId', getTask);
router.post('/:taskId/cancel', cancelTask);
router.get('/:taskId/artifacts', getTaskArtifacts);

export { router as taskRouter };
