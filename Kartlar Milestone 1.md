# Görev kartları: Milestone 1

Oct 10, 2026 · @Metin

Milestone 1'in görevleri, her biri tek bir PR olan ve yapay zekâya olduğu gibi verilebilen kartlara bölündü. Kart numaraları ana sekmedeki görev numaralarını izler: 1.8a, 1.8b ve 1.8c birlikte 1.8'i tamamlar.

## Kart dizini

22 kart var: 10'u Metin'de, 7'si B'de, 5'i C'de. Bir kartın bağımlılıkları "Bitti" olmadan başlanmaz; tablo yukarıdan aşağı yaklaşık yapılış sırasıdır.

| Kart | Başlık | Sahip | Bağımlı | Durum |
| --- | --- | --- | --- | --- |
| 1.1a | Proje iskeleti | Metin |  | Başlamadı |
| 1.1b | GitHub, AGENTS.md ve CI | Metin | 1.1a | Bitti |
| 1.2a | Ayarlar, veritabanı ve modeller | Metin | 1.1a | Bitti |
| 1.2b | Test altyapısı | Metin | 1.3a | Başlamadı |
| 1.3a | Kimlik servisi ve yetki bağımlılıkları | Metin | 1.2a | Başlamadı |
| 1.4a | Ortak şablon ve hata sayfası | Metin | 1.2a | Başlamadı |
| 1.3b | Giriş ve kayıt sayfaları | Metin | 1.3a, 1.4a, 1.2b | Başlamadı |
| 1.5a | Araç listesi servisi | Metin | 1.2b | Başlamadı |
| 1.5b | Araç listesi sayfası ve boş rota dosyaları | Metin | 1.5a, 1.4a | Başlamadı |
| 1.7a | Seed iskeleti | Metin | 1.3a | Başlamadı |
| 1.7b | Demo verisi: 30 araç | C | 1.7a | Başlamadı |
| 1.8a | Filo servisi: form modeli, listeleme, ekleme | B | 1.5b | Başlamadı |
| 1.8b | Filom sayfası | B | 1.8a | Başlamadı |
| 1.8c | Araç ekleme formu | B | 1.8b | Başlamadı |
| 1.9a | Sahiplik, düzenleme ve pasife alma servisi | B | 1.8a | Başlamadı |
| 1.9b | Düzenleme sayfası | B | 1.9a, 1.8c | Başlamadı |
| 1.9c | Pasife alma düğmesi | B | 1.9a, 1.8b | Başlamadı |
| 1.10a | Araç detay sayfası | B | 1.5b | Başlamadı |
| 1.11a | Kaynak toplama | C |  | Başlamadı |
| 1.11b | Kaynakça (APA 7) | C | 1.11a | Başlamadı |
| 1.12a | "Project Materials" taslağı | B | 1.1b | Başlamadı |
| 1.12b | Use case diyagramı | C |  | Başlamadı |

Ortak oturumlar (ana plandaki 1.6) kart değildir; yeri ve gündemi "Milestone 1: adım adım" sekmesindedir. Oturum 1, 1.1b'den sonra; Oturum 2 ve 3, 1.5b'den sonra yapılır.

**Kart biçimi.** Her kartın ilk satırı dört şey söyler: sahibi, bağımlı olduğu kartlar, değişecek dosyalar ("Dosyalar") ve sohbet aracı kullanılıyorsa yapıştırılacak dosyalar ("Yapay zekâya ver"). Kartın tamamı, başlığından anlama sorularına kadar, istem şablonuna yapıştırılır.

## Kurulum kartları (Metin)

Bu dört kart bitmeden kimse kod kartına başlamaz. Kodların çoğu "Milestone 1: adım adım" sekmesinde test edilmiş halde duruyor; kartlar oraya atıf yapar ve yalnız yeni parçaları içerir.

### 1.1a · Proje iskeleti

**Sahip:** Metin · **Bağımlı:** yok · **Dosyalar:** `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `docker-compose.yml`, `.env.example`, `app/__init__.py`, `app/routers/__init__.py`, `app/services/__init__.py`, `app/main.py`, `README.md` · **Yapay zekâya ver:** yok

**Yapılacak**

- "Milestone 1: adım adım" sekmesinde 1.1'in 1'den 6'ya kadar olan adımları.
- Geliştirme paketleri: `uv add --dev pytest ruff httpx2`. Starlette'in güncel `TestClient`'ı `httpx2` ister; eski `httpx` ile her test çalışmasında uyarı verir.
- `pyproject.toml` sonuna ruff ve pytest ayarları:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]

[tool.ruff.lint.per-file-ignores]
"tests/conftest.py" = ["E402"]
```

**Kabul**

- [ ] `http://localhost:8000/health` adresi `{"status":"ok"}` döner.
- [ ] `uv run ruff format --check .` ve `uv run ruff check .` temizdir.

### 1.1b · GitHub, AGENTS.md ve CI

**Sahip:** Metin · **Bağımlı:** 1.1a · **Dosyalar:** `AGENTS.md`, `.github/workflows/ci.yml`, `.github/pull_request_template.md`, `README.md` · **Yapay zekâya ver:** yok

**Yapılacak**

- `AGENTS.md` dosyasını proje köküne koy. Dosya Metin'e ayrıca verildi; takımın bundan sonraki her kartı bu dosyaya dayanır.
- CI: her PR'da format, lint ve testleri gerçek bir PostgreSQL'e karşı çalıştırır.

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: car_rental
          POSTGRES_PASSWORD: car_rental
          POSTGRES_DB: car_rental
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      DATABASE_URL: postgresql+psycopg://car_rental:car_rental@localhost:5432/car_rental
      SECRET_KEY: ci-only-secret
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v7
      - run: uv sync --locked
      - run: uv run ruff format --check .
      - run: uv run ruff check .
      - run: uv run pytest
```

- PR şablonu (`.github/pull_request_template.md`): Kart, Ne yaptım, Nasıl denedim (üç onay kutusu: ruff temiz, pytest geçiyor, kabul kontrolü elle denendi), Anlama soruları (kendi cümlelerimle), Yapay zekâ (hangi araç, çıktıda elle neyin değişti). Dosya Metin'e ayrıca verildi.
- GitHub'da repoyu oluştur, gönder, B ve C'yi ekle. `main` kuralına "pull request zorunlu" ve "`check` durum kontrolü geçmeli" koşullarını koy. Özel repolarda kuralın uygulanması GitHub planına bağlıdır.

**Kabul**

- [ ] Bir deneme PR'ında CI çalışır ve yeşil olur.
- [ ] PR açılırken açıklama alanı şablonla dolu gelir.

### 1.2a · Ayarlar, veritabanı ve modeller

**Sahip:** Metin · **Bağımlı:** 1.1a · **Dosyalar:** `app/config.py`, `app/db.py`, `app/models.py`, `app/main.py` · **Yapay zekâya ver:** yok

**Yapılacak:** "Milestone 1: adım adım" sekmesindeki 1.2'nin 1'den 4'e kadar olan adımları; kod orada test edilmiş halde.

**Kabul**

- [ ] Uygulama açılınca `docker compose exec db psql -U car_rental -c "\d reservations"` çıktısında `no_double_booking` görünür.

### 1.2b · Test altyapısı

**Sahip:** Metin · **Bağımlı:** 1.3a (fabrika fixture'ı kayıt servisini kullanır) · **Dosyalar:** `tests/conftest.py`, `tests/test_smoke.py` · **Yapay zekâya ver:** yok

**Yapılacak:** testler ayrı bir `car_rental_test` veritabanı kullanır, yoksa kendisi oluşturur ve her testten önce sıfırlanır. Geliştirme verisi hiçbir testte silinmez. `AGENTS.md` 7. bölümdeki fixture listesi bu dosyayı anlatır.

```python
import os

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://car_rental:car_rental@localhost:5432/car_rental_test",
)
# Must happen before anything from `app` is imported: tests never touch the dev database.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from collections.abc import Callable, Iterator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session


def _ensure_test_database(url: str) -> None:
    target = make_url(url)
    admin = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": target.database}
        )
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{target.database}"'))
    admin.dispose()


_ensure_test_database(TEST_DATABASE_URL)

from app.db import Base, SessionLocal, engine, init_db
from app.main import app
from app.models import Car, User
from app.services import auth

PASSWORD = "secret123"


@pytest.fixture(autouse=True)
def reset_db() -> None:
    Base.metadata.drop_all(engine)
    init_db()


@pytest.fixture
def db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def make_user(db: Session) -> Callable[..., User]:
    count = 0

    def _make(role: str = "customer", email: str | None = None) -> User:
        nonlocal count
        count += 1
        user = auth.register(
            db,
            email=email or f"user{count}@example.com",
            password=PASSWORD,
            full_name=f"User {count}",
            role=role,
            company_name=f"Company {count}" if role == "company" else None,
        )
        assert user is not None
        return user

    return _make


@pytest.fixture
def make_car(db: Session) -> Callable[..., Car]:
    def _make(owner: User, **overrides) -> Car:
        values = {
            "brand": "Fiat",
            "model": "Egea",
            "year": 2023,
            "category": "sedan",
            "seats": 5,
            "transmission": "manual",
            "fuel": "diesel",
            "daily_price": Decimal("1200.00"),
            "city": "Adana",
            "lat": 37.0,
            "lng": 35.32,
        }
        values.update(overrides)
        car = Car(owner_id=owner.id, **values)
        db.add(car)
        db.commit()
        return car

    return _make


@pytest.fixture
def login(client: TestClient) -> Callable[[User], None]:
    def _login(user: User) -> None:
        response = client.post(
            "/login", data={"email": user.email, "password": PASSWORD}, follow_redirects=False
        )
        assert response.status_code == 303

    return _login
```

`tests/test_smoke.py`:

```python
def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_factories(make_user, make_car):
    car = make_car(make_user("company"))
    assert car.is_active
```

`login` fixture'ı 1.3b'deki `/login` rotası gelene kadar kullanılamaz.

**Kabul**

- [ ] `uv run pytest` iki testi geçirir ve geliştirme veritabanındaki seed verisi yerinde kalır.

## Giriş, ortak şablon ve araç listesi kartları (Metin)

Bu altı kart referans dilimi kurar: B ve C'nin yapay zekâsı bundan sonra bu dosyaları örnek alarak yazar. Bu yüzden `AGENTS.md`'deki kalıplardan sapmamalıdır.

### 1.3a · Kimlik servisi ve yetki bağımlılıkları

**Sahip:** Metin · **Bağımlı:** 1.2a · **Dosyalar:** `app/deps.py`, `app/services/auth.py` · **Yapay zekâya ver:** `app/models.py`, `app/db.py`

**Yapılacak:** "Milestone 1: adım adım" sekmesindeki 1.3'ün 1. ve 2. adımları. `deps.py` şunları dışa verir: `templates`, `Db`, `LoginRequired`, `current_user`, `require_role`, `Customer`, `Company`. Testleri 1.3b'de gelir.

**Kabul**

- [ ] `uv run python -c "import app.deps, app.services.auth"` hatasız çalışır.

### 1.4a · Ortak şablon ve hata sayfası

**Sahip:** Metin · **Bağımlı:** 1.2a · **Dosyalar:** `app/templates/base.html`, `app/templates/error.html`, `app/static/style.css`, `app/main.py` · **Yapay zekâya ver:** `app/main.py`

**Yapılacak:** "Milestone 1: adım adım" sekmesindeki 1.4'ün tüm adımları: menü, tek seferlik bildirim (`flash`), `/static` bağlama ve 422 hata sayfası. `style.css` boş kalabilir ama repoda bulunmalıdır.

**Kabul**

- [ ] `/cars?min_seats=abc` (1.5b'den sonra) "Invalid input" sayfasını gösterir, ham JSON göstermez.

### 1.3b · Giriş ve kayıt sayfaları

**Sahip:** Metin · **Bağımlı:** 1.3a, 1.4a, 1.2b · **Dosyalar:** `app/routers/auth.py`, `app/templates/auth/login.html`, `app/templates/auth/register.html`, `app/main.py`, `tests/test_auth.py` · **Yapay zekâya ver:** `app/deps.py`, `app/services/auth.py`, `app/main.py`, `app/templates/base.html`, `tests/conftest.py`

**Yapılacak:** "Milestone 1: adım adım" sekmesindeki 1.3'ün 3, 4 ve 5. adımları. Testler (`tests/test_auth.py`): şirket kaydı 303 ile `/cars`'a yönlenir ve menüde "My fleet" görünür; aynı e-posta ikinci kez 400 verir; şirket adı boşsa 400 verir; yanlış parola 400 verir; 8 karakterden kısa parola 422 verir; çıkıştan sonra menüde "Log in" görünür.

**Kabul**

- [ ] Testler geçer; tarayıcıda kayıt, çıkış ve giriş çalışır.

### 1.5a · Araç listesi servisi

**Sahip:** Metin · **Bağımlı:** 1.2b · **Dosyalar:** `app/services/cars.py`, `tests/test_cars.py` · **Yapay zekâya ver:** `app/models.py`, `tests/conftest.py`

**Yapılacak:** "Milestone 1: adım adım" sekmesindeki 1.5'in 1. adımı (`CarFilters`, `list_cars`, `list_brands`). Testler: her filtre tek başına, üç filtre birlikte, bütün alanlar boş metin gelince tüm aktif araçlar, pasif araç hiçbir sonuçta yok.

**Kabul**

- [ ] `uv run pytest tests/test_cars.py` geçer.

### 1.5b · Araç listesi sayfası ve boş rota dosyaları

**Sahip:** Metin · **Bağımlı:** 1.5a, 1.4a · **Dosyalar:** `app/routers/cars.py`, `app/templates/cars/list.html`, `app/routers/fleet.py`, `app/routers/reservations.py`, `app/routers/recommend.py`, `app/main.py` · **Yapay zekâya ver:** `app/services/cars.py`, `app/deps.py`, `app/main.py`, `app/templates/base.html`

**Yapılacak**

- "Milestone 1: adım adım" sekmesindeki 1.5'in 2. ve 3. adımları ve `/` adresinin `/cars`'a yönlenmesi.
- Üç boş rota dosyası oluştur ve `main.py`'ye bağla. B ve C böylece `main.py`'ye hiç dokunmaz:
  - `app/routers/fleet.py`: `router = APIRouter(prefix="/fleet")`
  - `app/routers/reservations.py`: `router = APIRouter()`
  - `app/routers/recommend.py`: `router = APIRouter()`

**Kabul**

- [ ] `/cars` sayfası filtrelerle çalışır; boş formla "Filter" hata vermez.
- [ ] Oturum 2 ve 3 bu karttan sonra yapılır.

### 1.7a · Seed iskeleti

**Sahip:** Metin · **Bağımlı:** 1.3a · **Dosyalar:** `scripts/seed.py` · **Yapay zekâya ver:** yok

**Yapılacak:** "Milestone 1: adım adım" sekmesindeki 1.7'nin iki araçlık script'i, olduğu gibi.

**Kabul**

- [ ] `uv run python -m scripts.seed` "Seed complete." yazar; `/cars` iki araç gösterir.

## Filo ekranları ve araç detayı kartları (B)

Yedi kart, her alan için önce servis sonra sayfa sırasıyla gider. Hepsi `main.py`'ye dokunmadan yapılır; rota dosyası 1.5b'de boş olarak hazırlandı.

### 1.8a · Filo servisi: form modeli, listeleme, ekleme

**Sahip:** B · **Bağımlı:** 1.5b · **Dosyalar:** `app/services/fleet.py` (yeni), `tests/test_fleet.py` (yeni) · **Yapay zekâya ver:** `app/models.py`, `app/services/cars.py` (örnek), `tests/conftest.py`

**Yapılacak**

- `CarForm` (Pydantic): `brand`, `model`, `city` en az 1 karakter; `year` 1990 ile 2030 arası; `category`, `transmission`, `fuel` yalnız `AGENTS.md` 4. bölümdeki değerler (`Literal`); `seats` 1 ile 9 arası; `daily_price` `Decimal`, 0'dan büyük, en fazla 10 basamak ve 2 ondalık; `lat` −90 ile 90, `lng` −180 ile 180 arası; `image_url` isteğe bağlı, boş metin `None` olur.
- `list_for_owner(db, owner_id) -> Sequence[Car]`: yalnız o şirketin araçları, aktif ve pasif hepsi, marka ve modele göre sıralı.
- `create(db, owner_id, form) -> Car`: aracı kaydeder ve döndürür.
- Testler: liste yalnız kendi araçlarını ve pasif aracı da içerir; `create` fiyatı `Decimal` olarak, boş görseli `None` olarak kaydeder; `CarForm` şunları reddeder: `seats=0`, `year=1980`, `category="truck"`, `daily_price=0`.

**Kabul**

- [ ] `uv run pytest tests/test_fleet.py` geçer.

**Anlama soruları**

1. Fiyat neden `float` değil de `Decimal`? `0.1 + 0.2` örneğiyle açıkla.
2. `empty_to_none` olmasaydı boş bırakılan görsel alanı veritabanına nasıl yazılırdı?
3. `list_for_owner` neden kullanıcıyı kendisi bulmuyor da `owner_id` alıyor?

### 1.8b · Filom sayfası

**Sahip:** B · **Bağımlı:** 1.8a · **Dosyalar:** `app/routers/fleet.py`, `app/templates/fleet/list.html` (yeni), `tests/test_fleet.py` · **Yapay zekâya ver:** `app/routers/fleet.py`, `app/routers/cars.py` (örnek), `app/deps.py`, `app/services/fleet.py`, `app/templates/base.html`, `app/templates/cars/list.html` (örnek), `tests/conftest.py`

**Yapılacak**

- `GET /fleet` (router'ın öneki zaten `/fleet`, yol `""`): `user: Company` ile korunur, `fleet/list.html`'i araçlarla gösterir.
- Şablon: başlık "My fleet", `/fleet/new`'e giden "Add car" düğmesi, beş sütunlu tablo (Car, City, Daily price, Status, boş bir işlem sütunu); liste boşsa "You have not added any cars yet."
- Testler: iki şirket varken her biri yalnız kendi aracını görür; müşteri 403 alır; giriş yapmamış kullanıcı 303 ile `/login`'e gider.

**Kabul**

- [ ] Tarayıcıda şirket hesabıyla menüdeki "My fleet" bu sayfayı açar.

**Anlama soruları**

1. `user: Company` parametresi giriş yapmamış biri için ve müşteri için ayrı ayrı ne yapar?
2. Router sorguyu neden kendisi yazmıyor?
3. Şablon `base.html`'i genişletmeseydi sayfada ne eksik olurdu?

### 1.8c · Araç ekleme formu

**Sahip:** B · **Bağımlı:** 1.8b · **Dosyalar:** `app/routers/fleet.py`, `app/templates/fleet/form.html` (yeni), `tests/test_fleet.py` · **Yapay zekâya ver:** `app/routers/fleet.py`, `app/services/fleet.py`, `app/routers/auth.py` (form örneği), `app/templates/auth/register.html` (örnek), `tests/conftest.py`

**Yapılacak**

- `GET /fleet/new`: `form.html`'i `car=None` ile gösterir.
- `POST /fleet/new`: `form: Annotated[CarForm, Form()]` alır, `fleet.create` çağırır, "Car added." bildirimi yazar, 303 ile `/fleet`'e döner.
- `form.html` hem ekleme hem düzenleme için tek şablondur: `car` yoksa başlık "Add car", varsa "Edit car". 12 alan ve HTML kısıtları "Milestone 1: adım adım" sekmesindeki 1.8 tablosundaki gibidir; üç seçim kutusu, "Save" düğmesi ve `/fleet`'e dönen "Cancel" bağlantısı.
- Testler: geçerli form 303 döner ve araç o şirkete kaydedilir; `seats=0` 422 ve "Invalid input" döner; müşterinin `POST`'u 403 alır.

**Kabul**

- [ ] Tarayıcıda eklenen araç hem "My fleet"te hem müşterinin `/cars` listesinde görünür.

**Anlama soruları**

1. Başarılı kayıttan sonra neden sayfa döndürülmüyor da 303 ile yönlendiriliyor? Sayfayı yenileyince ne olurdu?
2. HTML'deki `min="1"` varken `CarForm`'daki `ge=1` neden hâlâ gerekli?
3. "Car added." mesajı sayfa yenilenince neden kayboluyor?

### 1.9a · Sahiplik, düzenleme ve pasife alma servisi

**Sahip:** B · **Bağımlı:** 1.8a · **Dosyalar:** `app/services/fleet.py`, `tests/test_fleet.py` · **Yapay zekâya ver:** `app/services/fleet.py`, `app/models.py`, `tests/conftest.py`

**Yapılacak**

- `get_owned(db, owner_id, car_id) -> Car | None`: araç yoksa ya da başka şirketinse `None`.
- `update(db, car, form) -> None`: formdaki bütün alanları araca yazar ve kaydeder.
- `toggle_active(db, car) -> None`: `is_active` değerini tersine çevirir ve kaydeder.
- Testler: kendi aracı döner; başka şirketin aracı ve olmayan numara `None` döner; `update` fiyatı değiştirir; iki kez `toggle_active` aracı yeniden aktif yapar.

**Kabul**

- [ ] `uv run pytest tests/test_fleet.py` geçer.

**Anlama soruları**

1. Başka şirketin aracı için neden hata fırlatılmıyor da `None` dönüyor? Kararı kim veriyor?
2. Araç neden silinmiyor da pasife alınıyor? Rezervasyon tablosuyla ilişkisini düşün.

### 1.9b · Düzenleme sayfası

**Sahip:** B · **Bağımlı:** 1.9a, 1.8c · **Dosyalar:** `app/routers/fleet.py`, `app/templates/fleet/form.html`, `app/templates/fleet/list.html`, `tests/test_fleet.py` · **Yapay zekâya ver:** bu dört dosya, `app/services/fleet.py`, `tests/conftest.py`

**Yapılacak**

- `GET /fleet/{car_id}/edit`: `get_owned` ile aracı alır, yoksa 404; `form.html`'i `car` ile gösterir.
- `POST /fleet/{car_id}/edit`: `get_owned`, yoksa 404; `update`, "Car updated." bildirimi, 303 ile `/fleet`.
- `form.html` alanları doldurur: `value="{{ car.brand if car }}"`; seçim kutularında eşleşen seçenek `selected`; görsel için `{{ car.image_url or '' if car }}`.
- `list.html`'de her satıra "Edit" bağlantısı.
- Testler: düzenleme sonrası yeni model adı `/cars`'ta görünür; başka şirket hem `GET` hem `POST` ile 404 alır.

**Kabul**

- [ ] Form aracın mevcut değerleriyle açılır ve kaydedince liste güncellenir.

**Anlama soruları**

1. Başka şirketin aracında neden 403 değil 404 dönüyor?
2. Aynı `form.html` ekleme ile düzenlemeyi nasıl ayırt ediyor?

### 1.9c · Pasife alma düğmesi

**Sahip:** B · **Bağımlı:** 1.9a, 1.8b · **Dosyalar:** `app/routers/fleet.py`, `app/templates/fleet/list.html`, `tests/test_fleet.py` · **Yapay zekâya ver:** bu üç dosya, `app/services/fleet.py`, `tests/conftest.py`

**Yapılacak**

- `POST /fleet/{car_id}/toggle`: `get_owned`, yoksa 404; `toggle_active`; 303 ile `/fleet`.
- `list.html`'de her satırda küçük bir `method="post"` formu: araç aktifse "Deactivate", değilse "Activate".
- Testler: pasife alınan araç müşterinin `/cars` listesinden kaybolur ve `/fleet`'te "Inactive" görünür; başka şirket 404 alır.

**Kabul**

- [ ] Araç pasife alınıp yeniden aktif edilebilir.

**Anlama soruları**

1. Bu işlem neden bağlantı (`GET`) değil de form (`POST`)?
2. Pasif araç müşteri listesinden hangi dosyadaki hangi satır sayesinde kayboluyor?

### 1.10a · Araç detay sayfası

**Sahip:** B · **Bağımlı:** 1.5b · **Dosyalar:** `app/services/cars.py`, `app/routers/cars.py`, `app/templates/cars/detail.html` (yeni), `tests/test_cars.py` · **Yapay zekâya ver:** bu dört dosyadan var olanlar, `app/models.py`, `app/templates/cars/list.html`, `tests/conftest.py`

**Yapılacak**

- `get_active_car(db, car_id) -> Car | None`: araç yoksa ya da pasifse `None`.
- `GET /cars/{car_id}`: `None` gelirse 404, yoksa `cars/detail.html`.
- Şablon: "Fiat Egea (2023)" biçiminde başlık, "Offered by şirket adı · şehir" satırı (`car.owner.company_name`), varsa görsel, kategori, koltuk, vites, yakıt ve günlük fiyat, listeye dönüş bağlantısı.
- Testler: sayfa 200 döner ve şirket adını içerir; `/cars/99999` ve pasif araç 404 döner.

**Kabul**

- [ ] Listedeki "Details" düğmesi doğru aracı açar.

**Anlama soruları**

1. Şablondaki `car.owner.company_name` değerini hangi dosyadaki hangi satır mümkün kılıyor?
2. Pasif bir aracın detayı neden 404 dönüyor?

## Seed verisi kartı (C)

### 1.7b · Demo verisi: 30 araç

**Sahip:** C · **Bağımlı:** 1.7a · **Dosyalar:** `scripts/seed.py` · **Yapay zekâya ver:** `scripts/seed.py`, `app/models.py`

**Yapılacak**

- `COMPANIES` sözlüğüne iki uydurma şirket daha ekle ve toplam araç sayısını 30'a çıkar. Script'in geri kalanı değişmez; yalnız veri eklenir.
- Veri kuralları ("Milestone 1: adım adım" sekmesindeki 1.7 ile aynı):
  - En az 4 şehir, her şehirde en az 4 araç; şehir adları `CITIES` içindeki yazımla aynı.
  - Her kategori, her vites ve her yakıt türü en az 3 araçta.
  - En az 3 araç 7 ya da daha fazla koltuklu.
  - Gerçek marka ve model adları, yıl 2018 ile 2025 arası; fiyatlar kategoriyle tutarlı (`economy` en ucuz, `luxury` en pahalı).
  - Aynı şehirdeki araçların `lat_offset` ve `lng_offset` değerleri farklı ve −0.03 ile 0.03 arasında.
- Yapay zekâya kuralları madde madde ver ve ürettiği veriyi kurallara karşı tek tek say; sayımı kendin yap.

**Kabul**

- [ ] `uv run python -m scripts.seed` hatasız biter ve `/cars` 30 araç gösterir.
- [ ] Her filtrenin her seçeneği en az bir sonuç döndürür.
- [ ] Üç şirket hesabı ve `customer@example.com` `demo1234` parolasıyla giriş yapar.

**Anlama soruları**

1. Script neden önce bütün tabloları siliyor? Bu ne zaman tehlikeli olur?
2. `python -m scripts.seed` ile `python scripts/seed.py` arasındaki fark ne?
3. Aynı şehirdeki araçlara neden farklı koordinat kayması veriyoruz?

## Rapor kartları (B, C)

Rapor taslakları repoda `docs/report/` altında Markdown olarak yazılır ve kod gibi PR ile gelir; Word şablonuna aktarma Milestone 2'deki derleme kartındadır. Bu kartlarda yapay zekânın işi yazmayı hızlandırmaktır; kaynak bulmak ve doğrulamak insanın işidir.

### 1.11a · Kaynak toplama

**Sahip:** C · **Bağımlı:** yok · **Dosyalar:** `docs/report/sources.md` (yeni) · **Yapay zekâya ver:** ana sekmedeki "Kapsam" ve "Eşzamanlılık kontrolü" bölümleri

**Yapılacak**

- `sources.md` içinde bir tablo: künye (şimdilik başlık, yazar, yıl), tür (makale, kitap, resmi doküman, platform), konu, İngilizce iki cümlelik özet, bağlantı ya da DOI.
- Üç konu: benzer araç kiralama platformları, eşzamanlılık kontrolü (kötümser kilit, iyimser kilit, veritabanı kısıtı), LLM tabanlı öneri.
- Hedef: en az 10 kaynak; en az 4'ü akademik, 3'ü platform incelemesi, kalanı resmi doküman.
- Yapay zekâyı yalnız iki iş için kullan: Google Scholar, IEEE Xplore ve ACM Digital Library'de aranacak İngilizce sorguları önermek ve senin yapıştırdığın özeti iki cümleye indirmek.

**Dikkat:** yapay zekâdan doğrudan "kaynak öner" isteme. Var olmayan makaleler üretebilir. Tabloya yalnız kendin açıp özetini okuduğun kaynak girer.

**Kabul**

- [ ] Tabloda en az 10 satır var ve her bağlantı açılıyor.

**Anlama soruları**

1. Seçtiğin eşzamanlılık kaynağı hangi yöntemi anlatıyor? Bizim çözümümüzden farkı ne?
2. Bir kaynağın gerçek olduğunu nasıl doğruladın?

### 1.11b · Kaynakça (APA 7)

**Sahip:** C · **Bağımlı:** 1.11a · **Dosyalar:** `docs/report/references.md` (yeni) · **Yapay zekâya ver:** `docs/report/sources.md`

**Yapılacak**

- Yapay zekâdan her kaynak için APA 7 künyesi iste; bağlantıyı ya da DOI'yi de ver.
- Her künyede yazar adlarını, yılı ve başlığı kaynağın kendi sayfasıyla karşılaştır; yapay zekâ bunları sık yanlış yazar.
- Liste ilk yazarın soyadına göre alfabetik sıralıdır. Aslı 1,25 cm'lik askılı girinti Word aşamasında verilir.

**Kabul**

- [ ] Her künye kaynağın sayfasıyla birebir tutuyor; biçim APA'nın "Reference examples" sayfasındaki örneklerle aynı.

**Anlama soruları**

1. Bir dergi makalesi ile bir web sayfasının APA künyesi arasındaki iki fark ne?

### 1.12a · "Project Materials" taslağı

**Sahip:** B · **Bağımlı:** 1.1b · **Dosyalar:** `docs/report/03-project-materials.md` (yeni) · **Yapay zekâya ver:** ana sekmedeki "Mimari kararlar" ve "Teknolojiler ve kaynaklar" tablolarının metni, `uv tree --depth 1` çıktısı

**Yapılacak**

- Yapay zekâdan İngilizce, bir sayfalık taslak iste; dört alt başlık: 3.1 Software and Tools (araç, sürüm, amaç tablosu), 3.2 System Architecture, 3.3 Data Model, 3.4 Methods (eşzamanlılık ve LLM için birer boş başlık).
- Taslağı satır satır kararlar tablosuyla karşılaştır. Bizim kullanmadığımız bir teknoloji ya da özellik geçiyorsa sil.

**Kabul**

- [ ] Sürümler `uv tree` çıktısıyla aynı; Metin metni onayladı.

**Anlama soruları**

1. Neden SQLite yerine PostgreSQL seçtik?
2. Neden React kullanmadık?

### 1.12b · Use case diyagramı

**Sahip:** C · **Bağımlı:** yok · **Dosyalar:** `docs/diagrams/use-case.drawio`, `docs/diagrams/use-case.png` (yeni) · **Yapay zekâya ver:** ana sekmedeki "Sayfalar ve rotalar" tablosunun metni

**Yapılacak**

- Yapay zekâdan aktörleri, use case'leri ve aralarındaki ilişkileri liste olarak iste. İçerik "Milestone 1: adım adım" sekmesindeki 1.12 ile aynı olmalı: Customer, Company ve ikincil aktör LLM Service.
- Diyagramı draw.io'da kendin çiz, kaynağı ve PNG'yi repoya koy.

**Kabul**

- [ ] Diyagramdaki her use case bir sayfaya karşılık geliyor; PNG raporda okunur boyutta.

**Anlama soruları**

1. "Rent a car" ile "simulated payment" arasındaki ilişki neden `include`?
