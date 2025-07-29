import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from store.models.db_model import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://postgres:postgresql@localhost:5432/book_store')

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session factory
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Function to initialize tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_database():
    """Get a database session for dependency injection"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()