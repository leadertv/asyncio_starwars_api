import os
from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
metadata = MetaData()

characters = Table(
    'characters', metadata,
    Column('id', Integer, primary_key=True),
    Column('birth_year', String),
    Column('eye_color', String),
    Column('films', String),
    Column('gender', String),
    Column('hair_color', String),
    Column('height', String),
    Column('homeworld', String),
    Column('mass', String),
    Column('name', String),
    Column('skin_color', String),
    Column('species', String),
    Column('starships', String),
    Column('vehicles', String)
)

if __name__ == "__main__":
    metadata.create_all(engine)
    print("Таблица создана.")
