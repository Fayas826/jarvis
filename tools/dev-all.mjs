import { spawn, spawnSync } from "node:child_process";
import process from "node:process";

const isWindows = process.platform === "win32";
const npmCmd = isWindows ? "npm.cmd" : "npm";

const processes = [
  { name: "hud", command: npmCmd, args: ["run", "dev:hud"] },
  { name: "core", command: npmCmd, args: ["run", "dev:core"] },
  { name: "enterprise", command: npmCmd, args: ["run", "dev:backend"] }
];

console.log("[BUILD] Compiling C++ Audio Accelerator...");
const compileCmd = isWindows ? "g++" : "g++"; // Assuming g++ is available
const compileArgs = ["-shared", "-o", "core/perception/audio/jarvis_audio.dll", "core/perception/audio/jarvis_audio_engine.cpp"];
const compileResult = spawnSync(compileCmd, compileArgs, { stdio: "inherit" });
if (compileResult.status !== 0) {
    console.error("[BUILD] C++ compilation failed. Falling back to Python audio engine.");
} else {
    console.log("[BUILD] C++ compilation successful.");
}

const children = processes.map(({ name, command, args }) => {
  const child = spawn(command, args, {
    cwd: process.cwd(),
    env: process.env,
    stdio: ["ignore", "pipe", "pipe"]
  });

  child.stdout.on("data", (chunk) => process.stdout.write(`[${name}] ${chunk}`));
  child.stderr.on("data", (chunk) => process.stderr.write(`[${name}] ${chunk}`));
  child.on("exit", (code, signal) => {
    if (code && code !== 0) {
      console.error(`[${name}] exited with code ${code}`);
    }
    if (signal) {
      console.error(`[${name}] stopped by ${signal}`);
    }
  });

  return child;
});

const shutdown = () => {
  for (const child of children) {
    if (!child.killed) child.kill();
  }
};

process.on("SIGINT", () => {
  shutdown();
  process.exit(130);
});
process.on("SIGTERM", () => {
  shutdown();
  process.exit(143);
});
