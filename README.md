# Shift-Reduce Parser (Python)

This project implements a **Shift-Reduce Parser** in Python for context-free grammars.  
It reads grammar rules from a file, parses an input string step-by-step, and displays:

- Shift / Reduce actions
- Conflict detection (Shift-Reduce, Reduce-Reduce)
- Parsing table (formatted)
- Final parsing result (Accepted / Rejected)
- Parse Tree (ASCII visualization)

---

## 📂 Project Structure

```

.
├── code.py        # Main shift-reduce parser implementation
├── grammar.txt    # Grammar rules file
└── README.md

````

---

## ⚙️ Requirements

- Python **3.8 or higher**
- `tabulate` library (for formatted parsing table output)

---

## 🐍 Setting Up a Python Virtual Environment (Recommended)

It is **strongly recommended** to run this project inside a virtual environment.

### 1️⃣ Create Virtual Environment

```bash
python -m venv venv
````

### 2️⃣ Activate Virtual Environment

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows (PowerShell)**

```powershell
venv\Scripts\Activate.ps1
```

---

### 3️⃣ Install Dependencies

```bash
pip install tabulate
```

---

## 📘 Grammar File Format

Grammar rules must follow these rules:

1. Use `->` to separate **LHS** and **RHS**
2. Separate symbols with **spaces**
3. Use `|` for multiple productions
4. The **first grammar rule** defines the start symbol

### Example (`grammar.txt`)

```
E -> E + T | T
T -> id
```

---

## ▶️ How to Run the Parser

```bash
python code.py grammar.txt
```

---

## ⌨️ Input Rules

After starting the program:

* Enter tokens **space-separated**
* Do **NOT** add `$` at the end (added automatically)
* Type `exit` to quit

### Example Input

```
id + id
```

---

## 📊 Output Details

The parser will display:

### ✔ Shift-Reduce Parsing Table

Includes:

* Step number
* Stack content
* Remaining input
* Action taken
* Grammar rule applied

### ✔ Parsing Status

* Accepted
* Rejected (Error / Conflict / Loop limit)

### ✔ Parse Tree

Displayed using ASCII tree structure.

Example:

```
└── E
    ├── E
    │   └── T
    │       └── id
    ├── +
    └── T
        └── id
```

---

## ⚠️ Conflict Handling

The parser automatically detects:

* **Shift-Reduce conflicts**
* **Reduce-Reduce conflicts**

Conflict resolution policy:

* Prefers **longest possible reduction**
* Shift-Reduce conflicts are resolved by **reducing**
* Reduce-Reduce conflicts cause rejection

---

## 🛡 Safety Features

* Loop limit of **100 steps**
* Input validation
* Grammar validation
* Graceful error handling

---

## 🧠 Educational Purpose

This project is designed for:

* Compiler Design courses
* Understanding bottom-up parsing
* Learning shift-reduce mechanics
* Visualizing parse trees

---

## 📌 Notes

* Grammar symbols must be **space-separated**
* Epsilon productions are supported internally
* The parser is interactive and can parse multiple inputs per run

---

## 🧑‍💻 Author

**Sheheryar Salman**
