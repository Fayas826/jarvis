import axios from 'axios';
import { logger } from '../../monitoring/logger';

export class GitHubClient {
  private token: string;
  private baseUrl = 'https://api.github.com';

  constructor(token: string) {
    this.token = token;
  }

  async getRepoMetadata(owner: string, repo: string) {
    try {
      const response = await axios.get(`${this.baseUrl}/repos/${owner}/${repo}`, {
        headers: {
          Authorization: `token ${this.token}`,
          Accept: 'application/vnd.github.v3+json',
        },
      });
      return response.data;
    } catch (error: any) {
      logger.error(`GitHub API error: ${error.message}`);
      throw error;
    }
  }

  async createWebhook(owner: string, repo: string, callbackUrl: string) {
    try {
      const response = await axios.post(
        `${this.baseUrl}/repos/${owner}/${repo}/hooks`,
        {
          name: 'web',
          active: true,
          events: ['push', 'pull_request'],
          config: {
            url: callbackUrl,
            content_type: 'json',
          },
        },
        {
          headers: {
            Authorization: `token ${this.token}`,
            Accept: 'application/vnd.github.v3+json',
          },
        }
      );
      return response.data;
    } catch (error: any) {
      logger.error(`GitHub Webhook error: ${error.message}`);
      throw error;
    }
  }
}
