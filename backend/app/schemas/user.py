from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    # `extra="forbid"`: hasta ahora Pydantic descartaba en silencio cualquier
    # campo no declarado y el registro devolvía 201 como si nada. El frontend
    # manda `role`, `country` y `birth_year` (Screen1Register.jsx) y los tres
    # se perdían. Ahora un campo inesperado da 422 en vez de fingir que se
    # guardó. Ver TODO_MATIAS_SCHEMA.md para `role` y `country`.
    model_config = ConfigDict(extra="forbid")

    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    city_id: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def _map_birth_year_to_birth_date(cls, data):
        """Convierte el `birth_year` del frontend en el `birth_date` que ya existe.

        Corre en modo "before", así que `birth_year` desaparece del payload
        antes de que actúe `extra="forbid"` y nunca llega a ser un campo del
        modelo (si lo fuera, `User(**model_dump())` en UserService reventaría).

        Ojo: el año no lleva mes ni día, así que se normaliza a 1 de enero.
        Es una convención, no un dato real del usuario.
        """
        if not isinstance(data, dict) or "birth_year" not in data:
            return data

        data = dict(data)
        birth_year = data.pop("birth_year")

        # Un `birth_date` explícito manda sobre el año suelto.
        if birth_year in (None, "") or data.get("birth_date"):
            return data

        try:
            year = int(birth_year)
        except (TypeError, ValueError):
            raise ValueError("birth_year debe ser un año numérico")

        current_year = date.today().year
        if not 1900 <= year <= current_year:
            raise ValueError(f"birth_year fuera de rango (1900-{current_year})")

        data["birth_date"] = date(year, 1, 1)
        return data

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city_id: Optional[int] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None

    # Skills dinámicos inferidos por el motor IA
    # Ejemplo: {"pensamiento_analitico": 72.5, "creatividad": 65.0}
    inferred_skills: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Diccionario de micro-habilidades inferidas por el algoritmo vocacional"
    )

    # `Screen2bCareerSelect.jsx` ya mandaba este campo, pero al no estar
    # declarado Pydantic lo descartaba y el PATCH devolvía 200 como si se
    # hubiera guardado. La selección sólo sobrevivía en localStorage, así que se
    # perdía al cambiar de dispositivo. Mismo fallo silencioso que `role` y
    # `country` en el registro, y por eso también aquí hay `extra="forbid"`:
    # el siguiente campo no declarado dará 422 en vez de fingir que persistió.
    careers: Optional[List[str]] = Field(
        default=None,
        description="Slugs de las carreras elegidas en el onboarding",
    )

    model_config = ConfigDict(extra="forbid")

class UserOut(UserBase):
    id: int
    is_active: bool
    xp_total: int = 0
    level_current: int = 1
    created_at: datetime
    # CRITICAL: Include ALL optional profile fields
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    city_id: Optional[int] = None
    avatar_url: Optional[str] = None
    # Se expone para que el perfil del oráculo haga round-trip: el frontend lo
    # escribe vía PATCH /users/me y lo rehidrata al arrancar sin repetir el test.
    inferred_skills: Optional[Dict[str, Any]] = None
    # Se expone por la misma razón que `inferred_skills`: sin esto el cliente
    # puede escribir las carreras pero no volver a leerlas, y la rehidratación
    # desde el backend no serviría de nada.
    careers: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryMastery(BaseModel):
    category: str
    average_mastery: float = Field(..., ge=0.0, le=100.0)
    skill_count: int = Field(..., ge=0)


class UserStatsOut(BaseModel):
    user_id: int
    total_skills: int
    category_mastery: List[CategoryMastery] = []

    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserOut):
    hashed_password: str
