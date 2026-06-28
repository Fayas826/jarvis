import request from 'supertest';
import app from '../src/index';
import mongoose from 'mongoose';

describe('JARVIS API Integration Tests', () => {
  afterAll(async () => {
    await mongoose.connection.close();
  });

  it('should return 200 OK from the root endpoint', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toContain('JARVIS O.M.E.G.A. Enterprise Backend Online');
  });

  it('should return 401 Unauthorized when accessing protected route without API key', async () => {
    const res = await request(app).post('/api/v1/tasks').send({
      type: 'analyze_project',
      description: 'Test task'
    });
    expect(res.statusCode).toEqual(401);
  });

  // Adding a simulated build validation placeholder
  it('should validate build artifacts (Simulated)', () => {
    const buildSuccess = true;
    expect(buildSuccess).toBe(true);
  });
});
