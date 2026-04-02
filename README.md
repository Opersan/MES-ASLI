# Üretim İzleme Sistemi (MES)

Fabrika ortamında iş emirleri, işçilik kayıtları, duruş takibi ve aylık raporlama işlemlerini yöneten Django tabanlı üretim izleme (MES) uygulaması.

## Özellikler

- **Kimlik Doğrulama** — Django auth ile kullanıcı girişi / çıkışı
- **Rol Tabanlı Erişim** — Admin, Yönetici, İşçi rolleri; her rol sadece yetkili olduğu ekranları görür
- **Üretim Ekranı** — Kart tabanlı gerçek zamanlı üretim takibi (canlı timer, ilerleme çubuğu)
- **İş İstasyonu Yönetimi** — İstasyon ekleme, düzenleme, listeleme
- **İş Emri Yönetimi** — İş emri CRUD, işçi atama, durum takibi
- **İşçilik Kaydı** — Üretim başlat/bitir, üretilen adet girişi, kısmi/tam tamamlama
- **Duruş Yönetimi** — Duruş başlat/bitir, neden seçimi, süre hesaplama
- **Aylık Raporlama** — İşçi, istasyon, iş emri ve duruş nedeni bazlı raporlar + CSV dışa aktarım
- **Django Admin** — Tüm modeller admin panelinde yönetilebilir
- **Seed Data** — Tek komutla örnek kullanıcı, istasyon, iş emri ve duruş nedeni oluşturma

## Kullanılan Teknolojiler

| Teknoloji | Versiyon |
|-----------|----------|
| Python | 3.12+ |
| Django | 5.2 |
| Veritabanı | SQLite |
| Ön Yüz | Bootstrap 5, Bootstrap Icons (CDN) |
| Sunucu | Django dev server / PythonAnywhere |

## Proje Yapısı

```
MES-ASLI/
├── config/                 # Django proje ayarları
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/               # Kimlik doğrulama, profil, roller
│   ├── models.py           # Profile modeli (rol, sicil no, yönetici)
│   ├── views.py            # Login / logout
│   ├── decorators.py       # @role_required dekoratörü
│   └── management/commands/seed_data.py
├── production/             # Üretim modülü
│   ├── models.py           # Workstation, WorkOrder, LaborEntry, DowntimeRecord
│   ├── views.py            # Dashboard, üretim ekranı, CRUD
│   ├── forms.py            # WorkstationForm, WorkOrderForm
│   └── templates/production/
├── reports/                # Raporlama modülü
│   ├── views.py            # Aylık rapor + CSV
│   └── templates/reports/
├── templates/              # Paylaşılan şablonlar
│   └── base.html
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Kurulum (Local)

### 1. Projeyi klonlayın

```bash
git clone https://github.com/KULLANICI/MES-ASLI.git
cd MES-ASLI
```

### 2. Sanal ortam oluşturun

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

### 4. Veritabanını oluşturun

```bash
python manage.py migrate
```

### 5. Örnek verileri yükleyin

```bash
python manage.py seed_data
```

Bu komut idempotent olarak çalışır — tekrar çalıştırıldığında duplicate oluşturmaz.

### 6. Sunucuyu başlatın

```bash
python manage.py runserver
```

Tarayıcıda açın: **http://127.0.0.1:8000**

## Demo Kullanıcılar

### Admin

| Kullanıcı | Şifre | Rol | Sicil No |
|-----------|-------|-----|----------|
| `admin` | `Admin123!` | Admin | 1000 |

### Yöneticiler

| Kullanıcı | Şifre | Rol | Sicil No |
|-----------|-------|-----|----------|
| `murat.yildiz` | `Test1234!` | Yönetici | 2001 |
| `selim.kaya` | `Test1234!` | Yönetici | 2002 |
| `hakan.ozturk` | `Test1234!` | Yönetici | 2003 |

### İşçiler

| Kullanıcı | Şifre | Sicil No | Yönetici |
|-----------|-------|----------|----------|
| `ali.demir` | `Test1234!` | 3001 | Murat Yıldız |
| `veli.celik` | `Test1234!` | 3002 | Murat Yıldız |
| `ayse.arslan` | `Test1234!` | 3003 | Selim Kaya |
| `mehmet.sahin` | `Test1234!` | 3004 | Murat Yıldız |
| `ahmet.yilmaz` | `Test1234!` | 3005 | Murat Yıldız |
| `fatma.kara` | `Test1234!` | 3006 | Selim Kaya |
| `emre.yildiz` | `Test1234!` | 3007 | Selim Kaya |
| `burak.can` | `Test1234!` | 3008 | Hakan Öztürk |
| `zeynep.dogan` | `Test1234!` | 3009 | Hakan Öztürk |
| `kemal.tas` | `Test1234!` | 3010 | Hakan Öztürk |

## Rol ve Yetki Özeti

| Özellik | Admin | Yönetici | İşçi |
|---------|:-----:|:--------:|:----:|
| Dashboard | ✅ | ✅ | ❌ |
| Üretim Ekranı (izleme) | ✅ | ✅ | — |
| Üretim Ekranı (çalışma) | — | — | ✅ |
| İş İstasyonu Yönetimi | ✅ | ✅ | ❌ |
| İş Emri Yönetimi | ✅ | ✅ | ❌ |
| İşçilik Kayıtları | ✅ | ✅ | ❌ |
| Duruş Kayıtları | ✅ | ✅ | ❌ |
| Aylık Rapor + CSV | ✅ | ✅ | ❌ |
| Django Admin | ✅ | ❌ | ❌ |

- **İşçiler** sadece Üretim Ekranı'nı görür; üretim başlatır/bitirir, duruş açar/kapatır.
- **Yöneticiler** kendi ekibine ait verileri görür ve yönetir.
- **Admin** tüm verilere erişir.

## Ortam Değişkenleri

| Değişken | Varsayılan | Açıklama |
|----------|-----------|----------|
| `DJANGO_SECRET_KEY` | Dev key (geliştirme için) | Production'da mutlaka değiştirin |
| `DJANGO_DEBUG` | `True` | Production'da `False` yapın |
| `DJANGO_ALLOWED_HOSTS` | `*` | Virgülle ayrılmış host listesi |

Local geliştirmede hiçbir ortam değişkeni tanımlamanıza gerek yoktur — varsayılanlar çalışır.

## PythonAnywhere Deploy

### 1. GitHub'dan kodları çekin

PythonAnywhere Bash konsolunda:

```bash
git clone https://github.com/KULLANICI/MES-ASLI.git
cd MES-ASLI
```

### 2. Sanal ortam oluşturun

```bash
mkvirtualenv --python=python3.12 mes-venv
pip install -r requirements.txt
```

### 3. WSGI yapılandırması

PythonAnywhere Web sekmesinde **WSGI configuration file** bağlantısına tıklayın ve içeriği şu şekilde değiştirin:

```python
import os
import sys

# Proje dizinini ayarlayın (KULLANICI yerine kendi PythonAnywhere kullanıcı adınızı yazın)
project_home = '/home/KULLANICI/MES-ASLI'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DJANGO_SECRET_KEY'] = 'buraya-guclu-bir-anahtar-yazin'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'kullanici.pythonanywhere.com'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 4. Veritabanı ve statik dosyalar

PythonAnywhere Bash konsolunda:

```bash
cd ~/MES-ASLI
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput
```

### 5. Static files ayarı

PythonAnywhere Web sekmesinde **Static files** bölümüne ekleyin:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/KULLANICI/MES-ASLI/staticfiles` |

### 6. Web uygulamasını yeniden başlatın

Web sekmesinde yeşil **Reload** butonuna tıklayın.

## GitHub'a Yükleme

```bash
cd MES-ASLI
git init
git add .
git commit -m "Initial commit: Üretim İzleme Sistemi (MES)"
git branch -M main
git remote add origin https://github.com/KULLANICI/MES-ASLI.git
git push -u origin main
```

> **Not**: `KULLANICI` yerine kendi GitHub kullanıcı adınızı yazın.

## Varsayımlar ve Sınırlamalar

- **Veritabanı**: SQLite kullanılmaktadır; yüksek trafikli ortamlar için PostgreSQL'e geçiş önerilir.
- **Statik dosyalar**: Bootstrap ve ikonlar CDN üzerinden yüklenir; çevrimdışı ortamlarda çalışmaz.
- **Tek aktif işçilik**: Bir işçi aynı anda yalnızca bir iş emrinde çalışabilir.
- **Zaman dilimi**: Tüm zamanlar `Europe/Istanbul` olarak kaydedilir.
- **Seed data**: Geliştirme ve demo amaçlıdır; production'da gerçek verilerle değiştirilmelidir.
- **HTTPS**: PythonAnywhere ücretsiz planlarda HTTPS otomatik sağlanır.
