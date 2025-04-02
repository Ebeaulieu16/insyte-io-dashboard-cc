#!/usr/bin/env python
"""
Script to display the current integrations in the database.
"""

import logging
from sqlalchemy import text
from app.database import SessionLocal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_integrations():
    """Show all integrations in the database."""
    try:
        db = SessionLocal()
        
        try:
            # First, check what columns actually exist
            columns_result = db.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'integrations'"
            ))
            columns = [row[0] for row in columns_result]
            print("Columns in integrations table:", columns)
            
            # Build a dynamic query based on available columns
            has_is_connected = 'is_connected' in columns
            has_status = 'status' in columns
            has_user_id = 'user_id' in columns
            
            select_parts = ["id", "platform"]
            
            if has_user_id:
                select_parts.append("user_id")
            else:
                select_parts.append("NULL as user_id")
                
            if has_is_connected:
                select_parts.append("is_connected")
            else:
                select_parts.append("NULL as is_connected")
                
            if has_status:
                select_parts.append("status")
            else:
                select_parts.append("NULL as status")
                
            select_parts.extend(["account_name", "account_id"])
            
            query = f"""
                SELECT {', '.join(select_parts)}
                FROM integrations
                ORDER BY platform
            """
            
            if has_user_id:
                query = f"""
                    SELECT {', '.join(select_parts)}
                    FROM integrations
                    ORDER BY user_id, platform
                """
            
            # Get all integrations
            result = db.execute(text(query))
            rows = result.fetchall()
            
            print("\nIntegrations in the database:")
            header = "ID | Platform"
            if has_user_id:
                header += " | User ID"
            if has_is_connected:
                header += " | Connected"
            if has_status:
                header += " | Status"
            header += " | Account Name | Account ID"
            
            print(header)
            print("-" * 120)
            
            for row in rows:
                values = [str(row[0]), row[1]]  # ID and platform
                col_idx = 2
                
                if has_user_id:
                    values.append(str(row[col_idx]))
                    col_idx += 1
                    
                if has_is_connected:
                    values.append(str(row[col_idx]))
                    col_idx += 1
                    
                if has_status:
                    values.append(str(row[col_idx]) if row[col_idx] else "unknown")
                    col_idx += 1
                    
                values.extend([str(row[col_idx]) if row[col_idx] else "-", 
                              str(row[col_idx+1]) if row[col_idx+1] else "-"])
                
                print(" | ".join(values))
            
            print("\nTotal integrations:", len(rows))
            
            # Count by user_id if it exists
            if has_user_id:
                result = db.execute(text("""
                    SELECT user_id, COUNT(*) 
                    FROM integrations 
                    GROUP BY user_id
                    ORDER BY user_id
                """))
                user_counts = result.fetchall()
                
                print("\nIntegrations by user:")
                for user_id, count in user_counts:
                    print(f"User {user_id}: {count} integrations")
                
            return True
            
        except Exception as e:
            logger.error(f"Error querying integrations: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    show_integrations() 