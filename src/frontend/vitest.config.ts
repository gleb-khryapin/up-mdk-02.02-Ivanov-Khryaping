import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "node:path";

const projectRoot = path.resolve(process.cwd(), "../..");
const posixRoot = projectRoot.split(path.sep).join("/");

export default defineConfig({
  plugins: [react()],
  server: {
    fs: { allow: [projectRoot] },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.ts",
    include: [posixRoot + "/tests/frontend/**/*.test.tsx"],
  },
});
