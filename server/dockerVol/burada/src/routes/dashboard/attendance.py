from flask import Blueprint, jsonify, request, g
from auth.authmiddleware import AuthMiddleware
from modal.Attenation import Attenation
from modal.Lesson import Lesson

attendance_bp = Blueprint('attendance', __name__)
auth_middleware = AuthMiddleware()

@attendance_bp.route('/lessons', methods=['GET'])
@auth_middleware.login_required
def get_teacher_lessons():
    """Öğretmenin derslerini listeler."""
    teacher_uuid = g.user.uniqueID
    academic_term = request.args.get('term')
    
    reports = Attenation.get_teacher_lessons_report(teacher_uuid, academic_term)
    return jsonify({"success": True, "data": reports})

@attendance_bp.route('/report/<lesson_uuid>', methods=['GET'])
@auth_middleware.login_required
def get_lesson_attendance_report(lesson_uuid):
    """Bir ders için yoklama raporunu getirir."""
    teacher_uuid = g.user.uniqueID
    academic_term = request.args.get('term')
    
    # Dersin bu öğretmene ait olup olmadığını kontrol et
    from modal.LessonTeacher import LessonTeacher
    lesson_teacher = LessonTeacher.query.filter_by(
        lesson_uuid=lesson_uuid,
        teacher_uuid=teacher_uuid
    ).first()
    
    if not lesson_teacher:
        return jsonify({"success": False, "message": "Bu dersi görüntüleme yetkiniz yok."}), 403
    
    report = Attenation.get_lesson_attendance_report(lesson_uuid, academic_term)
    return jsonify({"success": True, "data": report})

@attendance_bp.route('/create', methods=['POST'])
@auth_middleware.login_required
def create_attendance_session():
    """Yeni bir yoklama oturumu başlatır."""
    data = request.get_json()
    teacher_uuid = g.user.uniqueID
    
    lesson_uuid = data.get('lesson_uuid')
    week_number = int(data.get('week_number', 1))
    academic_term = data.get('academic_term')
    
    if not all([lesson_uuid, academic_term]):
        return jsonify({"success": False, "message": "Eksik parametreler."}), 400
    
    # Dersin bu öğretmene ait olup olmadığını kontrol et
    from modal.LessonTeacher import LessonTeacher
    lesson_teacher = LessonTeacher.query.filter_by(
        lesson_uuid=lesson_uuid,
        teacher_uuid=teacher_uuid
    ).first()
    
    if not lesson_teacher:
        return jsonify({"success": False, "message": "Bu ders için yoklama başlatma yetkiniz yok."}), 403
    
    status, message, attenation = Attenation.create(
        lesson_uuid=lesson_uuid,
        teacher_uuid=teacher_uuid,
        week_number=week_number,
        academic_term=academic_term
    )
    
    return jsonify({
        "success": status,
        "message": message,
        "data": attenation.id if attenation else None
    }), 200 if status else 400

@attendance_bp.route('/close/<int:attenation_id>', methods=['POST'])
@auth_middleware.login_required
def close_attendance_session(attenation_id):
    """Bir yoklama oturumunu kapatır."""
    teacher_uuid = g.user.uniqueID
    
    attenation = Attenation.query.get(attenation_id)
    if not attenation:
        return jsonify({"success": False, "message": "Yoklama oturumu bulunamadı."}), 404
    
    if attenation.teacher_uuid != teacher_uuid:
        return jsonify({"success": False, "message": "Bu oturumu kapatma yetkiniz yok."}), 403
    
    status, message, updated_attenation = attenation.close()
    
    return jsonify({
        "success": status,
        "message": message
    }), 200 if status else 400