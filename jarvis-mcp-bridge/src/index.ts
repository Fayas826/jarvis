import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";
import dotenv from "dotenv";
import puppeteer from "puppeteer";
// @ts-ignore
import screenshot from "screenshot-desktop";
import fs from "fs";

// @ts-ignore
dotenv.config({ quiet: true });

// Ensure MCP doesn't see "injected env" logs
if (process.stdout.isTTY) {
  // Only log if in a real terminal, not an MCP stream
}

const JARVIS_API = process.env.JARVIS_API || "http://localhost:4000/api/v1";
const JARVIS_KEY = process.env.JARVIS_KEY || "";
const PROJECT_ID = process.env.PROJECT_ID || "default-project";



class JarvisMcpServer {
  private server: Server;
  private axiosInstance;

  constructor() {
    this.server = new Server(
      {
        name: "jarvis-mcp-bridge",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.axiosInstance = axios.create({
      baseURL: JARVIS_API,
      headers: {
        "x-api-key": JARVIS_KEY,
        "Content-Type": "application/json",
      },
    });

    this.setupToolHandlers();
    
    // Error handling
    this.server.onerror = (_error) => {}; 
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "jarvis_generate_code",
          description: "Generate production-grade code using JARVIS Enterprise core",
          inputSchema: {
            type: "object",
            properties: {
              prompt: { type: "string", description: "What code should JARVIS build?" },
            },
            required: ["prompt"],
          },
        },
        {
          name: "jarvis_analyze_project",
          description: "Run a deep architectural and security scan of the project",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "jarvis_fix_errors",
          description: "Automatically identify and repair build/logic errors",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "jarvis_search_code",
          description: "Search for specific patterns or logic across the whole project",
          inputSchema: {
            type: "object",
            properties: {
              query: { type: "string", description: "The term or pattern to find" },
            },
            required: ["query"],
          },
        },
        {
          name: "jarvis_commit_changes",
          description: "Git automation: edit files, commit changes, push branches, and create pull requests",
          inputSchema: {
            type: "object",
            properties: {
              message: { type: "string", description: "Commit message for the changes" },
              files: { 
                type: "array", 
                items: { type: "string" },
                description: "Array of file paths to include in the commit"
              }
            },
            required: ["message"],
          },
        },
        {
          name: "jarvis_run_tests",
          description: "Run automated tests (Jest, API integration), validate Docker builds, and automatically repair failures before commits",
          inputSchema: {
            type: "object",
            properties: {},
            required: [],
          },
        },
        {
          name: "jarvis_deploy_release",
          description: "Automatically deploy latest branch to staging/production using Github Actions and Docker",
          inputSchema: {
            type: "object",
            properties: {
              environment: { type: "string", description: "Target environment (e.g., staging, production)" }
            },
            required: [],
          },
        },
        {
          name: "jarvis_council_task",
          description: "Initiate a complex Multi-Agent Council task. The Orchestrator will split this into sub-tasks for specialized agents.",
          inputSchema: {
            type: "object",
            properties: {
              prompt: { type: "string", description: "The overarching goal for the Swarm to accomplish." }
            },
            required: ["prompt"],
          },
        },
        {
          name: "jarvis_browser_action",
          description: "Run an autonomous browser action (navigate, click, read, screenshot) on the host machine.",
          inputSchema: {
            type: "object",
            properties: {
              url: { type: "string", description: "The URL to navigate to." },
              action: { type: "string", description: "The action to perform (e.g., read_page, screenshot, click)." },
              selector: { type: "string", description: "CSS selector for click actions." }
            },
            required: ["url", "action"],
          },
        },
        {
          name: "jarvis_take_screenshot",
          description: "Take a screenshot of the host's actual physical desktop.",
          inputSchema: {
            type: "object",
            properties: {},
            required: [],
          },
        },
        {
          name: "jarvis_memory",
          description: "Store or recall persistent JARVIS memories: architecture decisions, bug fixes, team preferences, deployment history, and security patches.",
          inputSchema: {
            type: "object",
            properties: {
              action: { type: "string", description: "'store', 'recall', or 'snapshot'" },
              category: { type: "string", description: "Memory category (architecture_decision, bug_fix, security_patch, etc.)" },
              summary: { type: "string", description: "Short memory summary" },
              detail: { type: "string", description: "Full detail of the memory" },
              tags: { type: "array", items: { type: "string" }, description: "Tags for filtering" },
              importance: { type: "number", description: "1-5, where 5 is critical" }
            },
            required: ["action"],
          },
        },
        {
          name: "jarvis_strategy",
          description: "Generate or retrieve long-term engineering roadmaps, weekly plans, refactor priorities, and release schedules.",
          inputSchema: {
            type: "object",
            properties: {
              action: { type: "string", description: "'generate' or 'list'" },
              title: { type: "string", description: "Strategy title" },
              goal: { type: "string", description: "The overarching goal of this strategy" },
              type: { type: "string", description: "Strategy type: refactor, security, performance, feature, release, architectural_evolution" },
              items: { type: "array", description: "Optional list of strategy items" }
            },
            required: ["action"],
          },
        },
        {
          name: "jarvis_avatar",
          description: "Launch or get the URL of the JARVIS HUD — a Tony Stark-style control center showing live agents, tasks, system health, and voice commands.",
          inputSchema: { type: "object", properties: {}, required: [] },
        },
        {
          name: "jarvis_voice",
          description: "Send a voice command or spoken directive to JARVIS via the HUD WebSocket. JARVIS will speak back and route the command to the appropriate agent.",
          inputSchema: {
            type: "object",
            properties: { command: { type: "string", description: "The voice command to send" } },
            required: ["command"],
          },
        }
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        let taskType = "";
        let input = args || {};

        switch (name) {
          case "jarvis_generate_code":
            taskType = "generate_code";
            break;
          case "jarvis_analyze_files":
            taskType = "analyze_files";
            break;
          case "jarvis_run_build":
            taskType = "run_build";
            break;
          case "jarvis_fix_errors":
            taskType = "fix_errors";
            break;
          case "jarvis_search_files":
            taskType = "search_files";
            break;
          case "jarvis_search_code":
            taskType = "search_code";
            break;
          case "jarvis_commit_changes":
            taskType = "commit_changes";
            break;
          case "jarvis_run_tests":
            taskType = "run_tests";
            break;
          case "jarvis_deploy_release":
            taskType = "deploy_release";
            break;
          case "jarvis_council_task":
            taskType = "council_task";
            break;
          case "jarvis_take_screenshot":
            try {
              const imgPath = "desktop_screenshot_" + Date.now() + ".jpg";
              await screenshot({ filename: imgPath });
              const stats = fs.statSync(imgPath);
              return {
                content: [{ type: "text", text: `Screenshot successfully taken and saved to ${imgPath} (${stats.size} bytes)` }]
              };
            } catch (err: any) {
              return { content: [{ type: "text", text: `Screenshot failed: ${err.message}` }] };
            }
          case "jarvis_browser_action":
            try {
              const args = request.params.arguments as any;
              const browser = await puppeteer.launch({ headless: "new" as any });
              const page = await browser.newPage();
              await page.goto(args.url || "https://google.com");
              let resultStr = "Navigated successfully.";
              
              if (args.action === "read_page") {
                const title = await page.title();
                // @ts-ignore
                const content = await page.evaluate(() => (document as any).body.innerText.substring(0, 2000));
                resultStr = `Title: ${title}\nContent: ${content}`;
              } else if (args.action === "screenshot") {
                await page.screenshot({ path: 'browser_screenshot.png' });
                resultStr = "Browser screenshot saved to browser_screenshot.png";
              }
              
              await browser.close();
              return { content: [{ type: "text", text: resultStr }] };
            } catch (err: any) {
              return { content: [{ type: "text", text: `Browser action failed: ${err.message}` }] };
            }
          case "jarvis_memory": {
            try {
              const a = request.params.arguments as any;
              let endpoint = "/memory";
              let method: "get" | "post" = "post";
              let payload: any = {};

              if (a.action === "store") {
                method = "post";
                payload = {
                  category: a.category || "project_decision",
                  summary: a.summary || "",
                  detail: a.detail || "",
                  tags: a.tags || [],
                  importance: a.importance || 3,
                  source: "agent",
                };
              } else if (a.action === "recall") {
                method = "get";
                const params = new URLSearchParams();
                if (a.category) params.set("category", a.category);
                if (a.tags) params.set("tags", a.tags.join(","));
                if (a.importance) params.set("importance", a.importance);
                endpoint = `/memory?${params.toString()}`;
              } else if (a.action === "snapshot") {
                method = "get";
                endpoint = "/memory/snapshot";
              }

              const res = method === "post"
                ? await this.axiosInstance.post(endpoint, payload)
                : await this.axiosInstance.get(endpoint);

              return { content: [{ type: "text", text: JSON.stringify(res.data, null, 2) }] };
            } catch (err: any) {
              return { content: [{ type: "text", text: `Memory operation failed: ${err.message}` }] };
            }
          }
          case "jarvis_strategy": {
            try {
              const a = request.params.arguments as any;
              let res: any;
              if (a.action === "generate") {
                res = await this.axiosInstance.post("/memory/strategy", {
                  title: a.title || "Auto-Generated Roadmap",
                  goal: a.goal || "",
                  type: a.type || "architectural_evolution",
                  items: a.items || [],
                  generatedBy: "council",
                });
              } else {
                res = await this.axiosInstance.get("/memory/strategy");
              }
              return { content: [{ type: "text", text: JSON.stringify(res.data, null, 2) }] };
            } catch (err: any) {
              return { content: [{ type: "text", text: `Strategy operation failed: ${err.message}` }] };
            }
          }
          case "jarvis_avatar":
            return {
              content: [{
                type: "text",
                text: `JARVIS HUD is live at: http://localhost:4000/hud\n\nOpen this URL in your browser for the Tony Stark-style control center.\nFeatures: Live task stream, agent status, system vitals, voice commands, WebSocket real-time updates.\nWebSocket endpoint: ws://localhost:4000/ws`
              }]
            };
          case "jarvis_voice": {
            const cmd = (request.params.arguments as any)?.command || "";
            try {
              // Dispatch voice command as a task
              const taskType = cmd.toLowerCase().includes('deploy') ? 'deploy_release'
                : cmd.toLowerCase().includes('scan') || cmd.toLowerCase().includes('security') ? 'fix_errors'
                : cmd.toLowerCase().includes('generate') || cmd.toLowerCase().includes('build') ? 'generate_code'
                : cmd.toLowerCase().includes('council') ? 'council_task'
                : 'analyze_files';
              const res = await this.axiosInstance.post("/tasks", {
                projectId: "voice-command",
                type: taskType,
                input: { prompt: cmd, source: "voice" }
              });
              return { content: [{ type: "text", text: `🎤 Voice command received: "${cmd}"\n✅ Dispatched as ${taskType}\nTask ID: ${res.data._id}\n\nJARVIS says: "Understood. Dispatching to Prime Directress."` }] };
            } catch (err: any) {
              return { content: [{ type: "text", text: `Voice dispatch failed: ${err.message}` }] };
            }
          }
          default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);


        }

        // 1. Create Task
        const createRes = await this.axiosInstance.post("/tasks", {
          projectId: PROJECT_ID,
          type: taskType,
          input: input
        });

        const taskId = createRes.data._id;

        // 2. Poll for Completion
        let completed = false;
        let result = null;
        let attempts = 0;
        
        while (!completed && attempts < 30) {
          await new Promise(r => setTimeout(r, 2000));
          const statusRes = await this.axiosInstance.get(`/tasks/${taskId}`);
          const task = statusRes.data;

          if (task.status === "completed") {
            completed = true;
            result = task.output;
          } else if (task.status === "failed") {
            throw new Error(`JARVIS Task Failed: ${task.error}`);
          }
          attempts++;
        }

        if (!completed) {
          return {
            content: [{ type: "text", text: `Task timed out. Check status later. ID: ${taskId}` }],
            isError: true
          };
        }

        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };

      } catch (error: any) {
        return {
          content: [{ type: "text", text: `Error: ${error.message}` }],
          isError: true,
        };
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    // console.error("JARVIS MCP Bridge running on stdio");
  }
}

const server = new JarvisMcpServer();
server.run().catch(() => {});

