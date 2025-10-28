# TODO Comment Standards

## Overview

This document defines the standards for TODO, FIXME, HACK, and similar comments in the BPSR Labs codebase, based on 2025 industry best practices from Google, Microsoft, Amazon, and other major tech companies.

## Why TODO Comments Are Valuable

Contrary to common misconceptions, TODO comments are **actively recommended** by major tech companies when properly formatted. They serve as:

- **Technical debt tracking**: Visible markers of work that needs to be done
- **Knowledge transfer**: Context for future developers
- **Issue integration**: Links between code and project management
- **Accountability**: Clear ownership of tasks

## Standard Format

### Required Format

```python
# TODO(username, YYYY-MM-DD): Description. Issue #123
# FIXME(username, YYYY-MM-DD): Description. See Issue #456
# HACK(username, YYYY-MM-DD): Description. Related to Issue #789
# REVIEW(username, YYYY-MM-DD): Description. Issue #101
```

### Required Elements

1. **Comment Type**: TODO, FIXME, HACK, REVIEW, etc.
2. **Username**: GitHub username or author identifier
3. **Date**: When the comment was added (YYYY-MM-DD format)
4. **Description**: Clear explanation of what needs to be done
5. **Issue Reference**: Link to GitHub issue, Jira ticket, or similar

### Examples

**Good Examples:**
```python
# TODO(john.doe, 2025-01-28): Refactor this function for better performance. Issue #123
def slow_function():
    pass

# FIXME(jane.smith, 2025-01-28): Memory leak in batch processing. See Issue #456
def process_batch(items):
    pass

# HACK(mike.wilson, 2025-01-28): Temporary workaround for protobuf bug. Issue #789
if hasattr(message, '_cached_byte_size_dirty'):
    message._cached_byte_size_dirty = True
```

**Bad Examples:**
```python
# TODO: Fix this later  # Missing author, date, issue
# FIXME: This is broken  # No context
# DEBUG: Remove this  # Temporary debug comment
# TEMP: Temporary fix  # Temporary marker
```

## Comment Types

### TODO
- **Purpose**: Planned features or tasks pending implementation
- **When to use**: When you know something needs to be done but can't do it now
- **Example**: `# TODO(username, date): Add error handling for edge case. Issue #123`

### FIXME
- **Purpose**: Known issues or bugs that require fixing
- **When to use**: When you've identified a problem that needs resolution
- **Example**: `# FIXME(username, date): Memory leak in this function. Issue #456`

### HACK
- **Purpose**: Temporary solutions or workarounds that are not ideal
- **When to use**: When you've implemented a suboptimal solution that should be revisited
- **Example**: `# HACK(username, date): Workaround for library bug. Issue #789`

### REVIEW
- **Purpose**: Code that needs further examination or validation
- **When to use**: When code needs peer review or additional testing
- **Example**: `# REVIEW(username, date): Algorithm needs performance review. Issue #101`

## Integration with Issue Tracking

### Creating GitHub Issues

1. **Create the issue first** in GitHub Issues
2. **Reference the issue** in your TODO comment
3. **Link back to code** in the issue description

### Issue Template

```markdown
## TODO: [Brief description]

**Location**: `src/file.py:line_number`
**Author**: @username
**Date**: YYYY-MM-DD

**Description**: [Detailed explanation]

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

**Priority**: [Low/Medium/High/Critical]
```

## Review Process

### During Code Reviews

1. **Check for proper format**: All TODOs should follow the standard
2. **Verify issue exists**: Ensure referenced issues are valid
3. **Assess priority**: Determine if TODOs should be addressed before merge
4. **Update if needed**: Fix formatting or create missing issues

### Regular Maintenance

1. **Monthly review**: Scan codebase for TODO comments
2. **Update stale TODOs**: Remove or update outdated comments
3. **Track progress**: Monitor issue resolution
4. **Clean up**: Remove completed TODOs

## Tools and Automation

### IDE Extensions

- **VS Code**: "TODO Tree" extension
- **PyCharm**: Built-in TODO support
- **Vim/Neovim**: Various TODO plugins

### Command Line Tools

```bash
# Find all TODO comments
grep -r "# TODO" src/

# Find poorly formatted TODOs (missing author/date)
grep -r "# TODO:" src/

# Find TODO comments by specific author
grep -r "# TODO(username" src/
```

### CI/CD Integration

Consider adding checks to your CI pipeline:
- Scan for poorly formatted TODOs
- Verify referenced issues exist
- Track TODO comment count over time

## Best Practices

### Do's

- ✅ Always include author, date, and issue reference
- ✅ Write clear, actionable descriptions
- ✅ Create corresponding GitHub issues
- ✅ Review and update regularly
- ✅ Remove completed TODOs promptly

### Don'ts

- ❌ Leave TODO comments without context
- ❌ Use TODOs for temporary debug statements
- ❌ Let TODOs accumulate indefinitely
- ❌ Create TODOs without creating issues
- ❌ Use vague descriptions like "fix this"

## Migration Guide

### Converting Existing TODOs

1. **Identify poorly formatted TODOs**:
   ```bash
   grep -r "# TODO:" src/
   grep -r "# FIXME:" src/
   ```

2. **For each TODO**:
   - Create a GitHub issue
   - Update the comment with proper format
   - Include issue reference

3. **Remove temporary comments**:
   ```bash
   grep -r "# DEBUG" src/
   grep -r "# TEMP" src/
   ```

### Example Migration

**Before:**
```python
# TODO: Fix this function
def broken_function():
    pass
```

**After:**
```python
# TODO(john.doe, 2025-01-28): Refactor function to handle edge cases. Issue #123
def broken_function():
    pass
```

## Conclusion

Properly formatted TODO comments are valuable tools for managing technical debt and maintaining code quality. By following these standards, we ensure that TODO comments serve their intended purpose and integrate well with our development workflow.

Remember: The goal is not to eliminate TODO comments, but to make them useful, trackable, and actionable.
