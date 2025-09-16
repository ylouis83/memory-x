# Memory-X Documentation Index

Welcome to the Memory-X documentation hub. This folder contains reference
material, configuration guides, and troubleshooting notes for running the
medical memory platform.

## Available Guides

- **[API Reference](api-reference.md)** – HTTP endpoints for the Flask backend
  (memory workflows, DashScope integration, medical graph services).
- **[Configuration Guide](configuration.md)** – Environment variables and
  deployment settings for local, staging, and production environments.
- **[Issue Notes](issues/)** – Known issues and debugging write-ups collected
  during development.

## Suggested Reading Order

1. Start with the [Configuration Guide](configuration.md) to set environment
   variables, database backends, and optional services (DashScope, medical
   graph).
2. Use the [API Reference](api-reference.md) as you build clients or integrate
   with downstream systems.
3. Consult the `issues/` directory for troubleshooting specific behaviours (for
   example, medical graph serialization or storage backends).

For front-end specific information, check
[`frontend/README.md`](../frontend/README.md).
