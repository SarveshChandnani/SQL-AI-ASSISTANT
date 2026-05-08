import os
import json
from datetime import datetime
import psycopg2
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

mcp = FastMCP(name="EXECUTE_SQL_MCP")


# 🔹 Connection helper
def get_connection():
    return psycopg2.connect(DB_URL)





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

if __name__ == "__main__":
    mcp.run()