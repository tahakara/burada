from flask import Flask
from flask import request, g
from sqlalchemy import inspect

from flask_cors import CORS

from utils.GlobalUtilities import str_to_bool
from utils.LogHandlerUtilities import RequestLogHandler

from logging import debug, info, warning, error, exception

from re import match
from os import getenv
from dotenv import load_dotenv
# region Env Load
load_dotenv()
debug(f"APP_NAME: {getenv('APP_NAME')}")
debug(f"APP_VERSION: {getenv('APP_VERSION')}")
debug(f"APP_DESCRIPTION: {getenv('APP_DESCRIPTION')}")
debug(f"APP_SECRET_KEY: {getenv('APP_SECRET_KEY')}")
debug(f"APP_HOST: {getenv('APP_HOST')}")
debug(f"APP_PORT: {getenv('APP_PORT')}")
debug(f"APP_DEBUG: {getenv('APP_DEBUG')}")
debug(f"APP_LOG_LEVEL: {getenv('APP_LOG_LEVEL')}")
debug(f"DB_HOST: {getenv('DB_HOST')}")
debug(f"DB_PORT: {getenv('DB_PORT')}")
debug(f"DB_USER: {getenv('DB_USER')}")
debug(f"DB_PASSWORD: {getenv('DB_PASSWORD')}")
debug(f"DB_NAME: {getenv('DB_NAME')}")
debug(f"DB_CHARSET: {getenv('DB_CHARSET')}")
debug(f"DB_COLLATION: {getenv('DB_COLLATION')}")
debug(f"DB_DRIVER: {getenv('DB_DRIVER')}")
debug(f"REDIS_HOST: {getenv('REDIS_HOST')}")
debug(f"REDIS_PORT: {getenv('REDIS_PORT')}")
debug(f"REDIS_USER: {getenv('REDIS_USER')}")
debug(f"REDIS_PASSWORD: {getenv('REDIS_PASSWORD')}")
debug(f"REDIS_DB: {getenv('REDIS_DB')}")
debug(f"JWT_SECRET_KEY: {getenv('JWT_SECRET_KEY')}")
debug(f"JWT_ALGORITHM: {getenv('JWT_ALGORITHM')}")
debug(f"JWT_EXPIRATION_TIME: {getenv('JWT_EXPIRATION_TIME')}")
debug(f"JWT_ISSUER: {getenv('JWT_ISSUER')}")
debug(f"JWT_REFRESH_TOKEN_EXPIRATION_TIME: {getenv('JWT_REFRESH_TOKEN_EXPIRATION_TIME')}")

APP_NAME = str(getenv('APP_NAME', 'Dust'))
APP_VERSION = str(getenv('APP_VERSION', '1.0.0'))
APP_DESCRIPTION = str(getenv('APP_DESCRIPTION', 'Burada App'))
APP_SECRET_KEY = str(getenv('APP_SECRET_KEY', 'Bi de Seviyom dedi Sana yanıyom dedi. İnan ölüyom dedi vah, vah, vahİş verip tüydü ortada koydu Aşkıma kıydı vah, vah, vah'))
APP_HOST = str(getenv('APP_HOST', '127.0.0.1'))
APP_PORT = int(getenv('APP_PORT', '5261')) if match(r'^\d+$', getenv('APP_PORT', '5261')) else 5261
APP_DEBUG = str_to_bool(getenv('APP_DEBUG', 'false'))
APP_LOG_LEVEL = str(getenv('APP_LOG_LEVEL', 'debug'))

DB_HOST = str(getenv('DB_HOST', '127.0.0.1'))
DB_PORT = int(getenv('DB_PORT', '3306')) if match(r'^\d+$', getenv('DB_PORT', '3306')) else 3306
DB_USER = str(getenv('DB_USER', 'root'))
DB_PASSWORD = str(getenv('DB_PASSWORD', '1234'))
DB_NAME = str(getenv('DB_NAME', 'burada'))
DB_CHARSET = str(getenv('DB_CHARSET', 'utf8mb4'))
DB_COLLATION = str(getenv('DB_COLLATION', 'utf8mb4_general_ci'))
DB_DRIVER = str(getenv('DB_DRIVER', 'mysql'))

REDIS_HOST = str(getenv('REDIS_HOST', '127.0.0.1'))
REDIS_PORT = int(getenv('REDIS_PORT', '6379')) if match(r'^\d+$', getenv('REDIS_PORT', '6379')) else 6379
REDIS_USER = str(getenv('REDIS_USER', 'default'))
REDIS_PASSWORD = str(getenv('REDIS_PASSWORD', '1234'))
REDIS_DB = int(getenv('REDIS_DB', '0')) if match(r'^\d+$', getenv('REDIS_DB', '0')) else 0

JWT_SECRET_KEY = str(getenv('JWT_SECRET_KEY', 'SomeSecretKey'))
JWT_ALGORITHM = str(getenv('JWT_ALGORITHM', 'HS256'))
JWT_EXPIRATION_TIME = int(getenv('JWT_EXPIRATION_TIME', '3600')) if match(r'^\d+$', getenv('JWT_EXPIRATION_TIME', '3600')) else 3600
JWT_ISSUER = str(getenv('JWT_ISSUER', 'https://burada.example.com'))
JWT_REFRESH_TOKEN_EXPIRATION_TIME = int(getenv('JWT_REFRESH_TOKEN_EXPIRATION_TIME', '172800')) if match(r'^\d+$', getenv('JWT_REFRESH_TOKEN_EXPIRATION_TIME', '172800')) else 172800
DB_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
# DB_URL = f'mysql+pymysql://root:1234@mysql:3306/burada'
debug(f"DB_URL: {DB_URL}")

# endregion

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = str(getenv('APP_SECRET_KEY', 'You were the Chosen One! It was said that you would destroy the Sith, not join them! Bring balance to the Force, not leave it in darkness! You were my brother, Anakin! I loved you!'))
    app.config['TEMPLATES_AUTO_RELOAD'] = True


    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    app.url_map.strict_slashes = False

    from middleware.app_middleware import middleware_bp


    from routes.bots import bots_bp
    from routes.errors import errors_bp
    from routes.dust import dust_bp
    from routes.burada import burada_bp

    from routes.link import link_bp

    from routes.auth import auth_bp
    from routes.dashboard import dash_bp
    from routes.dashboard.attendance import attendance_bp
    from routes.api.dashboard_lessons import lessons_api
    from routes.profile import profile_bp
    app.register_blueprint(middleware_bp)

    app.register_blueprint(errors_bp)
    app.register_blueprint(bots_bp)
    app.register_blueprint(dust_bp)
    app.register_blueprint(burada_bp, url_prefix='/burada')

    app.register_blueprint(link_bp, url_prefix='/l')

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dash_bp, url_prefix='/dashboard')
    app.register_blueprint(attendance_bp)
    app.register_blueprint(lessons_api)
    app.register_blueprint(profile_bp, url_prefix='/profile')


    return app

app = create_app()

CORS(app, supports_credentials=True)
# CORS(app, resources={r"/*": {"origins": "*"}})


# region DB Config
from modal import db

db.init_app(app)
with app.app_context():
    inspector = inspect(db.engine)
    # print(inspector)
    # print(inspector.get_table_names())
    
    # Tüm modelleri import et
    from modal import User
    from modal.Lesson import Lesson
    from modal.LessonTeacher import LessonTeacher
    from modal.Student import Student
    from modal.Attenation import Attenation
    from modal.AttenationDetail import AttenationDetail
    
    db.drop_all()  # Sadece geliştirme aşamasında kullanın
    if not inspector.get_table_names():
        db.create_all()
        # Önce tabloları temizle ve yeniden oluştur
        
        from datetime import datetime
        from sqlalchemy.exc import IntegrityError
        
        # Default user oluştur
        default_user = User(
            id=1,
            username='yagcimustafa',
            email='yagci@tahakara.dev',
            phone=None,
            passwordHash='002097684c6b1b20817abbb72a341294731adfbcd00d61d0afa232b9147ae2f6',
            passwordSalt='21f10f95514bea7a543ee41f9b01842e',
            isActive=True,
            isDeleted=False,
            isEmailVerified=False,
            isPhoneVerified=False,
            lastLogin=datetime.strptime('2025-05-17 19:28:34', '%Y-%m-%d %H:%M:%S'),
            uniqueID='36db24d9-3347-11f0-8318-1aebcda1d33f',
            updatedAt=datetime.strptime('2025-05-17 19:28:34', '%Y-%m-%d %H:%M:%S'),
            createdAt=datetime.strptime('2025-05-17 17:49:00', '%Y-%m-%d %H:%M:%S')
        )
        
        # Diğer öğretmenler
        other_teachers = [
            User(
                username='alikaya',
                email='ali.kaya@tahakara.dev',
                phone='5551234567',
                passwordHash='002097684c6b1b20817abbb72a341294731adfbcd00d61d0afa232b9147ae2f6',
                passwordSalt='21f10f95514bea7a543ee41f9b01842e',
                isActive=True,
                isDeleted=False,
                isEmailVerified=True,
                isPhoneVerified=True,
                lastLogin=datetime.strptime('2025-05-18 10:15:22', '%Y-%m-%d %H:%M:%S'),
                uniqueID='44db24d9-3347-11f0-8318-1aebcda1d34f',
                updatedAt=datetime.strptime('2025-05-18 10:15:22', '%Y-%m-%d %H:%M:%S'),
                createdAt=datetime.strptime('2025-05-17 18:30:00', '%Y-%m-%d %H:%M:%S')
            ),
            User(
                username='aycademir',
                email='ayca.demir@tahakara.dev',
                phone='5551234568',
                passwordHash='002097684c6b1b20817abbb72a341294731adfbcd00d61d0afa232b9147ae2f6',
                passwordSalt='21f10f95514bea7a543ee41f9b01842e',
                isActive=True,
                isDeleted=False,
                isEmailVerified=True,
                isPhoneVerified=True,
                lastLogin=datetime.strptime('2025-05-18 11:20:45', '%Y-%m-%d %H:%M:%S'),
                uniqueID='45db24d9-3347-11f0-8318-1aebcda1d35f',
                updatedAt=datetime.strptime('2025-05-18 11:20:45', '%Y-%m-%d %H:%M:%S'),
                createdAt=datetime.strptime('2025-05-17 19:00:00', '%Y-%m-%d %H:%M:%S')
            ),
            User(
                username='mehmetyilmaz',
                email='mehmet.yilmaz@tahakara.dev',
                phone='5551234569',
                passwordHash='002097684c6b1b20817abbb72a341294731adfbcd00d61d0afa232b9147ae2f6',
                passwordSalt='21f10f95514bea7a543ee41f9b01842e',
                isActive=True,
                isDeleted=False,
                isEmailVerified=True,
                isPhoneVerified=False,
                lastLogin=datetime.strptime('2025-05-18 09:45:30', '%Y-%m-%d %H:%M:%S'),
                uniqueID='46db24d9-3347-11f0-8318-1aebcda1d36f',
                updatedAt=datetime.strptime('2025-05-18 09:45:30', '%Y-%m-%d %H:%M:%S'),
                createdAt=datetime.strptime('2025-05-17 20:15:00', '%Y-%m-%d %H:%M:%S')
            )
        ]
        
        # Öğrenci verileri
        students = [
            Student(name='Ahmet', surname='Yılmaz', student_uuid='a1db24d9-3347-11f0-8318-1aebcda10001'),
            Student(name='Ayşe', surname='Demir', student_uuid='a2db24d9-3347-11f0-8318-1aebcda10002'),
            Student(name='Mehmet', surname='Kara', student_uuid='a3db24d9-3347-11f0-8318-1aebcda10003'),
            Student(name='Zeynep', surname='Çelik', student_uuid='a4db24d9-3347-11f0-8318-1aebcda10004'),
            Student(name='Ali', surname='Öztürk', student_uuid='a5db24d9-3347-11f0-8318-1aebcda10005'),
            Student(name='Fatma', surname='Şahin', student_uuid='a6db24d9-3347-11f0-8318-1aebcda10006'),
            Student(name='Can', surname='Aydın', student_uuid='a7db24d9-3347-11f0-8318-1aebcda10007'),
            Student(name='Ece', surname='Yıldız', student_uuid='a8db24d9-3347-11f0-8318-1aebcda10008'),
            Student(name='Burak', surname='Aksoy', student_uuid='a9db24d9-3347-11f0-8318-1aebcda10009'),
            Student(name='Deniz', surname='Koç', student_uuid='a0db24d9-3347-11f0-8318-1aebcda10010')
        ]
        
        # Veritabanına kaydet ve hata kontrolü yap
        try:
            # Kullanıcıları ekle
            db.session.add(default_user)
            for teacher in other_teachers:
                db.session.add(teacher)
            db.session.commit()
            print(f"Kullanıcılar oluşturuldu: yagcimustafa, alikaya, aycademir, mehmetyilmaz")
            
            # Öğrencileri ekle
            for student in students:
                db.session.add(student)
            db.session.commit()
            print(f"10 öğrenci başarıyla eklendi")
            
            # Dersleri oluştur
            lessons = [
                Lesson(name="Yazılım Mühendisliği", lesson_uuid="48db24d9-3347-11f0-8318-1aebcda1d44f"),
                Lesson(name="Veritabanı Sistemleri", lesson_uuid="49db24d9-3347-11f0-8318-1aebcda1d45f"),
                Lesson(name="Yapay Zeka", lesson_uuid="50db24d9-3347-11f0-8318-1aebcda1d46f"),
                Lesson(name="Web Programlama", lesson_uuid="51db24d9-3347-11f0-8318-1aebcda1d47f"),
                Lesson(name="Mobil Uygulama Geliştirme", lesson_uuid="52db24d9-3347-11f0-8318-1aebcda1d48f"),
                Lesson(name="Siber Güvenlik", lesson_uuid="53db24d9-3347-11f0-8318-1aebcda1d49f")
            ]
            
            for lesson in lessons:
                db.session.add(lesson)
            db.session.commit()
            print(f"6 ders başarıyla oluşturuldu")
            
            # Öğretmen-ders ilişkilerini oluştur
            lesson_teachers = [
                LessonTeacher(lesson_uuid="48db24d9-3347-11f0-8318-1aebcda1d44f", teacher_uuid="36db24d9-3347-11f0-8318-1aebcda1d33f"),  # Yazılım Müh - yagcimustafa
                LessonTeacher(lesson_uuid="49db24d9-3347-11f0-8318-1aebcda1d45f", teacher_uuid="44db24d9-3347-11f0-8318-1aebcda1d34f"),  # Veritabanı - alikaya
                LessonTeacher(lesson_uuid="50db24d9-3347-11f0-8318-1aebcda1d46f", teacher_uuid="45db24d9-3347-11f0-8318-1aebcda1d35f"),  # Yapay Zeka - aycademir
                LessonTeacher(lesson_uuid="51db24d9-3347-11f0-8318-1aebcda1d47f", teacher_uuid="46db24d9-3347-11f0-8318-1aebcda1d36f"),  # Web Prog - mehmetyilmaz
                LessonTeacher(lesson_uuid="52db24d9-3347-11f0-8318-1aebcda1d48f", teacher_uuid="36db24d9-3347-11f0-8318-1aebcda1d33f"),  # Mobil - yagcimustafa
                LessonTeacher(lesson_uuid="53db24d9-3347-11f0-8318-1aebcda1d49f", teacher_uuid="44db24d9-3347-11f0-8318-1aebcda1d34f")   # Siber - alikaya
            ]
            
            for lesson_teacher in lesson_teachers:
                db.session.add(lesson_teacher)
            db.session.commit()
            print(f"Öğretmen-ders ilişkileri başarıyla kuruldu")
            
            # Yoklama oturumları ekle
            attendance_sessions = [
                Attenation(
                    id=1,
                    lesson_uuid='48db24d9-3347-11f0-8318-1aebcda1d44f', 
                    teacher_uuid='36db24d9-3347-11f0-8318-1aebcda1d33f', 
                    is_active=False,  # 0 değerine karşılık gelecek string value
                    session_name='Yazılım Mühendisliği - 15 Mayıs Oturumu', 
                    created_at=datetime.strptime('2025-05-15 09:00:00', '%Y-%m-%d %H:%M:%S'),
                    closed_at=datetime.strptime('2025-05-15 11:30:00', '%Y-%m-%d %H:%M:%S')
                ),
                Attenation(
                    id=2,
                    lesson_uuid='49db24d9-3347-11f0-8318-1aebcda1d45f', 
                    teacher_uuid='44db24d9-3347-11f0-8318-1aebcda1d34f', 
                    is_active=False,
                    session_name='Veritabanı Sistemleri - 16 Mayıs Oturumu', 
                    created_at=datetime.strptime('2025-05-16 13:00:00', '%Y-%m-%d %H:%M:%S'),
                    closed_at=datetime.strptime('2025-05-16 15:30:00', '%Y-%m-%d %H:%M:%S')
                ),
                Attenation(
                    id=3,
                    lesson_uuid='50db24d9-3347-11f0-8318-1aebcda1d46f', 
                    teacher_uuid='45db24d9-3347-11f0-8318-1aebcda1d35f', 
                    is_active=True,
                    session_name='Yapay Zeka - 17 Mayıs Oturumu', 
                    created_at=datetime.strptime('2025-05-17 10:00:00', '%Y-%m-%d %H:%M:%S'),
                    closed_at=datetime.strptime('2025-05-17 12:30:00', '%Y-%m-%d %H:%M:%S')
                ),
                Attenation(
                    id=4,
                    lesson_uuid='51db24d9-3347-11f0-8318-1aebcda1d47f', 
                    teacher_uuid='46db24d9-3347-11f0-8318-1aebcda1d36f', 
                    is_active=True,  # 1 değerine karşılık gelecek string value
                    session_name='Web Programlama - 18 Mayıs Oturumu', 
                    created_at=datetime.strptime('2025-05-18 14:00:00', '%Y-%m-%d %H:%M:%S'),
                    closed_at=None
                ),
                Attenation(
                    id=5,
                    lesson_uuid='52db24d9-3347-11f0-8318-1aebcda1d48f', 
                    teacher_uuid='36db24d9-3347-11f0-8318-1aebcda1d33f', 
                    is_active=True,
                    session_name='Mobil Uygulama Geliştirme - 18 Mayıs Oturumu', 
                    created_at=datetime.strptime('2025-05-18 16:00:00', '%Y-%m-%d %H:%M:%S'),
                    closed_at=None
                )
            ]
            
            for attendance in attendance_sessions:
                db.session.add(attendance)
            db.session.commit()
            print(f"5 yoklama oturumu başarıyla eklendi")

            # Add attendance details for sessions
            attendance_details = [
                AttenationDetail(attenation_id=1, student_uuid='a1db24d9-3347-11f0-8318-1aebcda10001', card_id='CARD001', timestamp=datetime.strptime('2025-05-15 09:05:23', '%Y-%m-%d %H:%M:%S')),
                AttenationDetail(attenation_id=1, student_uuid='a2db24d9-3347-11f0-8318-1aebcda10002', card_id='CARD002', timestamp=datetime.strptime('2025-05-15 09:06:45', '%Y-%m-%d %H:%M:%S')),
                AttenationDetail(attenation_id=1, student_uuid='a3db24d9-3347-11f0-8318-1aebcda10003', card_id='CARD003', timestamp=datetime.strptime('2025-05-15 09:08:12', '%Y-%m-%d %H:%M:%S')),
                AttenationDetail(attenation_id=1, student_uuid='a4db24d9-3347-11f0-8318-1aebcda10004', card_id='CARD004', timestamp=datetime.strptime('2025-05-15 09:10:05', '%Y-%m-%d %H:%M:%S')),
                AttenationDetail(attenation_id=1, student_uuid='a5db24d9-3347-11f0-8318-1aebcda10005', card_id='CARD005', timestamp=datetime.strptime('2025-05-15 09:12:33', '%Y-%m-%d %H:%M:%S')),
                
                AttenationDetail(attenation_id=2, student_uuid='a2db24d9-3347-11f0-8318-1aebcda10002', card_id='CARD002', timestamp=datetime.strptime('2025-05-16 13:04:18', '%Y-%m-%d %H:%M:%S')),
                AttenationDetail(attenation_id=2, student_uuid='a3db24d9-3347-11f0-8318-1aebcda10003', card_id='CARD003', timestamp=datetime.strptime('2025-05-16 13:05:37', '%Y-%m-%d %H:%M:%S')),
                AttenationDetail(attenation_id=2, student_uuid='a6db24d9-3347-11f0-8318-1aebcda10006', card_id='CARD006', timestamp=datetime.strptime('2025-05-16 13:07:22', '%Y-%m-%d %H:%M:%S')),
                AttenationDetail(attenation_id=2, student_uuid='a7db24d9-3347-11f0-8318-1aebcda10007', card_id='CARD007', timestamp=datetime.strptime('2025-05-16 13:10:45', '%Y-%m-%d %H:%M:%S')),
                AttenationDetail(attenation_id=2, student_uuid='a8db24d9-3347-11f0-8318-1aebcda10008', card_id='CARD008', timestamp=datetime.strptime('2025-05-16 13:12:19', '%Y-%m-%d %H:%M:%S')),
            ]

            for detail in attendance_details:
                db.session.add(detail)
            db.session.commit()
            print(f"{len(attendance_details)} yoklama detayı başarıyla eklendi")
            
        except IntegrityError as e:
            db.session.rollback()
            print(f"Veri oluşturulurken hata: {str(e)}")
        except Exception as e:
            db.session.rollback()
            print(f"Beklenmeyen hata: {str(e)}")
# endregion

if __name__ == '__main__':
    from functools import partial
    if not APP_DEBUG:
        app.config['ENV'] = 'development'
        app.config['DEBUG'] = True
    app.run(debug=APP_DEBUG, host=APP_HOST, port=APP_PORT, request_handler=partial(RequestLogHandler))