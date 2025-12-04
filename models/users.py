from typing import Optional, Dict, Any
from dataclasses import dataclass
from services.database_service import get_db


@dataclass
class User:
    user_id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    country: Optional[str]
    state_province: Optional[str]
    city: Optional[str]
    subscription_plan: Optional[str]
    subscription_start_date: Optional[str]  
    is_active: int  
    monthly_spend: Optional[float]
    primary_device: Optional[str]
    household_size: Optional[int]
    created_at: str
    role: str
    password_hash: str

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "gender": self.gender,
            "country": self.country,
            "state_province": self.state_province,
            "city": self.city,
            "subscription_plan": self.subscription_plan,
            "subscription_start_date": self.subscription_start_date,
            "is_active": bool(self.is_active),
            "monthly_spend": self.monthly_spend,
            "primary_device": self.primary_device,
            "household_size": self.household_size,
            "created_at": self.created_at,
            "role": self.role,
        }

    # Flask-Login compatibility
    def get_id(self) -> str:
        return str(self.user_id)


def initialize_users_table() -> None:

    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            first_name TEXT,
            last_name TEXT,
            age INTEGER,
            gender TEXT,
            country TEXT,
            state_province TEXT,
            city TEXT,
            subscription_plan TEXT,
            subscription_start_date TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            monthly_spend REAL,
            primary_device TEXT,
            household_size INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            role TEXT NOT NULL DEFAULT 'user',
            password_hash TEXT NOT NULL
        )
        """
    )
    db.commit()


def row_to_user(row) -> Optional[User]:
    if row is None:
        return None
    return User(
        user_id=row["user_id"],
        email=row["email"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        age=row["age"],
        gender=row["gender"],
        country=row["country"],
        state_province=row["state_province"],
        city=row["city"],
        subscription_plan=row["subscription_plan"],
        subscription_start_date=row["subscription_start_date"],
        is_active=row["is_active"],
        monthly_spend=row["monthly_spend"],
        primary_device=row["primary_device"],
        household_size=row["household_size"],
        created_at=row["created_at"],
        role=row["role"],
        password_hash=row["password_hash"],
    )


