import express, { Request, Response } from 'express';
import { logger } from '../monitoring/logger';

const router = express.Router();

router.post('/github', (req: Request, res: Response) => {
  const event = req.headers['x-github-event'];
  const payload = req.body;

  logger.info(`Received GitHub webhook event: ${event}`);
  
  // Logic to handle different events
  if (event === 'push') {
    logger.info(`Push detected in repo: ${payload.repository?.full_name}`);
  }

  res.status(200).send('Webhook received');
});

export { router as webhookRouter };
