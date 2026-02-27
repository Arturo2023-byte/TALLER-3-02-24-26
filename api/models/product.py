from sqlalchemy import Column, String, Numeric, DateTime, text, Integer
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    name = Column(String(120), nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, server_default=text("0"))
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Product id={self.id} name={self.name} price={self.price} stock={self.stock}>"
