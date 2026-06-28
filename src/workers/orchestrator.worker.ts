import { Worker, Job, Queue } from 'bullmq';
import IORedis from 'ioredis';
import mongoose from 'mongoose';
import Task, { TaskStatus } from '../models/Task';
import * as dotenv from 'dotenv';

dotenv.config();

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/jarvis';

const connection = new IORedis(REDIS_URL, { maxRetriesPerRequest: null });

// Queue for the actual task execution worker (sub-tasks)
const taskQueue = new Queue('task-queue', { connection });

// Connect to MongoDB
mongoose.connect(MONGO_URI).then(() => console.log('[Prime Directress] Connected to MongoDB')).catch(console.error);

const orchestratorWorker = new Worker('orchestrator-queue', async (job: Job) => {
  const { taskId, command } = job.data;
  console.log(`[Prime Directress] Orchestrating task ${taskId}: ${command}`);

  try {
    const task = await Task.findById(taskId);
    if (!task) throw new Error('Task not found');

    task.status = TaskStatus.PROCESSING;
    await task.save();

    // In a full implementation, we'd use an LLM here to break the command into sub-tasks.
    // For now, we simulate the Master Node delegating standard tasks based on keywords.
    const subTasks = [];

    if (command.toLowerCase().includes('audit') || command.toLowerCase().includes('security')) {
      console.log(`[Prime Directress] Delegating to Security Auditor...`);
      const subTask = await Task.create({
        projectId: task.projectId,
        type: 'analyze_files',
        status: TaskStatus.PENDING,
        input: { target: '.', analysis_type: 'security_audit' },
        artifacts: []
      });
      subTasks.push(subTask._id);
      await taskQueue.add('process-task', { taskId: subTask._id, role: 'security_auditor' });
    }

    if (command.toLowerCase().includes('deploy') || command.toLowerCase().includes('release')) {
      console.log(`[Prime Directress] Delegating to Executioner...`);
      const subTask = await Task.create({
        projectId: task.projectId,
        type: 'deploy_release',
        status: TaskStatus.PENDING,
        input: { environment: 'staging' },
        artifacts: []
      });
      subTasks.push(subTask._id);
      // Wait a moment so tasks are queued properly
      await new Promise(res => setTimeout(res, 500));
      await taskQueue.add('process-task', { taskId: subTask._id, role: 'executioner' });
    }

    // Default to a generate code task if it's generic
    if (subTasks.length === 0) {
      console.log(`[Prime Directress] Delegating to Code Engineer...`);
      const subTask = await Task.create({
        projectId: task.projectId,
        type: 'generate_code',
        status: TaskStatus.PENDING,
        input: { prompt: command },
        artifacts: []
      });
      subTasks.push(subTask._id);
      await taskQueue.add('process-task', { taskId: subTask._id, role: 'code_engineer' });
    }

    // Wait for subtasks to finish (naive polling for simulation)
    let allFinished = false;
    let finalOutput: any[] = [];
    while (!allFinished) {
      await new Promise(res => setTimeout(res, 2000));
      const activeSubtasks = await Task.find({ _id: { $in: subTasks } });
      const pending = activeSubtasks.filter((t: any) => t.status === TaskStatus.PENDING || t.status === TaskStatus.PROCESSING);
      if (pending.length === 0) {
        allFinished = true;
        finalOutput = activeSubtasks.map((t: any) => ({ id: t._id, type: t.type, status: t.status, output: t.output || t.error }));
      }
    }

    task.status = TaskStatus.COMPLETED;
    task.output = {
      message: 'Council execution complete',
      subTasks: finalOutput
    };
    await task.save();
    console.log(`[Prime Directress] Task ${taskId} successfully orchestrated.`);
    return task.output;

  } catch (error: any) {
    console.error(`[Prime Directress] Error orchestrating task ${taskId}:`, error);
    await Task.findByIdAndUpdate(taskId, {
      status: TaskStatus.FAILED,
      error: error.message
    });
    throw error;
  }
}, { connection });

console.log('Orchestrator Worker (Prime Directress) started and listening to orchestrator-queue');

orchestratorWorker.on('failed', (job: Job | undefined, err: Error) => {
  console.error(`[Prime Directress] Job ${job?.id} failed:`, err);
});
