# Changelog

## [0.1.1]

### Fixed
- README and examples used `@monitor_agent(..., config=MonitorConfig(...))` and
  `get_metrics()`, which the 0.1.0 decorator did not support. `collector` is now optional
  (defaults to a shared collector), `config=` is accepted, and `get_metrics()` is exported.
- Removed a personal employer email address from package metadata.

### Added
- `async_monitor_agent`, `MetricsCollector`, `ExecutionMetrics`, `get_default_collector`,
  `reset_default_collector` exported from the package root.
- Decorator tests (sync, async, failure path, default collector, isolation).

## Unreleased

### Added
- `DuplicateToolCallGuard` — windowed block/count for identical tool starts

## [0.1.0] - 2026-05-26

### Added
- Initial release of agentsre-langchain
- @monitor_agent decorator for LangChain agents
- Semantic SLI tracking (DQR, TIE, HER metrics)
- Cost tracking integration
- 5 working examples
- agentsre core integration
- Full documentation

### Features
- Monitor agent decision quality
- Track tool invocation efficiency
- Monitor human escalation rates
- Cost tracking per execution
- Integration with agentsre

---

## Planned (v0.2.0)

- Prometheus exporter
- Grafana dashboard templates
- CrewAI integration
- AWS Bedrock integration
- Additional framework support
