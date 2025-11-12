# Poe the Poet Task Guidelines

## Overview

This document outlines the guidelines for using Poe the Poet task types in the BPSR Labs project. Understanding the distinction between `cmd`, `script`, and `shell` types is crucial for maintaining consistency and leveraging Poe's capabilities effectively.

## Task Type Guidelines

### `script` Type - For Python CLI Functions

**When to use:**
- Python functions that are part of your package's CLI
- Tasks that need access to your package's modules and dependencies
- Functions that should run in the same Python environment as your project

**Advantages:**
- Direct access to your package's modules and dependencies
- Better integration with Poetry's virtual environment
- Type hints and IDE support work properly
- Automatic dependency resolution

**Example:**
```toml
[tool.poe.tasks]
update-items = { script = "bpsr_labs.cli:update_items", help = "Update item name mappings" }
decode = { script = "bpsr_labs.cli:decode", help = "Decode BPSR packets" }
dps = { script = "bpsr_labs.cli:dps", help = "Calculate DPS from combat data" }
```

**Best practices:**
- Use for all Python CLI functions
- Reference functions by module path (e.g., `module:function`)
- Ensure functions have proper type hints
- Keep functions focused and single-purpose

### `cmd` Type - For External Tools

**When to use:**
- External command-line tools not part of your Python package
- System commands and utilities
- Tools that don't need access to your package's modules

**Advantages:**
- Direct execution of external commands
- No Python overhead
- Clear separation of concerns
- Easy to debug and test independently

**Example:**
```toml
[tool.poe.tasks]
init-submodules = { cmd = "git submodule update --init --recursive", help = "Initialize git submodules" }
install = { cmd = "poetry install --with dev", help = "Install dependencies" }
```

**Best practices:**
- Use for external tools and system commands
- Keep commands simple and focused
- Use absolute paths when necessary
- Consider cross-platform compatibility

### `shell` Type - For Complex Commands

**When to use:**
- Commands that need shell features (pipes, redirection, etc.)
- Complex command sequences
- Commands that need to run in Poetry's environment but aren't Python functions

**Advantages:**
- Access to shell features
- Can chain commands
- Runs in Poetry's environment when prefixed with `poetry run`

**Example:**
```toml
[tool.poe.tasks]
generate-protos = { shell = "poetry run python scripts/generate_protos.py", help = "Generate protobuf modules" }
clean-protos = { shell = "poetry run python scripts/generate_protos.py --clean", help = "Clean protobuf modules" }
```

**Best practices:**
- Use when you need shell features
- Prefix with `poetry run` to ensure correct Python environment
- Keep commands readable and maintainable
- Consider breaking complex commands into multiple tasks

## Decision Matrix

| Scenario | Recommended Type | Reason |
|----------|------------------|---------|
| Python CLI function | `script` | Direct access to package modules |
| External tool (git, npm, etc.) | `cmd` | No Python overhead needed |
| Python script with Poetry env | `shell` | Need Poetry's Python environment |
| Complex shell commands | `shell` | Need shell features |
| Simple system commands | `cmd` | Direct execution |

## Current Project Implementation

### Setup Tasks
```toml
init-submodules = { cmd = "git submodule update --init --recursive", help = "Initialize git submodules" }
generate-protos = { shell = "poetry run python scripts/generate_protos.py", help = "Generate protobuf modules" }
install = { cmd = "poetry install --with dev", help = "Install dependencies" }
update-items = { script = "bpsr_labs.cli:update_items", help = "Update item name mappings" }
```

### Development Tasks
```toml
decode = { script = "bpsr_labs.cli:decode", help = "Decode BPSR packets" }
dps = { script = "bpsr_labs.cli:dps", help = "Calculate DPS from combat data" }
trade-decode = { script = "bpsr_labs.cli:trade_decode", help = "Decode trading center data" }
```

### Code Quality Tasks
```toml
format = { shell = "poetry run black src/ tests/ scripts/", help = "Format code with black" }
lint = { shell = "poetry run ruff check src/ tests/ scripts/", help = "Lint code with ruff" }
typecheck = { shell = "poetry run mypy src/", help = "Type check with mypy" }
```

## Migration Guidelines

When migrating from Poetry scripts to Poe tasks:

1. **Identify the task type:**
   - If it's a Python function in your package → `script`
   - If it's an external tool → `cmd`
   - If it needs Poetry's environment → `shell`

2. **Update the task definition:**
   - Replace `[project.scripts]` with `[tool.poe.tasks]`
   - Use appropriate task type
   - Add help text for better documentation

3. **Test the migration:**
   - Run the task individually
   - Verify it works in the full sequence
   - Check for any environment issues

## Common Pitfalls

### ❌ Don't use `cmd` for Python functions
```toml
# Wrong - loses access to package modules
update-items = { cmd = "python -m bpsr_labs.cli update-items" }
```

### ❌ Don't use `script` for external tools
```toml
# Wrong - unnecessary Python overhead
init-submodules = { script = "subprocess.run(['git', 'submodule', 'update', '--init', '--recursive'])" }
```

### ✅ Use the right type for the job
```toml
# Correct - direct access to package modules
update-items = { script = "bpsr_labs.cli:update_items" }

# Correct - direct external command execution
init-submodules = { cmd = "git submodule update --init --recursive" }
```

## Maintenance

- **Review tasks regularly** to ensure they're using the appropriate type
- **Document complex tasks** with inline comments
- **Test tasks individually** before adding to sequences
- **Keep help text up to date** as functionality changes

## References

- [Poe the Poet Documentation](https://poethepoet.natn.io/)
- [Poe Task Types](https://poethepoet.natn.io/docs/task_types/)
- [Poetry Scripts Migration](https://poethepoet.natn.io/docs/poetry_scripts/)
