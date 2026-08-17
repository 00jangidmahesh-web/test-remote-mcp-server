import os
import sqlite3
from fastmcp import FastMCP

mcp = FastMCP(name="Expense Server")


DB_PATH =  os.path.join(os.path.dirname(__file__),'expenses.db')
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__),"categories.json")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """
        )

init_db()


@mcp.tool()
def add_expense(date,amount,category,subcategory="",note=""):
    """add a expense entry to the databse"""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
                  "insert into expenses(date,amount,category,subcategory,note) values (?,?,?,?,?)",
                  (date,amount,category,subcategory,note))
        return {'status':'ok','id':cur.lastrowid}


@mcp.tool()
def list_expense(start_date,end_date):
    "list expenses entries within inclusive date range"
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """
            select id,date,amount,category , subcategory , note
            from expenses
            where date between ? and ?
            order by id asc
            """,
            (start_date,end_date)
        )
        col = [d[0] for d in cur.description]
        return [dict(zip(col,r)) for r in cur.fetchall()]
    
    
@mcp.tool()
def summerize(start_date,end_date,category):
    '''summerize expenses by category within given inclusive date range'''
    with sqlite3.connect(DB_PATH) as c:
        query = """
                  select category , sum(amount) as total_amount
                  from expenses 
                  where date between ? and ?
                  """
        parms = [start_date,end_date]
        
        if category :
            query += " and category = ?"
            parms.append(category)
        
        query += " group by category order by category asc"
        cur = c.execute(query,parms)
        
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in cur.fetchall()]
    

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH,"r",encoding='utf-8') as f:
        return f.read()
        


if __name__ == "__main__":
    # HTTP/SSE transport ke liye:
    mcp.run(transport="sse", host="0.0.0.0", port=8000)