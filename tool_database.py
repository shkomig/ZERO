"""
Database Tool for Zero Agent
=============================
Execute SQL queries safely with validation

Supports: SQLite, PostgreSQL, MySQL
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re

try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


class DatabaseTool:
    """
    Safe SQL database interface for Zero Agent
    """
    
    # Dangerous SQL keywords (for safety)
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
        'INSERT', 'UPDATE', 'GRANT', 'REVOKE'
    ]
    
    def __init__(self, 
                 db_type: str = "sqlite",
                 db_path: Optional[Path] = None,
                 host: str = "localhost",
                 port: int = 5432,
                 database: str = "",
                 user: str = "",
                 password: str = "",
                 allow_write: bool = False):
        """
        Initialize database tool
        
        Args:
            db_type: Database type (sqlite, postgres, mysql)
            db_path: Path to SQLite database
            host: Database host
            port: Database port
            database: Database name
            user: Username
            password: Password
            allow_write: Allow INSERT/UPDATE/DELETE operations
        """
        self.db_type = db_type.lower()
        self.db_path = db_path
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.allow_write = allow_write
        self.connection = None
        
        self._connect()
    
    def _connect(self):
        """
        Connect to database
        """
        try:
            if self.db_type == "sqlite":
                if not self.db_path:
                    self.db_path = Path("workspace/data.db")
                self.db_path.parent.mkdir(exist_ok=True)
                self.connection = sqlite3.connect(str(self.db_path))
                
            elif self.db_type == "postgres":
                if not POSTGRES_AVAILABLE:
                    raise ImportError("Install: pip install psycopg2-binary")
                self.connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
                
            elif self.db_type == "mysql":
                if not MYSQL_AVAILABLE:
                    raise ImportError("Install: pip install mysql-connector-python")
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
                
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")
    
    def is_safe_query(self, query: str) -> Tuple[bool, str]:
        """
        Check if query is safe to execute
        
        Returns:
            (is_safe, reason)
        """
        query_upper = query.upper()
        
        # Check for dangerous keywords
        if not self.allow_write:
            for keyword in self.DANGEROUS_KEYWORDS:
                if keyword in query_upper:
                    return False, f"Write operations not allowed. Found: {keyword}"
        
        # Check for multiple statements (SQL injection protection)
        if ';' in query and query.count(';') > 1:
            return False, "Multiple statements not allowed"
        
        # Check for comments (potential injection)
        if '--' in query or '/*' in query:
            return False, "Comments not allowed in queries"
        
        return True, "Query is safe"
    
    def execute_query(self, 
                     query: str,
                     params: Optional[Tuple] = None) -> Dict[str, Any]:
        """
        Execute SQL query safely
        
        Args:
            query: SQL query
            params: Query parameters (for prepared statements)
            
        Returns:
            Query results
        """
        # Validate query
        is_safe, reason = self.is_safe_query(query)
        if not is_safe:
            return {
                'success': False,
                'error': f"Query rejected: {reason}",
                'rows': [],
                'columns': []
            }
        
        try:
            cursor = self.connection.cursor()
            
            # Execute query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get results for SELECT queries
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                return {
                    'success': True,
                    'rows': rows,
                    'columns': columns,
                    'row_count': len(rows)
                }
            else:
                # For INSERT/UPDATE/DELETE
                self.connection.commit()
                return {
                    'success': True,
                    'affected_rows': cursor.rowcount,
                    'rows': [],
                    'columns': []
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'rows': [],
                'columns': []
            }
        finally:
            if cursor:
                cursor.close()
    
    def query_to_dict(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute query and return results as list of dicts
        """
        result = self.execute_query(query)
        
        if not result['success']:
            return []
        
        rows = result.get('rows', [])
        columns = result.get('columns', [])
        
        return [
            dict(zip(columns, row))
            for row in rows
        ]
    
    def get_tables(self) -> List[str]:
        """
        Get list of tables in database
        """
        try:
            if self.db_type == "sqlite":
                query = "SELECT name FROM sqlite_master WHERE type='table'"
            elif self.db_type == "postgres":
                query = "SELECT tablename FROM pg_tables WHERE schemaname='public'"
            elif self.db_type == "mysql":
                query = "SHOW TABLES"
            else:
                return []
            
            result = self.execute_query(query)
            if result['success']:
                return [row[0] for row in result['rows']]
            return []
            
        except Exception as e:
            print(f"Error getting tables: {str(e)}")
            return []
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """
        Get schema for a table
        """
        try:
            if self.db_type == "sqlite":
                query = f"PRAGMA table_info({table_name})"
                result = self.execute_query(query)
                if result['success']:
                    return [
                        {
                            'column': row[1],
                            'type': row[2],
                            'nullable': 'YES' if row[3] == 0 else 'NO',
                            'primary_key': 'YES' if row[5] == 1 else 'NO'
                        }
                        for row in result['rows']
                    ]
            elif self.db_type == "postgres":
                query = f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                """
                result = self.execute_query(query)
                if result['success']:
                    return [
                        {
                            'column': row[0],
                            'type': row[1],
                            'nullable': row[2]
                        }
                        for row in result['rows']
                    ]
            
            return []
            
        except Exception as e:
            print(f"Error getting schema: {str(e)}")
            return []
    
    def count_rows(self, table_name: str) -> int:
        """
        Count rows in table
        """
        try:
            query = f"SELECT COUNT(*) FROM {table_name}"
            result = self.execute_query(query)
            if result['success'] and result['rows']:
                return result['rows'][0][0]
            return 0
        except:
            return 0
    
    def sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get sample data from table
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.query_to_dict(query)
    
    def close(self):
        """
        Close database connection
        """
        if self.connection:
            self.connection.close()


# Convenience functions for Zero Agent

def db_query(query: str, db_path: str = "workspace/data.db") -> str:
    """
    Execute SQL query (for Zero Agent)
    """
    try:
        tool = DatabaseTool(db_path=Path(db_path))
        result = tool.execute_query(query)
        
        if not result['success']:
            return f"❌ Error: {result['error']}"
        
        if result.get('rows'):
            # Format results
            output = f"✓ Query successful ({result['row_count']} rows)\n\n"
            columns = result['columns']
            rows = result['rows']
            
            # Header
            output += " | ".join(columns) + "\n"
            output += "-" * (len(columns) * 15) + "\n"
            
            # Rows (limit to 10 for display)
            for row in rows[:10]:
                output += " | ".join(str(val) for val in row) + "\n"
            
            if len(rows) > 10:
                output += f"\n... and {len(rows) - 10} more rows"
            
            return output
        else:
            return f"✓ Query executed. Affected rows: {result.get('affected_rows', 0)}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"


def db_tables(db_path: str = "workspace/data.db") -> str:
    """
    List database tables (for Zero Agent)
    """
    try:
        tool = DatabaseTool(db_path=Path(db_path))
        tables = tool.get_tables()
        
        if not tables:
            return "No tables found in database"
        
        output = f"📊 Database tables ({len(tables)}):\n\n"
        for i, table in enumerate(tables, 1):
            count = tool.count_rows(table)
            output += f"{i}. {table} ({count} rows)\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


def db_schema(table_name: str, db_path: str = "workspace/data.db") -> str:
    """
    Show table schema (for Zero Agent)
    """
    try:
        tool = DatabaseTool(db_path=Path(db_path))
        schema = tool.get_table_schema(table_name)
        
        if not schema:
            return f"Table '{table_name}' not found"
        
        output = f"📋 Schema for table '{table_name}':\n\n"
        for col in schema:
            output += f"• {col['column']}: {col['type']}"
            if col.get('nullable') == 'NO':
                output += " (NOT NULL)"
            if col.get('primary_key') == 'YES':
                output += " (PRIMARY KEY)"
            output += "\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Test
if __name__ == "__main__":
    print("Database Tool Test")
    print("="*70)
    
    try:
        # Create test database
        tool = DatabaseTool(db_path=Path("test.db"), allow_write=True)
        print("✓ Connected to test database")
        
        # Create test table
        tool.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created test table")
        
        # Insert test data
        tool.execute_query(
            "INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)",
            (1, "John Doe", "john@example.com")
        )
        tool.execute_query(
            "INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)",
            (2, "Jane Smith", "jane@example.com")
        )
        print("✓ Inserted test data")
        
        # Query data
        print("\n📊 Query results:")
        result = tool.query_to_dict("SELECT * FROM users")
        for row in result:
            print(f"   {row}")
        
        # Get tables
        print("\n📋 Tables:")
        tables = tool.get_tables()
        for table in tables:
            print(f"   • {table}")
        
        # Get schema
        print("\n📐 Schema for 'users':")
        schema = tool.get_table_schema('users')
        for col in schema:
            print(f"   {col}")
        
        tool.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
