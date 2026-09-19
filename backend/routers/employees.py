from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from models.database import get_db
import models.schemas as schemas
import api_schemas
from utils.auth import get_current_user, get_current_shop

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    dependencies=[Depends(get_current_user)]
)

@router.get("")
def get_employees(
    shop: schemas.Shop = Depends(get_current_shop), 
    db: Session = Depends(get_db)
):

    employees = db.query(schemas.Employee).filter(schemas.Employee.shop_id == shop.id).order_by(schemas.Employee.join_date.desc()).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": emp.id,
                "name": emp.name,
                "role": emp.role,
                "salary_amount": emp.salary_amount,
                "join_date": emp.join_date
            } for emp in employees
        ]
    }

@router.post("")
def add_employee(
    employee: api_schemas.EmployeeCreate, 
    db: Session = Depends(get_db),
    shop: schemas.Shop = Depends(get_current_shop)
):

    join_dt = datetime.utcnow()
    if employee.join_date:
        try:
            join_dt = datetime.strptime(employee.join_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")

    new_employee = schemas.Employee(
        shop_id=shop.id,
        name=employee.name,
        role=employee.role,
        salary_amount=employee.salary_amount,
        join_date=join_dt
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return {"success": True, "employee_id": new_employee.id}
