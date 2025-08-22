# 📜 Code of Conduct
Welcome to this personal project! While this repository is **not open for external contributions**, maintaining consistency and professionalism environment still matters, hence the C_O_C.md.
  
---
## 🧭 Project Ethos

This project is built with:
- 🧠 **Curiosity** — Exploring new tools and technologies (Flutter + FastAPI).
- 🛠 **Structure** — Following clean coding practices and maintainable architecture.
- 💸 **Frugality** — 100% designed for **free-tier infrastructure** (e.g., AWS free credits, Supabase, GitHub Actions, etc.).

  
---
## Coding Conventions
To ensure code clarity and self-discipline, the following rules apply across the stack (both Flutter & FastAPI):

### 🐍 Python (FastAPI Backend)
- ✅ All `import` statements are grouped at the **very top** of each file.

- ✅ **3 blank lines** between imports and the first function/class.

- ✅ **2 blank lines** between function definitions.

- ✅ Functions over ~10 lines or with conditional logic must include **docstrings** (`"""Explains purpose, args, returns"""`).

- ✅ Any code marked for later refactoring/review uses clear **`# NOTE:` comments**.

- ✅ Stick to [PEP8](https://peps.python.org/pep-0008/) wherever reasonable — with some personal style.

### Dart (Flutter Frontend)
- ✅ Use meaningful widget names — no `MyWidget1`, `MyWidget2` stuff.

- ✅ Use `const` constructors where possible.

- ✅ Always group `import`s properly: Dart first, Flutter packages next, then third-party libs.

- ✅ UI code must use **consistent spacing and padding**, with responsiveness in mind.

- ✅ Maintain modular widget/component structure (`/widgets`, `/screens`, `/models`, etc.).

- ✅ Use `///` for documentation-style comments where needed.

### Comments & TODOs

```python

# Use clear TODO comments for future work

# [ ] create_user(user_data: UserCreate) -> User

# - Hash password before storing

# - Ensure unique username and email


# Comment out old code that needs cleanup

''' -> commented out code to be removed later after schema creation

class UserRole(str, enum.Enum):

superadmin = "admin"

'''

```

## 🎨 Naming Conventions
### Variables & Functions

```python

# snake_case for variables and functions

user_id = 123

def get_user_by_id(user_id: int) -> Optional[User]:

pass


#  UPPER_CASE for constants

JWT_SECRET_KEY = "your-secret-key"

```
  
### Classes & Files

```python

# ✅ PascalCase for classes

class UserSubscription(BaseModel):

pass


# ✅ snake_case for files

user_subscription.py

``` 
### Database

```python
# ✅ snake_case for table names

__tablename__ = "user_subscriptions"
  

# ✅ Clear column names

user_id = Column(Integer, ForeignKey("users.id"))

subscription_plan_id = Column(Integer, ForeignKey("subscription_plans.id"))

```

### 🚫 Whats being avoided

- ❌ **No ambiguous numbers** — Using constants or config values
- ❌ **No hardcoded secrets** — Everything in `.env` files
- ❌ **No inconsistent formatting** — Trying to stick to PEP8-ish style

---
## 🚫 Contribution Policy

This is a **closed-source solo project**, external contributions are **not accepted**.
That said:
- You are welcome to explore the code.
- You are free to fork it, although this is novice codebase.

---
## ✉️ Contact
If you have suggestions or any queries, feel free to reach out to [me](mailto:myshaaa31ns@gmail.com)
