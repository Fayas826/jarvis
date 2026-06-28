import { Request, Response } from 'express';
import Project from '../models/Project';

export const createProject = async (req: Request, res: Response) => {
  try {
    const { name, githubRepo } = req.body;
    const project = new Project({ name, githubRepo });
    await project.save();
    res.status(201).json(project);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

export const getProject = async (req: Request, res: Response) => {
  try {
    const project = await Project.findById(req.params.projectId);
    if (!project) return res.status(404).json({ error: 'Project not found' });
    res.json(project);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};
