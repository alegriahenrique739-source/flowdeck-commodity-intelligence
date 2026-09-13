// Isolated loopback rehearsal, never a hosting entrypoint.
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, writeFileSync, realpathSync, rmSync } from "node:fs";
import { createServer, get } from "node:https";
import { createServer as tcpServer } from "node:net";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

if (process.env.FLOWDECK_PUBLIC_TEST_FIXTURE !== "true" || !process.send)
  throw new Error("Only Playwright may start this loopback fixture.");
if (process.env.NODE_TLS_REJECT_UNAUTHORIZED === "0")
  throw new Error("Global TLS bypass is not permitted.");

const frontend = fileURLToPath(new URL("../../", import.meta.url));
const root = resolve(frontend, "..");
const origin = "https://localhost:3443";
const api = "https://localhost:8444";
const children = [];
let web;
let app;
let directory;
let stopping = false;
let stage = "initialization";

async function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  if (web) {
    web.closeAllConnections();
    await new Promise((done) => web.close(done));
  }
  await app?.close();
  for (const child of children) {
    if (child.exitCode !== null || !child.pid) continue;
    const exited = new Promise((done) => child.once("exit", done));
    if (process.platform === "win32")
      spawnSync("taskkill", ["/PID", String(child.pid), "/T", "/F"], { windowsHide: true });
    else child.kill("SIGTERM");
    await exited;
  }
  // Delete only the exact temporary directory created by this process, never repo runs.
  if (directory && realpathSync(directory) === directory && dirname(directory) === realpathSync(tmpdir()))
    rmSync(directory, { recursive: true, force: true });
  process.exit(code);
}
process.on("disconnect", () => void stop());
process.on("message", (message) => { if (message === "stop") void stop(); });
process.on("SIGTERM", () => void stop());

async function requireFreePort(port) {
  const socket = tcpServer();
  await new Promise((done, reject) => {
    socket.once("error", reject);
    socket.listen(port, "127.0.0.1", done);
  });
  await new Promise((done) => socket.close(done));
}

async function ready(ca) {
  for (let attempt = 0; attempt < 120; attempt++) {
    if (children.some((child) => child.exitCode !== null)) throw new Error("Backend exited");
    const ok = await new Promise((done) => {
      const req = get(`${api}/api/info`, { ca, family: 4 }, (response) => {
        let text = "";
        response.on("data", (chunk) => { text += chunk; });
        response.on("end", () => {
          try { done(response.statusCode === 200 && JSON.parse(text).environment === "public_demo"); }
          catch { done(false); }
        });
      });
      req.on("error", () => done(false));
      req.setTimeout(1000, () => req.destroy());
    });
    if (ok) return;
    await new Promise((done) => setTimeout(done, 250));
  }
  throw new Error("Public backend readiness timed out");
}

try {
  if (!existsSync(join(frontend, ".next", "BUILD_ID"))) throw new Error("Build required");
  stage = "ports 3443/8444 (must be free)";
  await requireFreePort(3443);
  await requireFreePort(8444);
  directory = realpathSync(mkdtempSync(join(realpathSync(tmpdir()), "flowdeck-public-qa-")));
  const python = process.env.FLOWDECK_TEST_PYTHON || "uv";
  const args = process.env.FLOWDECK_TEST_PYTHON ? [] : [
    "run", "--cache-dir", ".uv-cache", "--with-requirements", "requirements-qa.txt", "python",
  ];
  stage = "ephemeral TLS";
  const generated = spawnSync(python, [...args, "tests/fixtures/pilot_test_tls.py"], {
    cwd: root, windowsHide: true, encoding: "utf8", timeout: 30000,
  });
  if (generated.status !== 0) throw new Error("Certificate generation failed");
  const tls = JSON.parse(generated.stdout);
  writeFileSync(join(directory, "cert.pem"), tls.cert);
  writeFileSync(join(directory, "key.pem"), tls.key, { mode: 0o600 });
  stage = "real public API";
  const child = spawn(python, [...args, "tests/fixtures/public_demo_service.py"], {
    cwd: root, windowsHide: true, stdio: ["ignore", "pipe", "pipe"],
    env: {
      ...process.env,
      FLOWDECK_PUBLIC_TEST_FIXTURE: "true", FLOWDECK_TEST_ROOT: directory,
      FLOWDECK_DEPLOYMENT_MODE: "public_demo", FLOWDECK_ENABLE_LOCAL_IMPORTS: "false",
      FLOWDECK_ALLOWED_ORIGINS: origin, FLOWDECK_PUBLIC_MAX_RUNS: "1",
    },
  });
  children.push(child);
  child.stdout.resume();
  child.stderr.resume();
  child.on("error", () => { process.send?.({ error: "Public QA Python process unavailable" }); void stop(1); });
  await ready(tls.ca);
  stage = "production Next HTTPS server";
  const { default: next } = await import("next");
  app = next({ dev: false, dir: frontend, hostname: "localhost", port: 3443 });
  await app.prepare();
  const handler = app.getRequestHandler();
  web = createServer({ cert: tls.cert, key: tls.key }, (req, res) => {
    if (req.headers.host !== "localhost:3443") { res.writeHead(400).end(); return; }
    req.headers["x-forwarded-proto"] = "https";
    req.headers["x-forwarded-host"] = "localhost:3443";
    req.headers["x-forwarded-port"] = "3443";
    void handler(req, res);
  });
  await new Promise((done, reject) => {
    web.once("error", reject);
    web.listen(3443, "127.0.0.1", done);
  });
  process.send({ ready: true, origin, api, pin: tls.pin, ca: tls.ca, directory });
} catch {
  process.send?.({ error: `Public rehearsal failed at ${stage}. Check the documented build/runtime and free loopback ports.` });
  await stop(1);
}
