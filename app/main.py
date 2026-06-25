from __future__ import annotations

import hashlib
import random
import uuid
from datetime import date, timedelta
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Vietnamese Person API",
    description="API tạo thông tin người Việt Nam giả lập phục vụ kiểm thử và phát triển.",
    version="1.0.0",
)

Gender = Literal["male", "female", "other"]

FAMILY_NAMES = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan",
    "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý",
]

MALE_GIVEN_NAMES = [
    ("An", "Andrew"), ("Bảo", "Brian"), ("Dũng", "Daniel"),
    ("Đức", "David"), ("Hải", "Henry"), ("Hùng", "Hugo"),
    ("Khang", "Kevin"), ("Long", "Leo"), ("Minh", "Michael"),
    ("Nam", "Nathan"), ("Phong", "Peter"), ("Quân", "Quinn"),
    ("Sơn", "Sean"), ("Thành", "Thomas"), ("Tuấn", "Tony"),
]

FEMALE_GIVEN_NAMES = [
    ("An", "Anna"), ("Anh", "Amy"), ("Chi", "Chloe"),
    ("Hà", "Hannah"), ("Hạnh", "Helen"), ("Hương", "Hazel"),
    ("Lan", "Lana"), ("Linh", "Linda"), ("Mai", "Mia"),
    ("Ngọc", "Nicole"), ("Nhung", "Nina"), ("Phương", "Phoebe"),
    ("Thảo", "Taylor"), ("Trang", "Tracy"), ("Vy", "Violet"),
]

OTHER_GIVEN_NAMES = [
    ("An", "Alex"), ("Bình", "Blake"), ("Khánh", "Kai"),
    ("Minh", "Morgan"), ("Thanh", "Taylor"),
]

MIDDLE_NAMES = {
    "male": ["Văn", "Hữu", "Đức", "Quang", "Minh", None],
    "female": ["Thị", "Ngọc", "Thu", "Thanh", "Bảo", None],
    "other": ["Minh", "Thanh", "Ngọc", None],
}


class NameInfo(BaseModel):
    vietnamese_full_name: str = Field(examples=["Nguyễn Văn Minh"])
    english_full_name: str = Field(examples=["Michael Nguyen"])
    family_name: str = Field(description="Họ", examples=["Nguyễn"])
    middle_name: str | None = Field(default=None, description="Tên lót, có thể không có")
    given_name: str = Field(description="Tên chính", examples=["Minh"])
    english_given_name: str = Field(examples=["Michael"])


class BirthInfo(BaseModel):
    date: date
    day: int
    month: int
    year: int
    age: int


class Person(BaseModel):
    id: uuid.UUID
    is_synthetic: bool = True
    gender: Gender
    gender_vi: str
    name: NameInfo
    birth: BirthInfo


def calculate_age(birth_date: date, today: date | None = None) -> int:
    today = today or date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def random_birth_date(rng: random.Random, min_age: int, max_age: int) -> date:
    today = date.today()
    latest = date(today.year - min_age, today.month, today.day)
    earliest = date(today.year - max_age - 1, today.month, today.day) + timedelta(days=1)
    days = (latest - earliest).days
    return earliest + timedelta(days=rng.randint(0, days))


def build_person(
    *,
    gender: Gender | None = None,
    min_age: int = 18,
    max_age: int = 80,
    seed: str | None = None,
) -> Person:
    if min_age > max_age:
        raise ValueError("min_age không được lớn hơn max_age")

    rng = random.Random()
    if seed is not None:
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        rng.seed(int(digest, 16))

    selected_gender: Gender = gender or rng.choice(["male", "female", "other"])
    family_name = rng.choice(FAMILY_NAMES)
    middle_name = rng.choice(MIDDLE_NAMES[selected_gender])

    name_pool = {
        "male": MALE_GIVEN_NAMES,
        "female": FEMALE_GIVEN_NAMES,
        "other": OTHER_GIVEN_NAMES,
    }[selected_gender]
    given_name, english_given_name = rng.choice(name_pool)

    vietnamese_parts = [family_name]
    if middle_name:
        vietnamese_parts.append(middle_name)
    vietnamese_parts.append(given_name)

    # Chuyển một số họ phổ biến sang dạng không dấu quen dùng trong tên tiếng Anh.
    english_family_name = {
        "Nguyễn": "Nguyen", "Trần": "Tran", "Lê": "Le", "Phạm": "Pham",
        "Hoàng": "Hoang", "Huỳnh": "Huynh", "Phan": "Phan", "Vũ": "Vu",
        "Võ": "Vo", "Đặng": "Dang", "Bùi": "Bui", "Đỗ": "Do",
        "Hồ": "Ho", "Ngô": "Ngo", "Dương": "Duong", "Lý": "Ly",
    }[family_name]

    birth_date = random_birth_date(rng, min_age, max_age)

    person_id = (
        uuid.uuid5(uuid.NAMESPACE_URL, f"person-api:{seed}")
        if seed is not None
        else uuid.uuid4()
    )

    return Person(
        id=person_id,
        gender=selected_gender,
        gender_vi={"male": "Nam", "female": "Nữ", "other": "Khác"}[selected_gender],
        name=NameInfo(
            vietnamese_full_name=" ".join(vietnamese_parts),
            english_full_name=f"{english_given_name} {english_family_name}",
            family_name=family_name,
            middle_name=middle_name,
            given_name=given_name,
            english_given_name=english_given_name,
        ),
        birth=BirthInfo(
            date=birth_date,
            day=birth_date.day,
            month=birth_date.month,
            year=birth_date.year,
            age=calculate_age(birth_date),
        ),
    )


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {
        "message": "Vietnamese Person API",
        "docs": "/docs",
        "health": "/health",
        "person": "/api/person",
    }


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/person", response_model=Person, tags=["Person"])
def get_person(
    gender: Gender | None = Query(default=None),
    min_age: int = Query(default=18, ge=0, le=120),
    max_age: int = Query(default=80, ge=0, le=120),
    seed: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Cùng seed sẽ trả về cùng một người giả lập.",
    ),
) -> Person:
    if min_age > max_age:
        raise HTTPException(
            status_code=422,
            detail="min_age không được lớn hơn max_age",
        )

    return build_person(
        gender=gender,
        min_age=min_age,
        max_age=max_age,
        seed=seed,
    )
