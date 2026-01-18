# Git Commit Guidelines

## Commit Message Structure

```
<prefix>: <short description>
```

- `<prefix>` : type of commit  
- `<short description>` : concise description of **one action**.  
- Always use **present tense**, not past.

---

## Common Prefixes

| Prefix    | Usage                                                                 |
|-----------|-----------------------------------------------------------------------|
| `feat`    | New feature or enhancement                                           |
| `fix`     | Bug fix                                                               |
| `refactor`| Code refactoring without changing behavior                           |
| `docs`    | Documentation changes                                                |
| `test`    | Adding or fixing tests                                               |
| `chore`   | Maintenance tasks, dependency updates, formatting, config changes    |

---

## Naming Conventions

- Be **descriptive but concise**: `feat: add Rotation class to Transform`  
- Use **imperative mood**: `fix: handle BoxCollider rotation properly`  
- Separate **multiple concepts** into multiple commits  
- Avoid vague messages like `update`, `fix stuff`, `changes`  

---

## Examples

```
feat: implement forward, right, left, behind in Transform
fix: correct get_closest_point_on_box calculation
refactor: simplify Vector2D.from_direction method
docs: add numpy-style docstrings to Rotation class
test: add parameterized tests for Transform.rotate
chore: update dependencies and format code
```

