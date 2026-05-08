import os
import json
from datetime import datetime
import psycopg2
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

mcp = FastMCP(name="SQL_QUERY_MCP")


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
        SELECT table_name, table_description, table_column_wise_description
        FROM table_metadata
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No table metadata found."

    return "\n".join([f"{r[0]}: {r[1]}" for r in rows])


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