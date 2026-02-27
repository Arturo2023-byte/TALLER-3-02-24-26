from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID

from database import get_db
from models.cart import Cart, CartItem
from models.product import Product
from models.user import User

router = APIRouter()


class AddItemRequest(BaseModel):
    user_id: UUID
    product_id: UUID
    quantity: int = 1


class UpdateItemRequest(BaseModel):
    quantity: int


@router.get("/")
async def get_user_cart(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    items = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id)
        .all()
    )

    return {
        "cart_id": str(cart.id),
        "user_id": str(cart.user_id),
        "items": [
            {
                "item_id": str(i.id),
                "product_id": str(i.product_id),
                "quantity": i.quantity,
                "added_at": i.added_at,
            }
            for i in items
        ],
    }


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(payload: AddItemRequest, db: Session = Depends(get_db)):
    if payload.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be > 0")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    cart = db.query(Cart).filter(Cart.user_id == payload.user_id).first()
    if not cart:
        cart = Cart(user_id=payload.user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_id == payload.product_id)
        .first()
    )

    if item:
        item.quantity += payload.quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=payload.product_id, quantity=payload.quantity)
        db.add(item)

    db.commit()
    db.refresh(item)

    return {
        "item_id": str(item.id),
        "cart_id": str(item.cart_id),
        "product_id": str(item.product_id),
        "quantity": item.quantity,
        "added_at": item.added_at,
    }


@router.put("/items/{item_id}")
async def update_cart_item(item_id: UUID, payload: UpdateItemRequest, db: Session = Depends(get_db)):
    if payload.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be > 0")

    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    item.quantity = payload.quantity
    db.commit()
    db.refresh(item)

    return {
        "item_id": str(item.id),
        "cart_id": str(item.cart_id),
        "product_id": str(item.product_id),
        "quantity": item.quantity,
        "added_at": item.added_at,
    }


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_cart(item_id: UUID, db: Session = Depends(get_db)):
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    db.delete(item)
    db.commit()
    return


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(user_id: UUID, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        return

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return
