# Milestone 1: adım adım

Oct 2, 2026 · @Metin

Milestone 1 dört şeyi çalışır hale getirir: iskelet, giriş, araç listesi ve filo yönetimi. İlk beş görev Metin'de ve sıralıdır; B ve C bu sırada kurulum, Git ve rapor işlerini yapar.

## Takvim

&#91;embedded content: takvim · 3 hafta, 4 şerit\]

B'nin kod görevleri 1.5'e bağlıdır; Metin ilk beş görevi ikinci haftanın ortasına kadar bitirmezse üçüncü hafta sıkışır. 5 Ekim Pazartesi başlanırsa Milestone 1 25 Ekim'de biter.

## Ön koşullar

Üç kişinin de makinesinde dört araç kurulu olmalı; kurulum ilk ortak oturumdan önce evde yapılır.

| Araç | Ne için | Kontrol komutu |
| --- | --- | --- |
| Git | Sürüm kontrolü | `git --version` |
| Docker Desktop | PostgreSQL'i çalıştırmak | `docker --version` ve `docker compose version` |
| uv | Python'u ve paketleri kurmak | `uv --version` |
| VS Code | Kod düzenleme (Python eklentisiyle) |  |

Ayrıca herkesin bir GitHub hesabı olmalı ve Metin repoya ortak olarak eklemeli. Python'u ayrıca kurmaya gerek yok; `uv sync` projenin istediği sürümü kendisi indirir.

Bu sayfadaki uv komutları ve kod parçaları 2 Ekim 2026'da PostgreSQL 16, FastAPI 0.142 ve SQLAlchemy 2.1 ile çalıştırılarak denendi. Docker Compose dosyası ve GitHub adımları denenmedi; test ortamında aynı sürümde yerel bir PostgreSQL kullanıldı. Komutlar bash içindir; Windows'ta Git ile gelen Git Bash kullanılır.

## 1.1 Repo ve iskelet

Sahip: Metin. Sonuç: boş ama çalışan bir uygulama; `/health` cevap verir, veritabanı Docker'da ayaktadır ve repo GitHub'dadır.

**1. Projeyi oluştur ve paketleri ekle.**

```bash
uv init car-rental
cd car-rental
rm main.py
uv add fastapi "uvicorn[standard]" sqlalchemy "psycopg[binary]" jinja2 \
       python-multipart itsdangerous "pwdlib[argon2]" pydantic-settings
uv add --dev pytest
mkdir -p app/routers app/services app/templates app/static scripts tests
touch app/__init__.py app/routers/__init__.py app/services/__init__.py
```

Az bilinen paketlerin işi: `python-multipart` form verisini okur, `itsdangerous` oturum cookie'sini imzalar, `pwdlib[argon2]` parolayı hash'ler, `pydantic-settings` `.env` dosyasını okur, `psycopg` PostgreSQL sürücüsüdür.

**2. `pyproject.toml` sonuna pytest ayarını ekle.** Bu olmadan testler `app` paketini bulamaz.

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
```

**3. `docker-compose.yml` dosyasını yaz.**

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: car_rental
      POSTGRES_PASSWORD: car_rental
      POSTGRES_DB: car_rental
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

**4. Ortam değişkenlerini tanımla.** `.env.example` repoya girer, `.env` girmez.

```text
DATABASE_URL=postgresql+psycopg://car_rental:car_rental@localhost:5432/car_rental
SECRET_KEY=change-me
```

```bash
cp .env.example .env
echo ".env" >> .gitignore
```

Adresteki `+psycopg` kısmı sürücüyü açıkça seçer. SQLAlchemy 2.1 bu kısım yazılmasa da psycopg 3'ü kullanır, 2.0 ise kurulu olmayan eski `psycopg2` sürücüsünü arar; açık yazmak iki sürümde de doğru çalışır.

**5. `app/main.py` dosyasını en küçük haliyle yaz.**

```python
from fastapi import FastAPI

app = FastAPI(title="Car Rental")


@app.get("/health")
def health():
    return {"status": "ok"}
```

**6. Çalıştır ve kontrol et.**

```bash
docker compose up -d
uv run uvicorn app.main:app --reload
```

`http://localhost:8000/health` adresi `{"status":"ok"}` dönmeli, `http://localhost:8000/docs` açılmalı.

**7. GitHub'a gönder.** `uv init` yerel Git deposunu zaten oluşturur.

```bash
git add -A
git commit -m "Project skeleton"
git branch -M main
git remote add origin <repo-adresi>
git push -u origin main
```

Sonra GitHub'da B ve C'yi ortak olarak ekle ve `main` için "pull request zorunlu" kuralını aç (Settings, Rules). Bu kuralın özel repolarda uygulanması GitHub planına bağlıdır; uygulanmıyorsa repo herkese açık yapılır ya da kural takım içi söz olarak kalır.

**8. README'yi yaz.** Üç bölüm yeterli: kurulum, çalıştırma ve "Team". Kurulum bölümü şu komutlardır:

```bash
git clone <repo-adresi>
cd car-rental
cp .env.example .env
docker compose up -d
uv sync
uv run python -m scripts.seed        # 1.7 bittikten sonra
uv run uvicorn app.main:app --reload
```

**Kabul kontrolü:** README'yi izleyen biri temiz bir makinede 15 dakikada `/health` cevabını görür.

## 1.2 Modeller ve veritabanı

Sahip: Metin. Sonuç: uygulama açılırken üç tablo ve `no_double_booking` kısıtı kendiliğinden oluşur. Kısıt Milestone 2'de kullanılacak, ama tabloyla birlikte şimdi kurulur; sonradan eklemek veritabanını sıfırlamayı gerektirir.

**1. `app/config.py`: ayarları `.env` dosyasından oku.**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    secret_key: str


settings = Settings()
```

**2. `app/db.py`: bağlantı, oturum ve kurulum.**

```python
from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))
    Base.metadata.create_all(engine)


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
```

Extension satırı `create_all`'dan önce çalışmalıdır; kısıt `car_id` üzerinde eşitlik kullandığı için `btree_gist` olmadan tablo oluşturulamaz.

**3. `app/models.py`: üç tablo.**

```python
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import DATERANGE, ExcludeConstraint, Range
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    full_name: Mapped[str]
    role: Mapped[str]  # "customer" | "company"
    company_name: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    brand: Mapped[str]
    model: Mapped[str]
    year: Mapped[int]
    category: Mapped[str]  # economy | sedan | suv | van | luxury
    seats: Mapped[int]
    transmission: Mapped[str]  # manual | automatic
    fuel: Mapped[str]  # gasoline | diesel | hybrid | electric
    daily_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    city: Mapped[str]
    lat: Mapped[float]
    lng: Mapped[float]
    image_url: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default=True)

    owner: Mapped[User] = relationship()


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        ExcludeConstraint(
            ("car_id", "="),
            ("period", "&&"),
            where=text("status = 'confirmed'"),
            using="gist",
            name="no_double_booking",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    period: Mapped[Range[date]] = mapped_column(DATERANGE)
    status: Mapped[str] = mapped_column(default="confirmed")  # confirmed | cancelled
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    card_last4: Mapped[str] = mapped_column(String(4))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    car: Mapped[Car] = relationship()
    user: Mapped[User] = relationship()
```

**4. `app/main.py`: kurulumu uygulama açılışına bağla.** `models` import edilmezse `create_all` hiçbir tablo görmez.

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (tabloları Base.metadata'ya kaydeder)
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Car Rental", lifespan=lifespan)
```

**5. Kontrol et.** Uygulamayı yeniden başlat, sonra tabloyu incele:

```bash
docker compose exec db psql -U car_rental -c "\d reservations"
```

Çıktının "Indexes" bölümünde şu satır görünmelidir:

```text
"no_double_booking" EXCLUDE USING gist (car_id WITH =, period WITH &&) WHERE (status::text = 'confirmed'::text)
```

**Bilinmesi gerekenler:**

- `create_all` yalnız olmayan tabloları oluşturur, var olan tabloyu değiştirmez. Model değişince veritabanı seed script'iyle sıfırdan kurulur.
- Aralık `Range(alis, iade)` ile yazılır; varsayılan sınır `[)` yani yarı açıktır. Gün sayısı `(period.upper - period.lower).days` ile bulunur.
- Kısıt ihlalinde SQLAlchemy `IntegrityError` fırlatır ve `exc.orig.sqlstate` değeri `23P01` olur. Denemede kesişen ikinci kayıt reddedildi, iade günü başlayan kayıt ve iptal sonrası aynı aralık kabul edildi.

## 1.3 Kayıt, giriş ve yetki

Sahip: Metin. Sonuç: kullanıcı müşteri ya da şirket olarak kayıt olur, giriş ve çıkış yapar; korumalı sayfalar role göre açılır. Şablonlar 1.4'teki `base.html` dosyasını genişlettiği için önce o dosya yazılır.

Oturum şöyle çalışır: girişte kullanıcının numarası, rolü ve adı imzalı bir cookie'ye yazılır. Menü bu üç değeri doğrudan cookie'den okur; korumalı sayfalar ise kullanıcıyı veritabanından yükler.

**1. `app/deps.py`: ortak bağımlılıklar.**

```python
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User

templates = Jinja2Templates(directory="app/templates")

Db = Annotated[Session, Depends(get_db)]


class LoginRequired(Exception):
    pass


def current_user(request: Request, db: Db) -> User | None:
    user_id = request.session.get("user_id")
    return db.get(User, user_id) if user_id else None


def require_role(role: str):
    def dependency(user: Annotated[User | None, Depends(current_user)]) -> User:
        if user is None:
            raise LoginRequired
        if user.role != role:
            raise HTTPException(status_code=403)
        return user

    return dependency


Customer = Annotated[User, Depends(require_role("customer"))]
Company = Annotated[User, Depends(require_role("company"))]
```

Bir rotayı korumak için parametre eklemek yeterlidir: `def fleet_list(user: Company)`. B ve C yetki kodu yazmaz, yalnız bu iki tipi kullanır.

**2. `app/services/auth.py`: kayıt ve doğrulama.**

```python
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User

_hasher = PasswordHash.recommended()


def register(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: str,
    role: str,
    company_name: str | None,
) -> User | None:
    """Create a user. Returns None if the email is already registered."""
    user = User(
        email=email.strip().lower(),
        password_hash=_hasher.hash(password),
        full_name=full_name.strip(),
        role=role,
        company_name=company_name.strip() if role == "company" and company_name else None,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not _hasher.verify(password, user.password_hash):
        return None
    return user
```

**3. `app/routers/auth.py`: beş rota.**

```python
from typing import Annotated, Literal

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.deps import Db, templates
from app.models import User
from app.services import auth

router = APIRouter()


def _login(request: Request, user: User) -> None:
    request.session.update(user_id=user.id, role=user.role, name=user.full_name)


@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse(request, "auth/register.html")


@router.post("/register")
def register(
    request: Request,
    db: Db,
    email: Annotated[str, Form()],
    password: Annotated[str, Form(min_length=8)],
    full_name: Annotated[str, Form(min_length=1)],
    role: Annotated[Literal["customer", "company"], Form()],
    company_name: Annotated[str, Form()] = "",
):
    error = None
    if role == "company" and not company_name.strip():
        error = "Company name is required."
    else:
        user = auth.register(
            db,
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            company_name=company_name,
        )
        if user is None:
            error = "This email is already registered."
    if error:
        return templates.TemplateResponse(
            request, "auth/register.html", {"error": error}, status_code=400
        )
    _login(request, user)
    return RedirectResponse("/cars", status_code=303)


@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(request, "auth/login.html")


@router.post("/login")
def login(
    request: Request,
    db: Db,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    user = auth.authenticate(db, email, password)
    if user is None:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": "Wrong email or password."},
            status_code=400,
        )
    _login(request, user)
    return RedirectResponse("/cars", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
```

**4. `app/main.py`: oturum katmanını, yönlendirmeyi ve rotaları ekle.**

```python
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.deps import LoginRequired
from app.routers import auth

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax")
app.include_router(auth.router)


@app.exception_handler(LoginRequired)
def redirect_to_login(request: Request, exc: LoginRequired):
    return RedirectResponse("/login", status_code=303)
```

**5. İki şablonu yaz.** `app/templates/auth/login.html` aşağıdadır; takımın bütün formları bu kalıbı izler.

```html
{% extends "base.html" %}
{% block title %}Log in{% endblock %}
{% block content %}
<h1 class="h3 mb-3">Log in</h1>
{% if error %}<div class="alert alert-danger">{{ error }}</div>{% endif %}
<form method="post" class="col-md-4">
  <div class="mb-3">
    <label class="form-label" for="email">Email</label>
    <input class="form-control" type="email" id="email" name="email" required>
  </div>
  <div class="mb-3">
    <label class="form-label" for="password">Password</label>
    <input class="form-control" type="password" id="password" name="password" required>
  </div>
  <button class="btn btn-primary">Log in</button>
</form>
{% endblock %}
```

`auth/register.html` aynı kalıpla beş alan içerir: `full_name`, `email`, `password` (`minlength="8"`), `role` (`customer` ve `company` seçenekli `select`) ve `company_name`. Her `input`'un `name` değeri rotadaki parametre adıyla aynı olmalıdır.

**Kabul kontrolü:**

- [ ] Şirket olarak kayıt olunca `/cars` sayfasına yönlenir ve menüde "My fleet" görünür.
- [ ] Aynı e-postayla ikinci kayıt "This email is already registered." mesajını verir.
- [ ] Yanlış parola "Wrong email or password." mesajını verir.
- [ ] Giriş yapmamış kullanıcı korumalı sayfada `/login`'e yönlenir; yanlış roldeki kullanıcı 403 alır.

**Uç durumlar:**

- E-posta küçük harfe çevrilerek saklanır; `Acme@x.com` ile `acme@x.com` aynı hesaptır.
- Yanlış e-posta ve yanlış parola aynı mesajı verir; hangi e-postaların kayıtlı olduğu sızdırılmaz.
- Veritabanı seed ile sıfırlanınca tarayıcıdaki eski oturum başka bir kullanıcıya denk gelebilir. Seed'den sonra çıkış yapıp yeniden girilir.
- `SECRET_KEY` değişirse bütün oturumlar geçersiz olur.

## 1.4 Ortak şablon

Sahip: Metin. Sonuç: bütün sayfaların genişlettiği `base.html`, tek seferlik bildirim mesajı ve geçersiz girdide gösterilen hata sayfası. Arayüz metinleri İngilizce yazılır; rapor İngilizce olduğu için ekran görüntüleri raporla aynı dilde olur.

**1. `app/templates/base.html` dosyasını yaz.**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Car Rental{% endblock %}</title>
  <!-- Bootstrap CSS: getbootstrap.com "Get started" sayfasındaki <link> satırı buraya -->
</head>
<body>
<nav class="navbar navbar-expand bg-body-tertiary mb-4">
  <div class="container">
    <a class="navbar-brand" href="/cars">Car Rental</a>
    <ul class="navbar-nav me-auto">
      <li class="nav-item"><a class="nav-link" href="/cars">Cars</a></li>
      {% if request.session.role == "customer" %}
      <li class="nav-item"><a class="nav-link" href="/reservations">My reservations</a></li>
      {% elif request.session.role == "company" %}
      <li class="nav-item"><a class="nav-link" href="/fleet">My fleet</a></li>
      {% endif %}
    </ul>
    {% if request.session.user_id %}
    <span class="navbar-text me-3">{{ request.session.name }}</span>
    <form method="post" action="/logout">
      <button class="btn btn-outline-secondary btn-sm">Log out</button>
    </form>
    {% else %}
    <a class="btn btn-outline-primary btn-sm me-2" href="/login">Log in</a>
    <a class="btn btn-primary btn-sm" href="/register">Sign up</a>
    {% endif %}
  </div>
</nav>
<main class="container">
  {% set flash = request.session.pop("flash", None) %}
  {% if flash %}<div class="alert alert-success">{{ flash }}</div>{% endif %}
  {% block content %}{% endblock %}
</main>
</body>
</html>
```

**2. Bildirim mesajını kullan.** Bir işlem başarılı olunca rota mesajı oturuma yazar ve yönlendirir; `base.html` mesajı bir kez gösterip siler.

```python
request.session["flash"] = "Car added."
return RedirectResponse("/fleet", status_code=303)
```

**3. Hata sayfasını ekle.** Form modeli doğrulamadan geçmezse FastAPI ham JSON döner. `app/main.py` içindeki şu işleyici bunu okunur bir sayfaya çevirir:

```python
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.deps import templates

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.exception_handler(RequestValidationError)
def invalid_input(request: Request, exc: RequestValidationError):
    messages = [f"{error['loc'][-1]}: {error['msg']}" for error in exc.errors()]
    return templates.TemplateResponse(
        request,
        "error.html",
        {"title": "Invalid input", "messages": messages},
        status_code=422,
    )
```

`app/templates/error.html`:

```html
{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}
{% block content %}
<h1 class="h3 mb-3">{{ title }}</h1>
<ul>
  {% for message in messages %}<li>{{ message }}</li>{% endfor %}
</ul>
<a class="btn btn-outline-secondary" href="javascript:history.back()">Go back</a>
{% endblock %}
```

Git boş klasörü saklamaz; `app/static` klonlanan makinede olmazsa `StaticFiles` açılışta hata verir. Klasöre boş bir `style.css` koy.

**Kabul kontrolü:** menü giriş yapmamış kullanıcıda "Log in" ve "Sign up", müşteride "My reservations", şirkette "My fleet" gösterir. Bildirim mesajı sayfa yenilenince kaybolur.

## 1.5 Referans dilim: araç listesi ve filtreler

Sahip: Metin. Sonuç: `/cars` sayfası aktif araçları listeler ve altı filtreyle daraltır. Bu dilim B ve C'nin kopyalayacağı kalıptır; bu yüzden üç katmanın her biri ayrı dosyada ve kısa tutulur.

Bir isteğin yolu şöyledir: tarayıcı `GET /cars?fuel=diesel` gönderir, router sorgu parametrelerini `CarFilters` nesnesine çevirir, service sorguyu kurup çalıştırır, router sonucu şablona verir, şablon HTML üretir.

**1. `app/services/cars.py`: filtre modeli ve sorgu.**

```python
from collections.abc import Sequence
from decimal import Decimal

from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Car


class CarFilters(BaseModel):
    brand: str | None = None
    category: str | None = None
    transmission: str | None = None
    fuel: str | None = None
    min_seats: int | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None

    @field_validator("*", mode="before")
    @classmethod
    def empty_to_none(cls, value):
        # A blank form field arrives as "", which must mean "no filter".
        return None if value == "" else value


def list_cars(db: Session, filters: CarFilters) -> Sequence[Car]:
    stmt = select(Car).where(Car.is_active).order_by(Car.daily_price)
    if filters.brand:
        stmt = stmt.where(Car.brand == filters.brand)
    if filters.category:
        stmt = stmt.where(Car.category == filters.category)
    if filters.transmission:
        stmt = stmt.where(Car.transmission == filters.transmission)
    if filters.fuel:
        stmt = stmt.where(Car.fuel == filters.fuel)
    if filters.min_seats is not None:
        stmt = stmt.where(Car.seats >= filters.min_seats)
    if filters.min_price is not None:
        stmt = stmt.where(Car.daily_price >= filters.min_price)
    if filters.max_price is not None:
        stmt = stmt.where(Car.daily_price <= filters.max_price)
    return db.scalars(stmt).all()


def list_brands(db: Session) -> Sequence[str]:
    return db.scalars(
        select(Car.brand).where(Car.is_active).distinct().order_by(Car.brand)
    ).all()
```

`empty_to_none` şarttır: boş bırakılan sayı alanı tarayıcıdan `min_seats=` olarak gelir ve bu dönüşüm olmadan istek 422 ile reddedilir.

**2. `app/routers/cars.py`: tek rota.**

```python
from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.deps import Db, templates
from app.services import cars
from app.services.cars import CarFilters

router = APIRouter()


@router.get("/cars")
def car_list(request: Request, db: Db, filters: Annotated[CarFilters, Query()]):
    return templates.TemplateResponse(
        request,
        "cars/list.html",
        {
            "cars": cars.list_cars(db, filters),
            "brands": cars.list_brands(db),
            "filters": filters,
        },
    )
```

`app/main.py` içine `app.include_router(cars.router)` ve ana sayfa yönlendirmesi eklenir:

```python
@app.get("/")
def home():
    return RedirectResponse("/cars")
```

**3. `app/templates/cars/list.html`: filtre formu ve kartlar.** Form `method="get"` kullanır; böylece filtreler adres çubuğunda görünür ve bağlantı paylaşılabilir. Bir seçim kutusu ve kart döngüsü şöyledir; diğer beş alan aynı kalıbı izler.

```html
<form method="get" class="row g-2 mb-4">
  <div class="col-md-2">
    <select class="form-select" name="fuel">
      <option value="">Any fuel</option>
      {% for value in ["gasoline", "diesel", "hybrid", "electric"] %}
      <option value="{{ value }}" {{ "selected" if filters.fuel == value }}>{{ value|capitalize }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="col-md-1">
    <input class="form-control" type="number" name="min_seats" min="1" placeholder="Seats"
           value="{{ filters.min_seats or '' }}">
  </div>
  <div class="col-md-1">
    <button class="btn btn-primary w-100">Filter</button>
  </div>
</form>

{% if not cars %}
<p class="text-secondary">No cars match these filters.</p>
{% endif %}
<div class="row row-cols-1 row-cols-md-3 g-3">
  {% for car in cars %}
  <div class="col">
    <div class="card h-100">
      <div class="card-body">
        <h2 class="h5 card-title">{{ car.brand }} {{ car.model }} ({{ car.year }})</h2>
        <p class="card-text text-secondary">
          {{ car.category|capitalize }} · {{ car.seats }} seats · {{ car.transmission }} · {{ car.fuel }} · {{ car.city }}
        </p>
        <p class="card-text fw-semibold">{{ car.daily_price }} ₺ / day</p>
        <a class="btn btn-outline-primary btn-sm" href="/cars/{{ car.id }}">Details</a>
      </div>
    </div>
  </div>
  {% endfor %}
</div>
```

Altı filtre: marka (`brand`, veritabanındaki markalardan), kategori, vites, yakıt, en az koltuk (`min_seats`) ve fiyat aralığı (`min_price`, `max_price`).

**Kabul kontrolü:**

- [ ] Filtresiz sayfa bütün aktif araçları fiyata göre sıralı gösterir; pasif araç görünmez.
- [ ] Her filtre tek başına doğru sonucu verir.
- [ ] Birkaç filtre birlikte "ve" olarak çalışır.
- [ ] Bütün alanlar boşken "Filter" düğmesi hata vermez.
- [ ] Seçilen filtreler sayfa yenilenince formda seçili kalır.

Bu noktada veritabanında araç yoktur; kontrol için 1.7'deki seed'in iki araçlık ilk hali yeterlidir.

## 1.6 Üç ortak oturum

Metin yürütür, herkes katılır. Her oturum yaklaşık 1 saattir ve herkes komutları kendi makinesinde yazar; izlemek yetmez.

### Oturum 1: kurulum ve Git

1.1 biter bitmez yapılır.

1. Herkes README'deki kurulum komutlarını çalıştırır. Üç makinede de `/health` görülmeden sonraki adıma geçilmez.
2. Metin Git akışını bir kez gösterir, sonra B ve C aynısını yapar. Görev: README'deki "Team" listesine kendi adını eklemek.

   ```bash
   git switch main
   git pull
   git switch -c add-my-name
   # README.md içinde "Team" listesine adını ekle
   git add -A
   git commit -m "Add my name to team list"
   git push -u origin add-my-name
   ```
3. GitHub'da "Compare & pull request" ile PR açılır; Metin review edip merge eder.
4. B ve C aynı satıra ekleme yaptığı için ikinci PR çakışır. Bu bilerek kurulmuş bir alıştırmadır; çakışma birlikte çözülür.

   ```bash
   git merge main
   # README.md içindeki <<<<<<<, ======= ve >>>>>>> işaretlerini sil, iki adı da bırak
   git add README.md
   git commit
   git push
   ```
5. Merge'den sonra herkes `git switch main` ve `git pull` ile güncel koda döner.

Oturum, B ve C'nin birer PR'ı `main`'e girince biter.

### Oturum 2: HTTP ve referans dilim

1.5 bitince yapılır.

1. Tarayıcıda `/cars` açılır; geliştirici araçlarının Network sekmesinde istek ve cevap gösterilir: `GET`, 200, HTML.
2. Filtre formu gönderilir; adres çubuğundaki `?fuel=diesel` ile `CarFilters` içindeki `fuel` alanı eşleştirilir.
3. Giriş formu gönderilir; `POST`, 303 ve ardından gelen `GET` gösterilir. Yanlış parolayla 400 gösterilir.
4. Kod isteğin geçtiği sırayla okunur: `routers/cars.py`, `services/cars.py`, `models.py`, `templates/cars/list.html`, `base.html`.
5. B ve C birer küçük değişiklik yapar: biri service'te sıralamayı pahalıdan ucuza çevirir, diğeri şablonda karta şirket adını ekler. Değişiklikler commit edilmez.

Oturum, B ve C bir isteğin yolunu kendi cümleleriyle anlatabildiğinde biter.

### Oturum 3: ilk görev

Oturum 2'nin hemen ardından yapılır.

1. B, "My fleet" sayfasının rotasını ve boş şablonunu Metin'le birlikte yazar; listeyi ve formu yalnız bitirir.
2. C, seed script'e üçüncü aracı Metin'le birlikte ekler; kalanını yalnız yazar.
3. İkisi de görev dalını açıp ilk commit'i oturum bitmeden atar.

### PR review listesi

Metin her PR'da şu beş şeye bakar:

- Dalı kendi makinesinde çalıştırınca görevin kabul kontrolü geçiyor mu?
- Router içinde sorgu var mı? Varsa service'e taşınır.
- Korumalı rotada `Company` ya da `Customer` parametresi var mı?
- Başkasının kaydına erişim engellenmiş mi (sahiplik kontrolü)?
- PR tek bir sayfayı ya da tek bir işi mi kapsıyor?

## 1.7 Seed verisi

Sahip: C. Sonuç: tek komut veritabanını sıfırlar ve 3 şirket, 30 araç, 1 müşteri yükler. Herkes aynı veriyle çalışır, şema değişince veritabanı bu komutla yeniden kurulur.

Metin 1.5 sırasında script'in aşağıdaki iki araçlık halini yazar; C veriyi tamamlar.

```python
"""Reset the database and load demo data.

Run from the project root:  uv run python -m scripts.seed
"""

from decimal import Decimal

from app.db import Base, SessionLocal, engine, init_db
from app.models import Car
from app.services import auth

PASSWORD = "demo1234"

CITIES = {
    "Adana": (37.0000, 35.3213),
    "Ankara": (39.9334, 32.8597),
    "Istanbul": (41.0082, 28.9784),
    "Izmir": (38.4237, 27.1428),
    "Antalya": (36.8969, 30.7133),
}

# brand, model, year, category, seats, transmission, fuel, daily_price, city, lat_offset, lng_offset
COMPANIES = {
    ("acme@example.com", "Acme Rent"): [
        ("Fiat", "Egea", 2023, "sedan", 5, "manual", "diesel", "1200", "Adana", 0.010, -0.015),
        ("Renault", "Clio", 2022, "economy", 5, "automatic", "gasoline", "1100", "Adana", -0.020, 0.012),
    ],
}


def main() -> None:
    Base.metadata.drop_all(engine)
    init_db()
    with SessionLocal() as db:
        auth.register(db, email="customer@example.com", password=PASSWORD,
                      full_name="Demo Customer", role="customer", company_name=None)
        for (email, name), cars in COMPANIES.items():
            company = auth.register(db, email=email, password=PASSWORD,
                                    full_name=f"{name} Admin", role="company", company_name=name)
            for brand, model, year, category, seats, transmission, fuel, price, city, dlat, dlng in cars:
                lat, lng = CITIES[city]
                db.add(Car(owner_id=company.id, brand=brand, model=model, year=year,
                           category=category, seats=seats, transmission=transmission, fuel=fuel,
                           daily_price=Decimal(price), city=city, lat=lat + dlat, lng=lng + dlng))
        db.commit()
    print("Seed complete.")


if __name__ == "__main__":
    main()
```

**C'nin adımları:**

1. Güncel kodu al ve dal aç: `git switch main`, `git pull`, `git switch -c seed-data`.
2. Script'i çalıştır ve `/cars` sayfasında iki aracı gör: `uv run python -m scripts.seed`.
3. `COMPANIES` sözlüğüne iki şirket daha ekle ve araç sayısını 30'a tamamla. Her satır bir araçtır ve alan sırası sözlüğün üstündeki yorum satırındadır.
4. Aşağıdaki veri kurallarını sağla.
5. Script'i yeniden çalıştır, filtreleri dene, PR aç.

**Veri kuralları:**

- En az 4 şehir kullanılır ve her şehirde en az 4 araç bulunur.
- Her kategori, her vites türü ve her yakıt türü en az 3 araçta geçer; yoksa o filtre denenemez.
- En az 3 araç 7 ya da daha fazla koltukludur; öneri modülü kalabalık grup isteğinde bunlara ihtiyaç duyar.
- Fiyatlar kategoriyle tutarlıdır: `economy` en ucuz, `luxury` en pahalı.
- Aynı şehirdeki araçların `lat_offset` ve `lng_offset` değerleri birbirinden farklıdır ve -0.03 ile 0.03 arasındadır. Aynı noktadaki araçlar haritada üst üste biner.
- Şehir adları `CITIES` içindeki yazımla birebir aynıdır; koordinatlar yaklaşık şehir merkezleridir.

**Dikkat:** script bütün tabloları siler. Komut proje kökünden ve `-m` ile çalıştırılır; `python scripts/seed.py` yazılırsa `No module named 'app'` hatası alınır.

**Kabul kontrolü:** boş veritabanında komut hatasız biter; `/cars` 30 araç gösterir; `customer@example.com` ve üç şirket hesabı `demo1234` parolasıyla giriş yapar.

## 1.8, 1.9, 1.10 Filo ekranları ve araç detayı

Sahip: B. Üç görev üç ayrı PR'dır ve 1.5 `main`'e girdikten sonra başlar. Her görev 1.5'teki kalıbı izler: service'te fonksiyon, router'da rota, `templates` altında şablon.

| Görev | Rota | Ne yapar |
| --- | --- | --- |
| 1.8 | `GET /fleet` | Şirketin kendi araçlarını listeler |
| 1.8 | `GET /fleet/new`, `POST /fleet/new` | Ekleme formunu gösterir, aracı kaydeder |
| 1.9 | `GET /fleet/{car_id}/edit`, `POST /fleet/{car_id}/edit` | Aynı formu dolu gösterir, değişikliği kaydeder |
| 1.9 | `POST /fleet/{car_id}/toggle` | Aracı aktif ya da pasif yapar |
| 1.10 | `GET /cars/{car_id}` | Araç detayını gösterir |

### 1.8 Filom sayfası ve araç ekleme

1. Dal aç: `git switch main`, `git pull`, `git switch -c fleet-list`.
2. `app/services/fleet.py` dosyasını oluştur. Form modeli hangi alanın geçerli olduğunu tanımlar; geçersiz girdi 1.4'teki hata sayfasına düşer.

   ```python
   from collections.abc import Sequence
   from decimal import Decimal
   from typing import Literal
   
   from pydantic import BaseModel, Field, field_validator
   from sqlalchemy import select
   from sqlalchemy.orm import Session
   
   from app.models import Car
   
   
   class CarForm(BaseModel):
       brand: str = Field(min_length=1)
       model: str = Field(min_length=1)
       year: int = Field(ge=1990, le=2030)
       category: Literal["economy", "sedan", "suv", "van", "luxury"]
       seats: int = Field(ge=1, le=9)
       transmission: Literal["manual", "automatic"]
       fuel: Literal["gasoline", "diesel", "hybrid", "electric"]
       daily_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
       city: str = Field(min_length=1)
       lat: float = Field(ge=-90, le=90)
       lng: float = Field(ge=-180, le=180)
       image_url: str | None = None
   
       @field_validator("image_url", mode="before")
       @classmethod
       def empty_to_none(cls, value):
           return None if value == "" else value
   
   
   def list_for_owner(db: Session, owner_id: int) -> Sequence[Car]:
       return db.scalars(
           select(Car).where(Car.owner_id == owner_id).order_by(Car.brand, Car.model)
       ).all()
   
   
   def create(db: Session, owner_id: int, form: CarForm) -> Car:
       car = Car(owner_id=owner_id, **form.model_dump())
       db.add(car)
       db.commit()
       return car
   ```
3. `app/routers/fleet.py` dosyasını oluştur. Liste ve kayıt rotaları aşağıdadır; formu gösteren `GET /fleet/new` rotasını giriş sayfasının rotasına bakarak sen yaz.

   ```python
   from typing import Annotated
   
   from fastapi import APIRouter, Form, Request
   from fastapi.responses import RedirectResponse
   
   from app.deps import Company, Db, templates
   from app.services import fleet
   from app.services.fleet import CarForm
   
   router = APIRouter(prefix="/fleet")
   
   
   @router.get("")
   def fleet_list(request: Request, db: Db, user: Company):
       return templates.TemplateResponse(
           request, "fleet/list.html", {"cars": fleet.list_for_owner(db, user.id)}
       )
   
   
   @router.post("/new")
   def create(request: Request, db: Db, user: Company, form: Annotated[CarForm, Form()]):
       fleet.create(db, user.id, form)
       request.session["flash"] = "Car added."
       return RedirectResponse("/fleet", status_code=303)
   ```
4. `app/main.py` içine `app.include_router(fleet.router)` satırını ekle.
5. `app/templates/fleet/list.html` şablonunu yaz: "Add car" düğmesi, beş sütunlu tablo (araç, şehir, günlük fiyat, durum, işlemler) ve liste boşken gösterilen bir mesaj.
6. `app/templates/fleet/form.html` şablonunu yaz. Her alanın `name` değeri `CarForm` içindeki adla aynı olmalıdır:

   | Alan | Girdi | HTML kısıtı |
   | --- | --- | --- |
   | `brand`, `model`, `city` | `input` | `required` |
   | `year` | `input type="number"` | `min="1990" max="2030" required` |
   | `seats` | `input type="number"` | `min="1" max="9" required` |
   | `daily_price` | `input type="number"` | `min="1" step="0.01" required` |
   | `lat` | `input type="number"` | `min="-90" max="90" step="any" required` |
   | `lng` | `input type="number"` | `min="-180" max="180" step="any" required` |
   | `category`, `transmission`, `fuel` | `select` | Seçenekler `CarForm` içindeki değerlerle aynı |
   | `image_url` | `input type="url"` | Zorunlu değil |
7. Kontrol et, sonra PR aç.

**Kabul kontrolü:**

- [ ] İki farklı şirket hesabıyla araç eklenir; her şirket `/fleet` sayfasında yalnız kendi araçlarını görür.
- [ ] Boş bırakılan zorunlu alanı tarayıcı göndermez.
- [ ] Kayıttan sonra "Car added." mesajı bir kez görünür ve araç müşterinin `/cars` listesinde çıkar.
- [ ] Müşteri hesabıyla `/fleet` 403 verir.

### 1.9 Araç düzenleme ve pasife alma

1. `services/fleet.py` içine sahiplik kontrolünü ekle. Düzenleme ve pasife alma rotalarının hepsi aracı bu fonksiyonla alır.

   ```python
   def get_owned(db: Session, owner_id: int, car_id: int) -> Car | None:
       car = db.get(Car, car_id)
       return car if car and car.owner_id == owner_id else None
   ```
2. Aynı dosyaya `update(db, car, form)` ve `toggle_active(db, car)` fonksiyonlarını yaz. İlki formdaki değerleri araca atayıp `db.commit()` çağırır, ikincisi `is_active` değerini tersine çevirip `db.commit()` çağırır.
3. Üç rotayı ekle. Her biri önce `get_owned` çağırır; sonuç `None` ise `raise HTTPException(status_code=404)` ile biter.
4. `form.html`'i düzenlemede de kullan: rota şablona `car` gönderir (eklemede `None`). Alanlar `value="{{ car.brand if car }}"`, seçim kutuları `{{ "selected" if car and car.fuel == value }}` ile dolar.
5. `list.html` içinde her satıra "Edit" bağlantısı ve pasife alma düğmesi ekle. Düğme `method="post"` olan küçük bir formdur; veri değiştiren işlem bağlantıyla (`GET`) yapılmaz.

**Kabul kontrolü:**

- [ ] Düzenleme formu aracın mevcut değerleriyle açılır ve değişiklik müşteri listesine yansır.
- [ ] Başka şirketin araç numarasıyla `/fleet/{car_id}/edit` ve `/fleet/{car_id}/toggle` 404 verir.
- [ ] Pasife alınan araç `/cars` listesinde görünmez, `/fleet` listesinde "Inactive" olarak durur ve yeniden aktif edilebilir.

### 1.10 Araç detay sayfası

1. `services/cars.py` içine `get_active_car(db, car_id)` fonksiyonunu yaz: araç yoksa ya da pasifse `None` döner.
2. `routers/cars.py` içine `GET /cars/{car_id}` rotasını ekle; `None` gelirse 404 döner.
3. `templates/cars/detail.html` şablonunu yaz: araç adı ve yılı, şirket adı (`car.owner.company_name`), şehir, kategori, koltuk, vites, yakıt, günlük fiyat, varsa görsel ve listeye dönüş bağlantısı.

**Kabul kontrolü:**

- [ ] Listedeki "Details" düğmesi doğru aracın sayfasını açar.
- [ ] `/cars/99999` ve pasif bir aracın adresi 404 verir.

Tarih seçimi ve tutar önizlemesi bu sayfaya Milestone 2'de eklenir.

**Bilinmesi gerekenler:**

- Başkasının aracı için 403 değil 404 dönülür; böylece o numarada bir araç olup olmadığı da belli olmaz.
- HTML kısıtları yalnız tarayıcıda çalışır; asıl doğrulama `CarForm` içindedir. İkisi aynı sınırları taşımalıdır.
- Boş bırakılan `image_url` veritabanına boş metin olarak değil `NULL` olarak yazılır; `empty_to_none` bunu sağlar.

## 1.11, 1.12 Rapor işleri

Bu iki görev kod beklemez ve ilk haftada başlar. Rapor İngilizce yazılır; ara rapor vize tarihinde teslim edilir.

### 1.11 Literatür taraması için kaynak toplama

Sahip: C. Sonuç: raporun 2. bölümü ve kaynakçası için en az 10 doğrulanmış kaynak.

1. Ortak bir tablo aç. Sütunlar: APA 7 künyesi, tür (makale, kitap, resmi doküman, platform), konu, İngilizce iki cümlelik özet, bağlantı ya da DOI.
2. Üç konuyu İngilizce sorgularla tara:
   - Benzer platformlar: üç araç kiralama platformunun filtreleme, harita ve rezervasyon akışı incelenir.
   - Eşzamanlılık kontrolü: "double booking prevention", "optimistic vs pessimistic concurrency control", "PostgreSQL exclusion constraint range types".
   - LLM tabanlı öneri: "large language models recommender systems", "conversational recommendation", "LLM reranking".
3. Arama yerleri: Google Scholar, IEEE Xplore, ACM Digital Library ve teknolojilerin resmi dokümanları. Üniversite ağından tam metne erişilir.
4. Hedef dağılım: en az 4 akademik kaynak, 3 platform incelemesi, kalanı resmi doküman.
5. Her kaynağı aç ve en azından özetini oku; okumadığın kaynak tabloya girmez.

**Dikkat:** yapay zekâ araçları var olmayan makale künyeleri üretebilir. Bir araçtan gelen her kaynak, bağlantısı ya da DOI'si açılarak doğrulanır; açılmayan kaynak kullanılmaz.

**Kabul kontrolü:** tabloda en az 10 satır var, her satırın bağlantısı açılıyor, künyeler APA 7 biçiminde ve ilk yazar soyadına göre sıralı.

### 1.12 "Project Materials" taslağı ve use case diyagramı

**B, raporun 3. bölümünün bir sayfalık İngilizce taslağını yazar.** Alt başlıklar:

1. Software and Tools: araç, sürüm ve amaç sütunlu bir tablo. Sürümler `uv tree --depth 1` çıktısından alınır, amaçlar ana sekmedeki kararlar tablosundan.
2. System Architecture: üç katmanın birer cümlelik açıklaması; figür Milestone 2'de eklenir.
3. Data Model: üç tablonun birer cümlelik açıklaması.
4. Methods: eşzamanlılık kontrolü ve LLM önerisi için birer başlık; içleri Milestone 2 ve 3'te dolar.

**C, use case diyagramını draw.io ile çizer.** İçeriği:

- Aktörler: Customer, Company ve ikincil aktör olarak LLM Service.
- Customer: register and log in, browse and filter cars, filter cars on the map, view car details, rent a car, view and cancel reservations, get a smart recommendation.
- Company: register and log in, manage fleet (add, edit, deactivate), view incoming reservations.
- "Rent a car", "select dates" ve "simulated payment" adımlarını içerir; "get a smart recommendation" LLM Service'e bağlanır.

Diyagram PNG olarak dışa aktarılır ve draw.io kaynak dosyası repoda `docs/` altında saklanır.

**Şablon kuralları:** figürler "Figure 3.1." ve tablolar "Table 3.1." biçiminde numaralanır; figür ve tabloların öncesinde ve sonrasında birer boş satır bırakılır.

**Kabul kontrolü:** taslaktaki teknoloji listesi kararlar tablosuyla aynı; diyagramdaki her use case ana sekmedeki "Sayfalar ve rotalar" tablosunda bir sayfaya karşılık geliyor.

## Bitiş kontrolü

Milestone 1, aşağıdaki senaryo sıfırlanmış veritabanında baştan sona hatasız geçtiğinde biter. Senaryoyu Metin dışında biri çalıştırır; kodu yazan kişi kendi hatasını en zor görendir.

- [ ] `docker compose down -v`, `docker compose up -d`, `uv run python -m scripts.seed` ve uygulamanın başlatılması hatasız geçer.
- [ ] Yeni bir şirket hesabıyla kayıt olunur; menüde "My fleet" görünür.
- [ ] Şirket bir araç ekler; "Car added." mesajı bir kez görünür.
- [ ] Şirket aracı düzenler, pasife alır ve yeniden aktif eder.
- [ ] Çıkış yapılır; yeni bir müşteri hesabıyla kayıt olunur.
- [ ] Müşteri eklenen aracı marka ve fiyat filtresiyle bulur ve detay sayfasını açar.
- [ ] Müşteri `/fleet` adresinde 403 alır.
- [ ] Yanlış parolayla giriş reddedilir.
- [ ] `\d reservations` çıktısında `no_double_booking` görünür.
- [ ] Senaryo üç makinede de geçer.
- [ ] B ve C'nin kod PR'ları `main`'dedir; kaynak tablosu, "Project Materials" taslağı ve use case diyagramı hazırdır.
- [ ] Ana sekmedeki görev tablosunda 12 satırın durumu "Bitti" olarak işaretlidir.

## Sık karşılaşılan hatalar

Aşağıdaki dokuz hata bu iskelette beklenenlerdir; çoğu ilk kurulumda yaşanır.

| Belirti | Neden | Çözüm |
| --- | --- | --- |
| Açılışta `connection refused` | PostgreSQL container'ı çalışmıyor | Docker Desktop'ı aç, `docker compose up -d`, sonra `docker compose ps` ile kontrol et |
| `docker compose up` sırasında `port is already allocated` | Makinede 5432 portunu kullanan başka bir PostgreSQL var | `docker-compose.yml` içinde `"5433:5432"` yaz ve `.env` içindeki portu 5433 yap |
| `ValidationError ... database_url Field required` | `.env` dosyası yok | `cp .env.example .env` |
| `No module named 'psycopg2'` | `DATABASE_URL` `postgresql://` ile başlıyor ve kurulu SQLAlchemy 2.1'den eski | `postgresql+psycopg://` olarak düzelt |
| `No module named 'app'` | Komut proje kökünden ya da `-m` ile çalıştırılmadı | Kök klasörde `uv run python -m scripts.seed` |
| `TemplateNotFound` ya da `Directory 'app/static' does not exist` | Uygulama başka klasörden başlatıldı ya da `app/static` boş olduğu için repoya girmedi | Kök klasörden başlat; `app/static/style.css` dosyasını ekle |
| `SessionMiddleware must be installed` | `main.py` içinde `add_middleware` satırı yok | 1.3'teki 4. adımı uygula |
| Form gönderince "Invalid input" sayfası, alan adıyla `Field required` | `input`'un `name` değeri rotadaki ya da modeldeki adla eşleşmiyor | İki adı aynı yap |
| Model değişti ama tablo eski kaldı, `column ... does not exist` | `create_all` var olan tabloyu değiştirmez | `uv run python -m scripts.seed` ile sıfırdan kur |

İki durum hata mesajı vermez: seed'den sonra menüde yanlış kullanıcı adı görünürse çıkış yapıp yeniden girilir; `.env` değişikliği yansımıyorsa uygulama yeniden başlatılır.
