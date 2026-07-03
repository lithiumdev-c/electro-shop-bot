from sqlalchemy import select

from app.database.models import Category, Item, User, async_session


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def category_items(category: int):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == category))


async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))
