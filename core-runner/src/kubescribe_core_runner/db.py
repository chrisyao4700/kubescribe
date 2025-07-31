from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

def make_engine(url: str) -> Engine:
    # Use pool_pre_ping to avoid stale connections
    return create_engine(url, pool_pre_ping=True, future=True)

def simple_count(engine: Engine, table: str) -> int:
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
