from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from production.models import Workstation, WorkOrder, DowntimeReason
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed initial data: users, workstations, work orders, downtime reasons'

    def handle(self, *args, **options):
        self.stdout.write('Seed verileri yükleniyor...')
        self._create_downtime_reasons()
        self._create_users()
        self._create_workstations()
        self._create_work_orders()
        self.stdout.write(self.style.SUCCESS('Seed verileri başarıyla yüklendi!'))

    def _create_downtime_reasons(self):
        reasons = [
            {'code': 'ARIZA', 'name': 'Arıza', 'description': 'Makine arızası'},
            {'code': 'MALZEME_BEKLEME', 'name': 'Malzeme Bekleme', 'description': 'Malzeme tedarik bekleme'},
            {'code': 'AYAR', 'name': 'Ayar', 'description': 'Makine ayar süresi'},
            {'code': 'MOLA', 'name': 'Mola', 'description': 'Mola süresi'},
            {'code': 'KALITE_SORUNU', 'name': 'Kalite Sorunu', 'description': 'Kalite kontrol kaynaklı duruş'},
        ]
        for r in reasons:
            obj, created = DowntimeReason.objects.get_or_create(code=r['code'], defaults=r)
            status = 'oluşturuldu' if created else 'zaten var'
            self.stdout.write(f"  Duruş nedeni {status}: {r['code']}")

    def _create_users(self):
        users_data = [
            # ── ADMİN ──
            {
                'username': 'admin', 'password': 'Admin123!',
                'first_name': 'Admin', 'last_name': 'Kullanıcı',
                'email': 'admin@example.com',
                'is_staff': True, 'is_superuser': True,
                'employee_id': '1000', 'role': 'ADMIN',
                'manager_username': None,
            },
            # ── YÖNETİCİLER ──
            {
                'username': 'murat.yildiz', 'password': 'Test1234!',
                'first_name': 'Murat', 'last_name': 'Yıldız',
                'email': 'murat@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '2001', 'role': 'MANAGER',
                'manager_username': None,
            },
            {
                'username': 'selim.kaya', 'password': 'Test1234!',
                'first_name': 'Selim', 'last_name': 'Kaya',
                'email': 'selim@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '2002', 'role': 'MANAGER',
                'manager_username': None,
            },
            {
                'username': 'hakan.ozturk', 'password': 'Test1234!',
                'first_name': 'Hakan', 'last_name': 'Öztürk',
                'email': 'hakan@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '2003', 'role': 'MANAGER',
                'manager_username': None,
            },
            # ── İŞÇİLER (Yönetici: murat.yildiz) ──
            {
                'username': 'ali.demir', 'password': 'Test1234!',
                'first_name': 'Ali', 'last_name': 'Demir',
                'email': 'ali@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '3001', 'role': 'WORKER',
                'manager_username': 'murat.yildiz',
            },
            {
                'username': 'veli.celik', 'password': 'Test1234!',
                'first_name': 'Veli', 'last_name': 'Çelik',
                'email': 'veli@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '3002', 'role': 'WORKER',
                'manager_username': 'murat.yildiz',
            },
            {
                'username': 'mehmet.sahin', 'password': 'Test1234!',
                'first_name': 'Mehmet', 'last_name': 'Şahin',
                'email': 'mehmet@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '3004', 'role': 'WORKER',
                'manager_username': 'murat.yildiz',
            },
            {
                'username': 'ahmet.yilmaz', 'password': 'Test1234!',
                'first_name': 'Ahmet', 'last_name': 'Yılmaz',
                'email': 'ahmet@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '3005', 'role': 'WORKER',
                'manager_username': 'murat.yildiz',
            },
            # ── İŞÇİLER (Yönetici: selim.kaya) ──
            {
                'username': 'ayse.arslan', 'password': 'Test1234!',
                'first_name': 'Ayşe', 'last_name': 'Arslan',
                'email': 'ayse@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '3003', 'role': 'WORKER',
                'manager_username': 'selim.kaya',
            },
            {
                'username': 'fatma.kara', 'password': 'Test1234!',
                'first_name': 'Fatma', 'last_name': 'Kara',
                'email': 'fatma@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '3006', 'role': 'WORKER',
                'manager_username': 'selim.kaya',
            },
            {
                'username': 'emre.yildiz', 'password': 'Test1234!',
                'first_name': 'Emre', 'last_name': 'Yıldız',
                'email': 'emre@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '3007', 'role': 'WORKER',
                'manager_username': 'selim.kaya',
            },
            # ── İŞÇİLER (Yönetici: hakan.ozturk) ──
            {
                'username': 'burak.can', 'password': 'Test1234!',
                'first_name': 'Burak', 'last_name': 'Can',
                'email': 'burak@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '3008', 'role': 'WORKER',
                'manager_username': 'hakan.ozturk',
            },
            {
                'username': 'zeynep.dogan', 'password': 'Test1234!',
                'first_name': 'Zeynep', 'last_name': 'Doğan',
                'email': 'zeynep@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '3009', 'role': 'WORKER',
                'manager_username': 'hakan.ozturk',
            },
            {
                'username': 'kemal.tas', 'password': 'Test1234!',
                'first_name': 'Kemal', 'last_name': 'Taş',
                'email': 'kemal@example.com',
                'is_staff': False, 'is_superuser': False,
                'employee_id': '3010', 'role': 'WORKER',
                'manager_username': 'hakan.ozturk',
            },
        ]

        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'is_staff': data['is_staff'],
                    'is_superuser': data['is_superuser'],
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(f"  Kullanıcı oluşturuldu: {data['username']}")
            else:
                self.stdout.write(f"  Kullanıcı zaten var: {data['username']}")

            manager = None
            if data['manager_username']:
                manager = User.objects.get(username=data['manager_username'])

            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': data['employee_id'],
                    'role': data['role'],
                    'manager': manager,
                }
            )

    def _create_workstations(self):
        workstations = [
            {'code': 'IST-01', 'name': 'Kesim', 'description': 'Kesim iş istasyonu'},
            {'code': 'IST-02', 'name': 'Büküm', 'description': 'Büküm iş istasyonu'},
            {'code': 'IST-03', 'name': 'Kaynak', 'description': 'Kaynak iş istasyonu'},
            {'code': 'IST-04', 'name': 'Montaj', 'description': 'Montaj iş istasyonu'},
            {'code': 'IST-05', 'name': 'Boyama', 'description': 'Boyama iş istasyonu'},
        ]
        for ws in workstations:
            obj, created = Workstation.objects.get_or_create(code=ws['code'], defaults=ws)
            status = 'oluşturuldu' if created else 'zaten var'
            self.stdout.write(f"  İş istasyonu {status}: {ws['code']}")

    def _create_work_orders(self):
        murat = User.objects.get(username='murat.yildiz')
        selim = User.objects.get(username='selim.kaya')
        hakan = User.objects.get(username='hakan.ozturk')

        ali = User.objects.get(username='ali.demir')
        veli = User.objects.get(username='veli.celik')
        mehmet = User.objects.get(username='mehmet.sahin')
        ahmet = User.objects.get(username='ahmet.yilmaz')
        ayse = User.objects.get(username='ayse.arslan')
        fatma = User.objects.get(username='fatma.kara')
        emre = User.objects.get(username='emre.yildiz')
        burak = User.objects.get(username='burak.can')
        zeynep = User.objects.get(username='zeynep.dogan')
        kemal = User.objects.get(username='kemal.tas')

        ist01 = Workstation.objects.get(code='IST-01')
        ist02 = Workstation.objects.get(code='IST-02')
        ist03 = Workstation.objects.get(code='IST-03')
        ist04 = Workstation.objects.get(code='IST-04')
        ist05 = Workstation.objects.get(code='IST-05')

        today = date.today()
        orders = [
            {
                'number': 'IE-2025-001',
                'product_name': 'Metal Profil A',
                'description': 'Çelik profil kesim işi',
                'planned_quantity': 500,
                'start_date': today,
                'end_date': today + timedelta(days=30),
                'status': 'ACTIVE',
                'workstation': ist01,
                'created_by': murat,
                'workers': [ali, veli, mehmet],
            },
            {
                'number': 'IE-2025-002',
                'product_name': 'Boru Bükümü B',
                'description': 'Boru büküm operasyonu',
                'planned_quantity': 300,
                'start_date': today,
                'end_date': today + timedelta(days=20),
                'status': 'ACTIVE',
                'workstation': ist02,
                'created_by': murat,
                'workers': [ali, ahmet],
            },
            {
                'number': 'IE-2025-003',
                'product_name': 'Kaynak Montaj C',
                'description': 'Kaynak ve montaj işlemi',
                'planned_quantity': 200,
                'start_date': today,
                'end_date': today + timedelta(days=25),
                'status': 'ACTIVE',
                'workstation': ist03,
                'created_by': selim,
                'workers': [ayse, fatma, emre],
            },
            {
                'number': 'IE-2025-004',
                'product_name': 'Paslanmaz Çerçeve D',
                'description': 'Paslanmaz çelik çerçeve montajı',
                'planned_quantity': 150,
                'start_date': today,
                'end_date': today + timedelta(days=15),
                'status': 'ACTIVE',
                'workstation': ist04,
                'created_by': hakan,
                'workers': [burak, zeynep, kemal],
            },
            {
                'number': 'IE-2025-005',
                'product_name': 'Boyalı Panel E',
                'description': 'Panel boyama ve kurutma',
                'planned_quantity': 400,
                'start_date': today,
                'end_date': today + timedelta(days=35),
                'status': 'ACTIVE',
                'workstation': ist05,
                'created_by': selim,
                'workers': [fatma, emre],
            },
            {
                'number': 'IE-2025-006',
                'product_name': 'Alüminyum Profil F',
                'description': 'Alüminyum profil kesim ve şekillendirme',
                'planned_quantity': 600,
                'start_date': today,
                'end_date': today + timedelta(days=40),
                'status': 'ACTIVE',
                'workstation': ist01,
                'created_by': murat,
                'workers': [veli, mehmet, ahmet],
            },
            {
                'number': 'IE-2025-007',
                'product_name': 'Kapı Menteşesi G',
                'description': 'Menteşe kaynak ve montaj',
                'planned_quantity': 1000,
                'start_date': today,
                'end_date': today + timedelta(days=20),
                'status': 'ACTIVE',
                'workstation': ist03,
                'created_by': hakan,
                'workers': [burak, zeynep],
            },
        ]

        for order_data in orders:
            workers = order_data.pop('workers')
            order, created = WorkOrder.objects.get_or_create(
                number=order_data['number'], defaults=order_data
            )
            if created:
                order.assigned_workers.set(workers)
                self.stdout.write(f"  İş emri oluşturuldu: {order_data['number']}")
            else:
                self.stdout.write(f"  İş emri zaten var: {order_data['number']}")
