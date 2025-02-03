# flexpower_quant_challenge

My approach to solving Flex Power Quant Challenge 

## Task 1 Minimal Reporting tool

The first task is to build a _minimal reporting tool_ based on the database of 
base trades. A trade is represented as 
- `id`: int
- `price`: float
- `qantity`: int
- `side`: str (buy or sell)
- `strategy_id`: string

These trades are provided in a `sqlite` database with a table named 
'epex_12_20_12_13' (NOTE: different name) and schema
```sql
id TEXT PRIMARY KEY,
quantity INTEGER NOT NULL,
price REAL NOT NULL,
side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
strategy TEXT NOT NULL
```

### Task 1.1

Compute total buy and sell values. Here total buy volume can be computed via a sql query as 
```sql
    SELECT IFNULL(SUM(quantity), 0)
    FROM tbl_name
    WHERE side = 'buy'
```
where tbl_name is 'epex_12_20_12_13'. Similarly, total sell is 
```sql
    SELECT IFNULL(SUM(quantity), 0)
    FROM tbl_name
    WHERE side = 'sell'
```

To compute the PnL for a given strategy I sum sell orders (quantity * price) and 
substract buy orders (-quantity * price). In SQL it reads
```sql
SELECT IFNULL(SUM(
    CASE
        WHEN side = 'sell' THEN (quantity * price)
        WHEN side = 'buy'  THEN -(quantity * price)
    END
), 0)
FROM epex_2022_12_20_12-13
WHERE strategy = ?
```
for each strategy (strategy = ?). I also included '0' for the case if there is no trade. 

Finally, I need to expose the PnL calculation via an API. A standard approach is to 
use FastAPI. There the API end point can be created as  
```python
@app.get("/pnl/{strategy_id}")
def getpnl(strategy_id:str)->dict:
    """ return PnL for a given strategy """
    pnl_value = ... # compute pnl using query defined above
    return {
        "strategy": strategy_id,
        "value": pnl_value,
        "unit": "euro",
        "capture_time": datetime.utcnow().isoformat() + "Z"
    }
```

In the actual code is implemented in [task_1_minimal_reporting_tool.py](task_1_minimal_reporting_tool.py) 

I have add several safeguards regarding database access and API structure. 

In [test_task_1_minimal_reporting_tool.py](test_task_1_minimal_reporting_tool.py) 
I added a few simple tests. 

I also tried using `Depends` package to avoid loading database for each query but there 
seems to be a bug in the package dependencies which is a bit ironic... 

### Remarks 
- Table name specified in the task README is incorrect. The only table in the database is `epex_12_20_12_13`


### Installation and Usage

1. Clone the repository and open a bash shell inside.
2. Install dependencies and launch FastAPI 
```bash
pip install -r requirements.txt
uvicorn task_1_minimal_reporting_tool:app --reload
```
This creates a local endpoint at `http://127.0.0.1:8000` (default settings)

3. Open different terminal and run pytest (to check that server is up and running and basic functionaly works)
```bash
pytest test_task_1_minimal_reporting_tool.py
```

4. Example calls for _sell_, _buy_ and _pnl_ endpoints:

- http://127.0.0.1:8000/volume/buy 
- http://127.0.0.1:8000/volume/sell
- http://127.0.0.1:8000/pnl/strategy_1
- http://127.0.0.1:8000/pnl/strategy_2


## Task 2.1 - 2.6 

Please see notebook [task_2_eda_v2.ipynb](task_2_eda_v2.ipynb) for the solution.

## Task 2.7 

This task is a bit larger, so I put it into a separate notebook.  
Please see [task_2_7_ver2.ipynb](task_2_7_ver2.ipynb) for the solution.


