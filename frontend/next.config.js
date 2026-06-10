/** @type {import('next').NextConfig} */
const nextConfig = {
  // Standalone only for Docker production builds
  ...(process.env.DOCKER_BUILD === "true" ? { output: "standalone" } : {}),
};

module.exports = nextConfig;
