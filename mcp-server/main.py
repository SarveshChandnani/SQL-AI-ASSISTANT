# # from langchain_core.tools import tool
# import sqlite3
# import os
# import json
# from datetime import datetime
# from fastmcp import FastMCP  
# from dotenv import load_dotenv

# load_dotenv()

# DB_PATH = os.getenv("DB_PATH")


# mcp = FastMCP(name = "SQL_QUERY_MCP")

# @mcp.tool
# def get_tables() -> str:
#     """
#     Returns all available tables with descriptions.
#     Use this FIRST to understand database structure.
#     """

#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     # db_path = os.path.join(current_dir, "..", "data", "customers_orders.db")
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT table_name, table_description
#         FROM table_metadata
#     """)

#     rows = cursor.fetchall()
#     conn.close()

#     if not rows:
#         return "No table metadata found."

#     result = [f"{table_name}: {table_desc}" for table_name, table_desc in rows]

#     return "\n".join(result)


# @mcp.tool
# def get_schema(tables: str) -> str:
#     """
#     Input: comma-separated table names
#     Returns column-wise descriptions of those tables.
#     uset this to check if column has some specific distinct values to be used in the query.
#     """
    
#     table_list = [t.strip() for t in tables.split(",")]

#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     # db_path = os.path.join(current_dir, "..", "data", "customers_orders.db")

#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     schema = ""
#     for table in table_list:
#         cursor.execute("""
#             SELECT table_column_wise_description
#             FROM table_metadata
#             WHERE table_name = ?
#         """, (table,))
        
#         row = cursor.fetchone()

#         if not row:
#             schema += f"\nTable: {table} (No metadata found)\n"
#             continue

#         column_desc_json = row[0]

#         schema += f"\nTable: {table}\n"
#         schema += "Columns:\n"

#         try:
#             column_desc = json.loads(column_desc_json)
#             for col, desc in column_desc.items():
#                 schema += f"- {col}: {desc}\n"
#         except Exception:
#             schema += "- Column descriptions unavailable\n"

#     conn.close()
#     return schema

# def is_safe_query(query: str) -> bool:
#     query = query.strip().lower()

#     # ❌ multiple statements
#     if ";" in query.strip()[:-1]:
#         return False

#     if not query.startswith("select"):
#         return False

#     forbidden = [
#         "insert", "update", "delete", "drop",
#         "alter", "truncate", "create", "replace"
#     ]

#     return not any(word in query for word in forbidden)

# @mcp.tool
# def execute_sql(query: str) -> str:
#     """
#     Executes SQL query and returns results.
#     """

#     if not is_safe_query(query):
#         return "Only read-only queries are allowed."

#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     # db_path = os.path.join(current_dir, "..", "data", "customers_orders.db")
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     try:
#         cursor.execute(query)
#         rows = cursor.fetchall()
#         return str(rows)
#     except Exception as e:
#         return f"ERROR: {str(e)}"
#     finally:
#         conn.close()

# @mcp.tool
# def calculator(num1: float, num2: float, operator: str) -> str:
#     """Perform arithmetic operation on two numbers."""
#     if operator == "+":
#         return str(num1 + num2)
#     elif operator == "-":
#         return str(num1 - num2)
#     elif operator == "*":
#         return str(num1 * num2)
#     elif operator == "/":
#         return str(num1 / num2) if num2 != 0 else "Error: Division by zero"
#     else:
#         return "Error: Unsupported operator"


# @mcp.tool
# def get_distinct_values(table: str, column: str) -> str:
#     """
#     If you are a little bit confused about the schema or want to validate your understanding, use this tool to get distinct values of a column.
#     """
#     import sqlite3

#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     # db_path = os.path.join(current_dir, "..", "data", "customers_orders.db")
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute(f"SELECT DISTINCT {column} FROM {table} LIMIT 20")
#     rows = cursor.fetchall()

#     conn.close()

#     return str(rows)

# @mcp.tool
# def get_current_datetime() -> str:
#     """
#     Returns the current date and time in ISO format.
#     Useful for time-based queries like 'today', 'last 7 days', etc.
#     """
#     now = datetime.now()

#     return now.strftime("%Y-%m-%d %H:%M:%S")


# if __name__ == "__main__":
#     mcp.run()


import os
import json
from datetime import datetime
import psycopg2
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

mcp = FastMCP(name="SQL_QUERY_MCP")


# 🔹 Connection helper
def get_connection():
    return psycopg2.connect(DB_URL)


@mcp.tool
def get_tables() -> str:
    """
    Returns all available tables with descriptions.
    Use this FIRST to understand database structure.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name, table_description
        FROM table_metadata
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No table metadata found."

    return "\n".join([f"{r[0]}: {r[1]}" for r in rows])


@mcp.tool
def get_schema(tables: str) -> str:
    """
    Input: comma-separated table names
    Returns column-wise descriptions of those tables.
    """
    table_list = [t.strip() for t in tables.split(",")]

    conn = get_connection()
    cursor = conn.cursor()

    schema = ""

    for table in table_list:
        cursor.execute("""
            SELECT table_column_wise_description
            FROM table_metadata
            WHERE table_name = %s
        """, (table,))

        row = cursor.fetchone()

        if not row:
            schema += f"\nTable: {table} (No metadata found)\n"
            continue

        schema += f"\nTable: {table}\nColumns:\n"

        try:
            column_desc = json.loads(row[0])
            for col, desc in column_desc.items():
                schema += f"- {col}: {desc}\n"
        except Exception:
            schema += "- Column descriptions unavailable\n"

    conn.close()
    return schema


def is_safe_query(query: str) -> bool:
    query = query.strip().lower()

    if ";" in query.strip()[:-1]:
        return False

    if not query.startswith("select"):
        return False

    forbidden = [
        "insert", "update", "delete", "drop",
        "alter", "truncate", "create", "replace"
    ]

    return not any(word in query for word in forbidden)


@mcp.tool
def execute_sql(query: str) -> str:
    """
    Executes SQL query and returns results.
    """
    if not is_safe_query(query):
        return "Only read-only queries are allowed."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return str(rows)
    except Exception as e:
        return f"ERROR: {str(e)}"
    finally:
        conn.close()


@mcp.tool
def calculator(num1: float, num2: float, operator: str) -> str:
    if operator == "+":
        return str(num1 + num2)
    elif operator == "-":
        return str(num1 - num2)
    elif operator == "*":
        return str(num1 * num2)
    elif operator == "/":
        return str(num1 / num2) if num2 != 0 else "Error: Division by zero"
    return "Error: Unsupported operator"


@mcp.tool
def get_distinct_values(table: str, column: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT DISTINCT {column} FROM {table} LIMIT 20")
        rows = cursor.fetchall()
        return str(rows)
    except Exception as e:
        return f"ERROR: {str(e)}"
    finally:
        conn.close()


@mcp.tool
def get_current_datetime() -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    mcp.run()