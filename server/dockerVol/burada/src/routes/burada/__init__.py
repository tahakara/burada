from flask import Blueprint
from flask import request, g
from flask import current_app 
from flask import jsonify, make_response, send_from_directory, render_template
from modal import db
from modal.Attenation import Attenation
from modal.AttenationDetail import AttenationDetail
from modal.User import User
from modal.Student import Student
from modal.Lesson import Lesson  # Ders bilgisi için Lesson modelini ekleyelim
from modal.LessonTeacher import LessonTeacher  # Öğretmen-ders ilişkisi için
from datetime import datetime
import json
import re


burada_bp = Blueprint("bot", __name__, url_prefix='/burada')

ALL_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE', 'CONNECT']

@burada_bp.route('/', methods=['POST', 'GET'])
def burada():
    """
    IoT cihazından gelen kart okuma isteklerini işler.
    
    Senaryolar:
    - Öğretmen kartı okutulduğunda yoklama açılır (100)
    - Yoklama açıkken öğrenci kartları okutulduğunda onaylanır (200)
    - Öğretmen tekrar kart okuttuğunda yoklama kapanır (000)
    - Yoklama açık değilken veya geçersiz kartlar için hata (400)
    """
    try:
        if request.method == 'POST':
            # IoT cihazından gelen veriyi al
            data = request.get_json()
            if not data:
                return make_response(jsonify({'status': 400, 'message': 'Veri formatı geçersiz'}), 400)
            
            # 24, 25, 26. sektörlerden isim, soyisim bilgisini ve ders ID'sini oluştur
            sector24 = data.get('id24', '')
            sector25 = data.get('id25', '')
            sector26 = data.get('id26', '')
            lesson_uuid = data.get('lesson_uuid', '')
            
            # Nokta karakterlerini kaldır
            sector24 = sector24.replace('.', '')
            sector25 = sector25.replace('.', '')
            sector26 = sector26.replace('.', '')
            
            # İsim ve soyisim oluştur (24 ve 25. sektör)
            full_name = f"{sector24} {sector25}%"
            full_name = full_name.strip()
            
            # Aktif yoklama oturumu var mı kontrol et
            active_session = Attenation.query.filter_by(is_active=True, lesson_uuid=lesson_uuid).first()

            # Kullanıcıyı bul (öğretmen veya öğrenci)
            teacher = User.query.filter(
                db.func.concat(User.username).like(str.lower(f"{sector25}{sector24}"))
            ).first()
            
            student = None
            if not teacher:
                # Öğrenci olarak ara
                student = Student.query.filter(
                    # db.func.concat(Student.name, ' ', Student.surname).ilike(f"TAHA KARA")
                    db.func.concat(Student.name, ' ', Student.surname).like(full_name)
                ).first()
            
            # Öğretmen kartı ve yoklama açma/kapama durumu
            if teacher:
                if not active_session:
                    # Ders ID'sini doğrula
                    if lesson_uuid:
                        # Öğretmenin verdiği bir ders mi kontrol et
                        lesson_teacher = LessonTeacher.query.filter_by(
                            lesson_uuid=lesson_uuid,
                            teacher_uuid=teacher.uniqueID
                        ).first()
                        
                        if not lesson_teacher:
                            return make_response(jsonify({
                                'status': 400, 
                                'message': 'Bu ders için yoklama açma yetkiniz yok'
                            }), 200)
                        
                        # Dersi bul
                        lesson = Lesson.query.filter_by(lesson_uuid=lesson_uuid).first()
                        if not lesson:
                            return make_response(jsonify({
                                'status': 400, 
                                'message': 'Belirtilen ders bulunamadı'
                            }), 200)
                        
                        session_name = f"{lesson.name} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                    else:
                        # Ders ID'si yoksa genel bir yoklama oturumu oluştur
                        session_name = f"Yoklama Oturumu - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                    
                    # Yoklama yok, öğretmen yeni yoklama açıyor
                    new_session = Attenation(
                        lesson_uuid=lesson_uuid if lesson_uuid else None,
                        teacher_uuid=teacher.uniqueID,
                        is_active=True,
                        session_name=session_name,
                        created_at=datetime.now(),
                        closed_at=None
                    )
                    db.session.add(new_session)
                    db.session.commit()
                    current_app.logger.info(f"Yoklama açıldı: {teacher.name} {teacher.surname}, Ders: {lesson_uuid}")
                    return make_response(jsonify({
                        'status': 100, 
                        'message': 'Yoklama açıldı',
                        'session_name': session_name,
                        'teacher': f"{teacher.name} {teacher.surname}"
                    }), 200)
                else:
                    # Yoklama var, öğretmenin yoklamayı kapatma yetkisi var mı kontrol et
                    if active_session.teacher_uuid != teacher.uniqueID:
                        return make_response(jsonify({
                            'status': 400, 
                            'message': 'Bu yoklamayı yalnızca açan öğretmen kapatabilir'
                        }), 200)
                    
                    # Yoklamayı kapat
                    active_session.is_active = False
                    active_session.closed_at = datetime.now()
                    db.session.commit()
                    current_app.logger.info(f"Yoklama kapatıldı: {teacher.name} {teacher.surname}")
                    return make_response(jsonify({
                        'status': 000, 
                        'message': 'Yoklama kapatıldı',
                        'teacher': f"{teacher.name} {teacher.surname}",
                        'session_name': active_session.session_name
                    }), 200)
            
            # Öğrenci kartı
            elif student:
                if active_session:
                    # Dersi kontrol et (eğer ders belirtilmişse)
                    if active_session.lesson_uuid and lesson_uuid and active_session.lesson_uuid != lesson_uuid:
                        return make_response(jsonify({
                            'status': 400, 
                            'message': 'Bu öğrenci bu dersin yoklamasına dahil edilemez'
                        }), 200)
                    
                    # Öğrenci yoklamaya kaydediliyor
                    # Daha önce bu yoklamaya kaydedilmiş mi kontrol et
                    existing_record = AttenationDetail.query.filter_by(
                        attenation_id=active_session.id, 
                        student_uuid=student.student_uuid
                    ).first()
                    
                    if existing_record:
                        return make_response(jsonify({
                            'status': 400, 
                            'message': 'Bu öğrenci zaten yoklamada kayıtlı',
                            'student': f"{student.name} {student.surname}"
                        }), 200)
                    
                    # Yeni yoklama kaydı oluştur
                    new_detail = AttenationDetail(
                        attenation_id=active_session.id,
                        student_uuid=student.student_uuid,
                        card_id=sector26 if sector26 else "NOCARD",
                        timestamp=datetime.now()
                    )
                    db.session.add(new_detail)
                    db.session.commit()
                    current_app.logger.info(f"Öğrenci yoklamaya eklendi: {student.name} {student.surname}")
                    return make_response(jsonify({
                        'status': 200, 
                        'message': 'Yoklama kaydedildi',
                        'student': f"{student.name} {student.surname}",
                        'session_name': active_session.session_name
                    }), 200)
                else:
                    # Aktif yoklama yok
                    return make_response(jsonify({
                        'status': 400, 
                        'message': 'Aktif yoklama bulunmamaktadır',
                        'student': f"{student.name} {student.surname}"
                    }), 200)
            else:
                # Kullanıcı bulunamadı
                return make_response(jsonify({
                    'status': 400, 
                    'message': 'Kullanıcı bulunamadı',
                    'data': {'full_name': full_name}
                }), 200)
                
        # GET isteği için basit bir yanıt
        return make_response(jsonify({'status': 200, 'message': 'Burada IoT servisi aktif'}), 200)
        
    except Exception as e:
        current_app.logger.error(f"Yoklama işleminde hata: {str(e)}")
        return make_response(jsonify({
            'status': 400, 
            'message': f'İşlem sırasında hata oluştu: {str(e)}'
        }), 200)