#!/usr/bin/env python3
"""Create database tables for testing."""

import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from shared.src.db.session import create_engine
from shared.src.models import Base

async def create_tables():
    """Create all database tables."""
    engine, _ = create_engine()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created successfully")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
