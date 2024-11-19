import os
import aiohttp
import asyncio
import asyncpg
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import insert
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

metadata = MetaData()
engine = create_engine(DATABASE_URL)
metadata.reflect(bind=engine)
characters = metadata.tables['characters']

async def fetch_person(session, person_id):
    async with session.get(f'https://swapi.dev/api/people/{person_id}/') as response:
        if response.status == 200:
            return await response.json()
        return None

async def fetch_name_from_url(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data.get('title') or data.get('name')
        return None

async def process_character(person, session):
    films = [await fetch_name_from_url(session, film) for film in person['films']]
    species = [await fetch_name_from_url(session, species) for species in person['species']]
    starships = [await fetch_name_from_url(session, starship) for starship in person['starships']]
    vehicles = [await fetch_name_from_url(session, vehicle) for vehicle in person['vehicles']]
    homeworld = await fetch_name_from_url(session, person['homeworld'])

    return {
        "id": int(person['url'].split('/')[-2]),
        "birth_year": person["birth_year"],
        "eye_color": person["eye_color"],
        "films": ", ".join(films),
        "gender": person["gender"],
        "hair_color": person["hair_color"],
        "height": person["height"],
        "homeworld": homeworld,
        "mass": person["mass"],
        "name": person["name"],
        "skin_color": person["skin_color"],
        "species": ", ".join(species),
        "starships": ", ".join(starships),
        "vehicles": ", ".join(vehicles),
    }

async def save_to_db(conn, character):
    try:
        query = insert(characters).values(character)
        await conn.execute(query)
    except Exception as e:
        print(f"Ошибка при сохранении в базу данных: {e}")

async def main():
    async with aiohttp.ClientSession() as session, asyncpg.create_pool(DATABASE_URL) as pool:
        char_ids = range(1, 84)  # ID от 1 до 83, ну допустим

        # Семафор на 10 
        semaphore = asyncio.Semaphore(10)

        async def bound_fetch_and_save(person_id):
            # Ограничиваем количество одновременных операций
            async with semaphore:
                person = await fetch_person(session, person_id)
                if person:
                    character_data = await process_character(person, session)
                    async with pool.acquire() as conn:
                        await save_to_db(conn, character_data)
                        print(f"Данные персонажа {character_data['name']} загружены.")

        # Асинхронно обрабатываем всех и вся на этом свете
        tasks = [bound_fetch_and_save(person_id) for person_id in char_ids]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
