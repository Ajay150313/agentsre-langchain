# Contributing to agentsre-langchain

We love contributions! Here's how to get started.

## Getting Started

1. Fork the repo
2. Clone: `git clone https://github.com/YOUR_USERNAME/agentsre-langchain.git`
3. Install dev dependencies: `pip install -e .[dev]`
4. Create a branch: `git checkout -b feature/your-feature`
5. Make changes and test: `pytest tests/`
6. Commit: `git commit -m "feat: Your feature"`
7. Push: `git push origin feature/your-feature`
8. Open a PR

## Code Style

- Use type hints
- Write docstrings
- 88-character line limit
- Run `black agentsre_langchain/`
- Run `isort agentsre_langchain/`

## Testing

```bash
pytest tests/ -v --cov=agentsre_langchain
```

## Areas We Need Help

- Additional framework integrations (CrewAI, Bedrock, etc.)
- Prometheus exporter
- Grafana dashboard templates
- More examples
- Documentation improvements

---

Created with ❤️ by Ajay Devineni
