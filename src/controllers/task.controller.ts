import { Request, Response } from 'express';
import Task, { TaskStatus } from '../models/Task';
import { taskQueue } from '../queues/task.queue';
import { orchestratorQueue } from '../queues/orchestrator.queue';

export const createTask = async (req: Request, res: Response) => {
  try {
    const { projectId, type, input } = req.body;
    const task = new Task({ projectId, type, input });
    await task.save();

    if (type === 'council_task') {
      await orchestratorQueue.add('orchestrate', { taskId: task._id, command: input.prompt || 'Process undefined task' });
    } else {
      // Add to standard BullMQ queue
      await taskQueue.add('execute-task', { taskId: task._id });
    }

    res.status(201).json(task);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

export const getTasks = async (req: Request, res: Response) => {
  try {
    const tasks = await Task.find().sort({ createdAt: -1 }).limit(100);
    res.json(tasks);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

export const getTask = async (req: Request, res: Response) => {
  try {
    const task = await Task.findById(req.params.taskId);
    if (!task) return res.status(404).json({ error: 'Task not found' });
    res.json(task);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

export const cancelTask = async (req: Request, res: Response) => {
  try {
    const task = await Task.findById(req.params.taskId);
    if (!task) return res.status(404).json({ error: 'Task not found' });
    
    if (task.status === TaskStatus.PENDING || task.status === TaskStatus.PROCESSING) {
      task.status = TaskStatus.CANCELLED;
      await task.save();
      return res.json({ message: 'Task cancelled successfully', task });
    }
    
    res.status(400).json({ error: 'Task cannot be cancelled in its current state' });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

export const getTaskArtifacts = async (req: Request, res: Response) => {
  try {
    const task = await Task.findById(req.params.taskId);
    if (!task) return res.status(404).json({ error: 'Task not found' });
    res.json({ artifacts: task.artifacts });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};
