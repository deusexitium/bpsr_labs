# Documentation Parity

## Purpose

Automatically analyze and enhance Python code documentation to achieve industry-standard coverage and quality, following 2025 best practices from Google, Microsoft, and the Python community. This command brings your codebase to documentation parity by adding missing docstrings, type hints, and effective inline comments while maintaining non-noisy, informative documentation standards.

## When to use

- After implementing new features
- During code review preparation  
- When onboarding new team members
- Quarterly documentation audits
- Before major releases
- When refactoring complex modules

## Coverage Standards (2025 Industry Best Practices)

### Documentation Requirements by Category

**Public API (100% Required)**
- All public modules (`__init__.py` files)
- All public classes and their methods
- All public functions and methods
- All public constants and module-level variables
- All public exceptions

**Complex Internal Logic (70-80% Required)**
- Functions with >15 lines of code
- Functions with >2 conditional branches
- Classes with complex state management
- Non-trivial algorithms and business logic
- Functions with side effects or external dependencies
- State machines and complex control flow

**Private Helpers (30-40% Required)**
- Document when behavior is non-obvious
- Document when there are side effects
- Document complex parameter validation
- Document when behavior differs from naming
- Document workarounds and temporary fixes

**Type Annotations (100% Required)**
- All function parameters and return types
- Class attributes with complex types
- Module-level variables with non-obvious types
- Generic type parameters
- Union types and Optional types

## Enhancement Rules

### Google-Style Docstrings Format

**Functions:**
```python
def function_name(param1: type1, param2: type2) -> return_type:
    """Brief one-line summary ending with period.
    
    Optional extended description providing more context about what
    the function does, when to use it, and any important behavior.
    This section can span multiple lines and should explain the
    function's purpose, usage patterns, and any important details.
    
    Args:
        param1: Description of param1, including any constraints or
            special behavior. Can span multiple lines if needed.
        param2: Description of param2.
    
    Returns:
        Description of return value, including type and any special
        conditions or constraints.
    
    Raises:
        ValueError: When param1 is invalid or out of range.
        RuntimeError: When the operation cannot be completed.
    
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        "test_42"
    """
```

**Classes:**
```python
class ClassName:
    """Brief description of the class.
    
    Extended description of the class purpose, behavior, and usage.
    Include information about the class's role in the system and
    any important design decisions.
    
    Attributes:
        attr1: Description of attr1.
        attr2: Description of attr2.
    
    Example:
        >>> obj = ClassName("value")
        >>> obj.method()
    """
```

**Modules:**
```python
"""Module-level docstring.

Brief description of the module's purpose and functionality.
This should explain what the module does, its main components,
and how it fits into the larger system.

Example:
    Basic usage of the module:
    >>> from module import main_function
    >>> result = main_function()
"""
```

### Inline Comments Guidelines

**DO Comment:**
- **WHY over WHAT**: Explain reasoning and intent, not obvious code
- **Complex algorithms**: Break down non-trivial logic step by step
- **Business rules**: Document domain-specific constraints and requirements
- **Workarounds**: Explain temporary fixes and why they exist
- **Magic numbers**: Explain non-obvious constants and their significance
- **Performance considerations**: Document why certain approaches were chosen
- **Edge cases**: Explain handling of unusual conditions
- **State changes**: Document when and why state is modified

**DON'T Comment:**
- Obvious variable assignments (`x = 5  # assign 5 to x`)
- Simple loops without complexity (`for item in items:`)
- Self-explanatory code (`return True`)
- Restating the code in English
- Comments that will become outdated quickly
- **Temporary comments**: Debug statements, work-in-progress markers, or temporary notes

**Good Comment Examples:**
```python
# Use binary search for O(log n) lookup in sorted data
# This is critical for performance with large datasets
index = bisect.bisect_left(sorted_list, target)

# Skip validation for internal calls to avoid double-checking
# External API calls are validated separately
if not self._is_internal_call():
    self._validate_input(data)

# Workaround for protobuf serialization bug in v3.19.0
# TODO: Remove when upgrading to v3.20.0+
if hasattr(message, '_cached_byte_size_dirty'):
    message._cached_byte_size_dirty = True
```

**Bad Comment Examples:**
```python
# Increment counter
counter += 1

# Loop through items
for item in items:
    # Process item
    process(item)

# Return the result
return result

# TODO: Fix this later
# FIXME: This is broken
# DEBUG: Remove this
# TEMP: Temporary fix
print("DEBUG: Value is", value)  # Debug statement
```

## Quality Checklist

### Docstring Quality
- [ ] Brief summary is clear and concise (one line)
- [ ] Extended description provides useful context
- [ ] All parameters documented with types and descriptions
- [ ] Return value documented with type and conditions
- [ ] All exceptions documented with conditions
- [ ] Examples provided for complex functions
- [ ] Consistent formatting throughout codebase
- [ ] No spelling or grammar errors

### Type Annotation Quality
- [ ] All function signatures have complete type hints
- [ ] Complex return types properly specified
- [ ] Generic types used where appropriate
- [ ] Union types clearly documented
- [ ] Type hints match actual behavior
- [ ] No `Any` types without justification

### Inline Comment Quality
- [ ] Comments explain WHY, not WHAT
- [ ] Complex logic is broken down clearly
- [ ] Business rules are documented
- [ ] Workarounds are explained
- [ ] No redundant or obvious comments
- [ ] Comments are up-to-date with code
- [ ] Consistent style and tone
- [ ] **No temporary comments remain**: No TODO, FIXME, DEBUG, TEMP, or work-in-progress markers

### Coverage Verification
- [ ] All public APIs documented
- [ ] Complex internal functions documented
- [ ] Non-obvious private functions documented
- [ ] Module docstrings present
- [ ] Type hints complete
- [ ] No undocumented breaking changes

## Notes to the Agent

### Execution Strategy

**Phase 1: Analysis**
1. Use `codebase_search` to find all Python files in the project
2. Use `grep` to identify functions, classes, and modules without docstrings
3. Use `grep` to find functions missing type hints
4. Analyze code complexity to identify areas needing inline comments
5. Generate a comprehensive coverage report

**Phase 2: Enhancement**
1. Start with module-level docstrings (`__init__.py` files)
2. Add docstrings to all public classes and functions
3. Add docstrings to complex internal functions (>15 LOC or >2 branches)
4. Add type hints to all function signatures
5. Add inline comments for complex algorithms and business logic
6. **Remove temporary comments**: Clean up any temporary comments, debug prints, or work-in-progress markers
7. Preserve existing good documentation

**Phase 3: Verification**
1. Re-analyze the codebase to verify coverage
2. Check docstring format consistency
3. Verify type hint completeness
4. Ensure inline comments are non-redundant
5. **Verify no temporary comments remain**: Scan for and remove any remaining temporary comments, debug statements, or work-in-progress markers
6. Generate final coverage report

### Tools to Use

- `codebase_search`: Find Python files and analyze structure
- `grep`: Search for specific patterns (docstrings, type hints, etc.)
- `read_file`: Examine individual files for detailed analysis
- `search_replace`: Make precise documentation additions
- `MultiEdit`: Make multiple related changes efficiently

### Temporary Comment Detection Patterns

Use these grep patterns to identify and remove temporary comments:
- `grep -r "# TODO"` - Find TODO comments
- `grep -r "# FIXME"` - Find FIXME comments  
- `grep -r "# DEBUG"` - Find DEBUG comments
- `grep -r "# TEMP"` - Find TEMP comments
- `grep -r "print.*DEBUG"` - Find debug print statements
- `grep -r "# XXX"` - Find XXX markers
- `grep -r "# HACK"` - Find HACK comments

### Temporary Comment Cleanup Process

1. **Scan for temporary comments** using the patterns above
2. **Evaluate each comment**:
   - If it's a legitimate TODO for future work, convert to proper documentation
   - If it's a temporary debug statement, remove it
   - If it's a work-in-progress marker, complete the work or remove the marker
   - If it's a temporary fix, either implement properly or document as a known limitation
3. **Replace temporary comments** with proper documentation or remove them entirely
4. **Verify no temporary comments remain** in the final codebase

### Quality Standards

- Follow PEP 257 docstring conventions
- Use Google style (not NumPy or Sphinx)
- Keep comments concise and informative
- Maintain consistent formatting
- Preserve existing good documentation
- Focus on WHY over WHAT in comments
- Ensure all public APIs are documented
- Add type hints to all function signatures

### Iteration Strategy

1. **Analyze first**: Always start with comprehensive analysis
2. **Prioritize public API**: Focus on public interfaces first
3. **Batch similar changes**: Group related documentation additions
4. **Verify incrementally**: Check quality after each major change
5. **Preserve existing work**: Don't modify well-documented code unnecessarily

### Success Criteria

- All public APIs have complete docstrings
- All functions have type hints
- Complex internal logic is documented
- Inline comments are informative and non-redundant
- Documentation follows Google style consistently
- Coverage report shows >90% for public API, >70% for complex internal logic
- **No temporary comments remain**: All TODO, FIXME, DEBUG, TEMP, and work-in-progress markers removed
- No breaking changes to existing functionality
