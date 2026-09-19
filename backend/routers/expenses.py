from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from models.database import get_db
import models.schemas as schemas
import api_schemas
from utils.auth import get_current_user, get_current_shop

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    dependencies=[Depends(get_current_user)]
)

@router.get("")
def get_expenses(
    shop: schemas.Shop = Depends(get_current_shop), 
    db: Session = Depends(get_db)
):

    expenses = db.query(schemas.Expense).filter(schemas.Expense.shop_id == shop.id).order_by(schemas.Expense.timestamp.desc()).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": exp.id,
                "category": exp.category,
                "amount": exp.amount,
                "description": exp.description,
                "timestamp": exp.timestamp
            } for exp in expenses
        ]
    }

@router.post("")
def add_expense(
    expense: api_schemas.ExpenseCreate, 
    db: Session = Depends(get_db),
    shop: schemas.Shop = Depends(get_current_shop)
):

    expense_dt = datetime.utcnow()
    if expense.expense_date:
        try:
            expense_dt = datetime.strptime(expense.expense_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")

    new_expense = schemas.Expense(
        shop_id=shop.id,
        category=expense.category,
        amount=expense.amount,
        description=expense.description,
        timestamp=expense_dt
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return {"success": True, "expense_id": new_expense.id}

@router.put("/{expense_id}")
def update_expense(
    expense_id: int,
    expense_update: api_schemas.ExpenseUpdate, 
    db: Session = Depends(get_db),
    shop: schemas.Shop = Depends(get_current_shop)
):
    expense = db.query(schemas.Expense).filter(
        schemas.Expense.id == expense_id,
        schemas.Expense.shop_id == shop.id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found or unauthorized")

    if expense_update.category is not None:
        expense.category = expense_update.category
    if expense_update.amount is not None:
        expense.amount = expense_update.amount
    if expense_update.description is not None:
        expense.description = expense_update.description

    db.commit()
    return {"success": True, "message": "Expense updated successfully"}

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    shop: schemas.Shop = Depends(get_current_shop)
):
    expense = db.query(schemas.Expense).filter(
        schemas.Expense.id == expense_id,
        schemas.Expense.shop_id == shop.id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found or unauthorized")

    db.delete(expense)
    db.commit()
    return {"success": True, "message": "Expense deleted successfully"}

@router.get("/summary")
def get_expenses_summary(
    shop: schemas.Shop = Depends(get_current_shop), 
    db: Session = Depends(get_db)
):

    # Total Sales Profit
    total_sales_profit = db.query(func.sum(schemas.Sale.profit)).filter(schemas.Sale.shop_id == shop.id).scalar() or 0.0
    
    # Expenses by Category
    expenses = db.query(
        schemas.Expense.category, 
        func.sum(schemas.Expense.amount).label("total")
    ).filter(schemas.Expense.shop_id == shop.id).group_by(schemas.Expense.category).all()
    
    expenses_breakdown = {cat: float(total) for cat, total in expenses}
    
    # We intentionally exclude 'Inventory Cost (Unsold)' from total expenses, 
    # as requested by the user, because unsold inventory is an asset, not a realized expense.
        
    total_expenses = sum(expenses_breakdown.values())
    
    true_net_profit = total_sales_profit - total_expenses
    
    return {
        "success": True,
        "data": {
            "total_sales_profit": total_sales_profit,
            "total_expenses": total_expenses,
            "true_net_profit": true_net_profit,
            "expenses_breakdown": expenses_breakdown
        }
    }
