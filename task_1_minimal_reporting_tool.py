from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sqlite3

# NOTE: it is better to use .env varaible
DB_PATH = './database/trades.sqlite'

# Initialize FastAPI app
app = FastAPI(title="Energy Trading API", version="1.0.0")

# NOTE: it is better to use persistent connection instead of connecting each time...
def get_db():
    """Opens a new SQLite connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enables access to columns by name
    return conn

# Utility function to execute queries
def execute_query(query: str, params: tuple):
    """Executes an SQL query and returns a single value."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()[0] or 0.0
        conn.close()
        return result
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Dynamic table name function
def get_trade_table() -> str:
    """Returns the trade table name dynamically."""
    return "'epex_12_20_12_13'"  # corrected table name

# Function to retrieve available strategies
def get_available_strategies() -> list:
    """Fetches a list of all available strategy IDs from the database."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        query = f"SELECT DISTINCT strategy FROM {get_trade_table()}"
        cursor.execute(query)
        strategies = [row[0] for row in cursor.fetchall()]
        conn.close()
        return strategies
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



# Functions to compute trading metrics
def compute_total_buy_volume() -> float:
    query = f"SELECT IFNULL(SUM(quantity), 0) FROM {get_trade_table()} WHERE side = 'buy'"
    return float(execute_query(query, ()))

def compute_total_sell_volume() -> float:
    query = f"SELECT IFNULL(SUM(quantity), 0) FROM {get_trade_table()} WHERE side = 'sell'"
    return float(execute_query(query, ()))

def compute_pnl(strategy_id: str) -> float:
    # Check if strategy_id exists
    available_strategies = get_available_strategies()
    if strategy_id not in available_strategies:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Strategy '{strategy_id}' not found.",
                "available_strategies": available_strategies
            }
        )

    # Compute PnL if the strategy exists
    query = f"""
        SELECT IFNULL(SUM(
            CASE 
              WHEN side = 'sell' THEN (quantity * price)
              WHEN side = 'buy'  THEN -(quantity * price)
            END
        ), 0)
        FROM {get_trade_table()}
        WHERE strategy = ?
    """
    return float(execute_query(query, (strategy_id,)))

# Pydantic model for API response
class PnLResponse(BaseModel):
    strategy: str
    value: float
    unit: str = "euro"
    capture_time: str

# API endpoint to fetch PnL for a strategy
@app.get("/pnl/{strategy_id}", response_model=PnLResponse)
def get_pnl(strategy_id: str) -> PnLResponse:
    pnl_value = compute_pnl(strategy_id)
    return PnLResponse(
        strategy=strategy_id,
        value=pnl_value,
        capture_time=datetime.utcnow().isoformat() + "Z"
    )

# API endpoint to fetch total buy volume
@app.get("/volume/buy", response_model=dict)
def get_total_buy_volume():
    buy_volume = compute_total_buy_volume()
    return {"total_buy_volume": buy_volume, "unit": "MW"}

# API endpoint to fetch total sell volume
@app.get("/volume/sell", response_model=dict)
def get_total_sell_volume():
    sell_volume = compute_total_sell_volume()
    return {"total_sell_volume": sell_volume, "unit": "MW"}

# API root path
@app.get("/")
def home():
    return {"message": "Welcome to the Energy Trading API"}