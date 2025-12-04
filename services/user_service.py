from typing import Optional, Any
from werkzeug.security import generate_password_hash, check_password_hash
from services.database_service import get_db
from models.users import User, row_to_user


def create_user(
    *,
    email: str,
    password: str,
    role: str = "user",
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    country: Optional[str] = None,
    state_province: Optional[str] = None,
    city: Optional[str] = None,
    subscription_plan: Optional[str] = None,
    subscription_start_date: Optional[str] = None,  # 'YYYY-MM-DD'
    is_active: bool = True,
    monthly_spend: Optional[float] = None,
    primary_device: Optional[str] = None,
    household_size: Optional[int] = None,
) -> User:
    db = get_db()
    password_hash = generate_password_hash(password)
    cur = db.execute(
        """
        INSERT INTO users (
            email, first_name, last_name, age, gender, country, state_province, city,
            subscription_plan, subscription_start_date, is_active, monthly_spend,
            primary_device, household_size, role, password_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            email, first_name, last_name, age, gender, country, state_province, city,
            subscription_plan, subscription_start_date, 1 if is_active else 0,
            monthly_spend, primary_device, household_size, role, password_hash
        ),
    )
    db.commit()
    return get_user_by_id(cur.lastrowid)  # type: ignore[arg-type]


def get_user_by_id(user_id: int) -> Optional[User]:
    db = get_db()
    row = db.execute(
        "SELECT * FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    return row_to_user(row)


def get_user_by_email(email: str) -> Optional[User]:
    db = get_db()
    row = db.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    return row_to_user(row)


def verify_credentials(email: str, password: str) -> Optional[User]:
    user = get_user_by_email(email)
    if user is None:
        return None
    if check_password_hash(user.password_hash, password):
        return user
    return None


def update_user(
    user_id: int,
    *,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    country: Optional[str] = None,
    state_province: Optional[str] = None,
    city: Optional[str] = None,
    subscription_plan: Optional[str] = None,
    subscription_start_date: Optional[str] = None,  # 'YYYY-MM-DD'
    is_active: Optional[bool] = None,
    monthly_spend: Optional[float] = None,
    primary_device: Optional[str] = None,
    household_size: Optional[int] = None,
    role: Optional[str] = None,
    password: Optional[str] = None,
) -> Optional[User]:
    db = get_db()
    fields = []
    values: list[Any] = []

    if email is not None:
        fields.append("email = ?")
        values.append(email)
    if first_name is not None:
        fields.append("first_name = ?")
        values.append(first_name)
    if last_name is not None:
        fields.append("last_name = ?")
        values.append(last_name)
    if age is not None:
        fields.append("age = ?")
        values.append(age)
    if gender is not None:
        fields.append("gender = ?")
        values.append(gender)
    if country is not None:
        fields.append("country = ?")
        values.append(country)
    if state_province is not None:
        fields.append("state_province = ?")
        values.append(state_province)
    if city is not None:
        fields.append("city = ?")
        values.append(city)
    if subscription_plan is not None:
        fields.append("subscription_plan = ?")
        values.append(subscription_plan)
    if subscription_start_date is not None:
        fields.append("subscription_start_date = ?")
        values.append(subscription_start_date)
    if is_active is not None:
        fields.append("is_active = ?")
        values.append(1 if is_active else 0)
    if monthly_spend is not None:
        fields.append("monthly_spend = ?")
        values.append(monthly_spend)
    if primary_device is not None:
        fields.append("primary_device = ?")
        values.append(primary_device)
    if household_size is not None:
        fields.append("household_size = ?")
        values.append(household_size)
    if role is not None:
        fields.append("role = ?")
        values.append(role)
    if password is not None:
        fields.append("password_hash = ?")
        values.append(generate_password_hash(password))

    if not fields:
        return get_user_by_id(user_id)

    values.append(user_id)
    db.execute(
        f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?",
        tuple(values),
    )
    db.commit()
    return get_user_by_id(user_id)


def delete_user(user_id: int) -> None:
    db = get_db()
    db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    db.commit()


