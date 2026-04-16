"""
Seed script — creates the demo employees database.

Run:
    python scripts/seed_demo_db.py

Creates: data/demo/employees.db
Populates with 20 realistic-looking demo employees
across 5 departments with varied salary ranges.
"""

import os
import sqlite3
import random

DB_PATH = os.path.join("data", "demo", "employees.db")

# Realistic demo data — all fictional
DEPARTMENTS = ["Engineering", "Marketing", "Finance", "Human Resources", "Operations"]

EMPLOYEES = [
    # (name, email, phone, department, role, salary, performance_rating)
    ("Arjun Mehta",       "arjun.mehta@acmecorp.com",       "555-0101", "Engineering",      "Senior Software Engineer",  125000, "Exceeds Expectations"),
    ("Priya Sharma",      "priya.sharma@acmecorp.com",      "555-0102", "Engineering",      "Staff Engineer",            155000, "Outstanding"),
    ("Rahul Verma",       "rahul.verma@acmecorp.com",       "555-0103", "Engineering",      "Junior Developer",           72000, "Meets Expectations"),
    ("Sneha Patel",       "sneha.patel@acmecorp.com",       "555-0104", "Engineering",      "DevOps Lead",              140000, "Exceeds Expectations"),
    ("Ananya Gupta",      "ananya.gupta@acmecorp.com",      "555-0105", "Marketing",        "Marketing Director",        135000, "Outstanding"),
    ("Vikram Singh",      "vikram.singh@acmecorp.com",      "555-0106", "Marketing",        "Content Strategist",         85000, "Meets Expectations"),
    ("Neha Reddy",        "neha.reddy@acmecorp.com",        "555-0107", "Marketing",        "Social Media Manager",       78000, "Exceeds Expectations"),
    ("Karan Joshi",       "karan.joshi@acmecorp.com",       "555-0108", "Marketing",        "SEO Analyst",                68000, "Meets Expectations"),
    ("Divya Nair",        "divya.nair@acmecorp.com",        "555-0109", "Finance",          "CFO",                       210000, "Outstanding"),
    ("Amit Kulkarni",     "amit.kulkarni@acmecorp.com",     "555-0110", "Finance",          "Financial Analyst",          92000, "Exceeds Expectations"),
    ("Ritu Agarwal",      "ritu.agarwal@acmecorp.com",      "555-0111", "Finance",          "Accounts Payable Clerk",     55000, "Meets Expectations"),
    ("Suresh Iyer",       "suresh.iyer@acmecorp.com",       "555-0112", "Finance",          "Tax Specialist",            105000, "Exceeds Expectations"),
    ("Meera Deshmukh",    "meera.deshmukh@acmecorp.com",    "555-0113", "Human Resources",  "HR Director",               128000, "Outstanding"),
    ("Rohan Chandra",     "rohan.chandra@acmecorp.com",     "555-0114", "Human Resources",  "Recruiter",                  70000, "Meets Expectations"),
    ("Pooja Mishra",      "pooja.mishra@acmecorp.com",      "555-0115", "Human Resources",  "Benefits Coordinator",       62000, "Exceeds Expectations"),
    ("Sanjay Bhatt",      "sanjay.bhatt@acmecorp.com",      "555-0116", "Human Resources",  "Training Manager",           88000, "Meets Expectations"),
    ("Kavita Rao",        "kavita.rao@acmecorp.com",        "555-0117", "Operations",       "VP Operations",             175000, "Outstanding"),
    ("Deepak Tiwari",     "deepak.tiwari@acmecorp.com",     "555-0118", "Operations",       "Supply Chain Manager",      102000, "Exceeds Expectations"),
    ("Lakshmi Subramanian", "lakshmi.sub@acmecorp.com",     "555-0119", "Operations",       "Logistics Coordinator",      65000, "Meets Expectations"),
    ("Nikhil Saxena",     "nikhil.saxena@acmecorp.com",     "555-0120", "Operations",       "Quality Assurance Lead",     95000, "Exceeds Expectations"),
]


def seed():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Remove existing DB to start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL,
            salary INTEGER NOT NULL,
            performance_rating TEXT NOT NULL,
            ssn TEXT NOT NULL,
            hire_date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            head_count INTEGER NOT NULL DEFAULT 0,
            budget INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Insert employees
    years = list(range(2018, 2026))
    months = list(range(1, 13))
    for name, email, phone, dept, role, salary, rating in EMPLOYEES:
        # Generate fake SSN (clearly fake pattern)
        ssn = f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"
        hire_date = f"{random.choice(years)}-{random.choice(months):02d}-{random.randint(1,28):02d}"
        cursor.execute(
            "INSERT INTO employees (name, email, phone, department, role, salary, performance_rating, ssn, hire_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, email, phone, dept, role, salary, rating, ssn, hire_date),
        )

    # Insert department summaries
    dept_data = {}
    for _, _, _, dept, _, salary, _ in EMPLOYEES:
        if dept not in dept_data:
            dept_data[dept] = {"count": 0, "total_salary": 0}
        dept_data[dept]["count"] += 1
        dept_data[dept]["total_salary"] += salary

    for dept_name, data in dept_data.items():
        cursor.execute(
            "INSERT INTO departments (name, head_count, budget) VALUES (?, ?, ?)",
            (dept_name, data["count"], data["total_salary"]),
        )

    conn.commit()
    conn.close()

    print(f"[OK] Demo database created: {DB_PATH}")
    print(f"     {len(EMPLOYEES)} employees across {len(DEPARTMENTS)} departments")


if __name__ == "__main__":
    seed()
