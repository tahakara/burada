from flask import Blueprint, jsonify, request, current_app, g
from modal import (get_teacher_lessons, get_lesson_detail, create_attendance_session, 
                  close_attendance_session, get_attendance_students_list, 
                  generate_lesson_pdf_report, generate_lesson_single_attendance_report,
                  get_attendance_session)
from auth.authmiddleware import AuthMiddleware

AuthMiddleware = AuthMiddleware()
# Create blueprint
lessons_api = Blueprint('lessons_api', __name__)

@lessons_api.route('/api/dashboard/lessons', methods=['GET'])
@AuthMiddleware.login_required
def get_teacher_lessons_route():
    """Get all lessons for the logged-in teacher"""
    try:
        # Get current user ID
        teacher_uuid = g.user['user_uuid']
        if not teacher_uuid:
            return jsonify({
                "success": False,
                "message": "Kullanıcı kimliği bulunamadı."
            }), 401
        
        # Use the model function to get lessons
        lessons = get_teacher_lessons(teacher_uuid)
        
        return jsonify({
            "success": True,
            "data": lessons
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching lessons: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Dersler yüklenirken bir hata oluştu."
        }), 500
    
@lessons_api.route('/api/dashboard/lessons/detail/<lesson_uuid>', methods=['GET'])  
@AuthMiddleware.login_required
def get_lesson_detail_route(lesson_uuid):
    """Get details of a specific lesson"""
    try:
        # Get current user ID
        teacher_uuid = g.user['user_uuid']
        if not teacher_uuid:
            return jsonify({
                "success": False,
                "message": "Kullanıcı kimliği bulunamadı."
            }), 401
        
        # Use the model function to get lesson details
        lesson_details = get_lesson_detail(lesson_uuid, teacher_uuid)
        
        if not lesson_details["success"]:
            return jsonify(lesson_details), 404
            
        return jsonify(lesson_details)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching lesson details: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Ders detayları yüklenirken bir hata oluştu."
        }), 500

@lessons_api.route('/api/dashboard/attendance/create', methods=['POST'])
@AuthMiddleware.login_required
def create_attendance_session_route():
    """Create a new attendance session for a lesson"""
    try:
        data = request.json
        lesson_uuid = data.get('lesson_uuid')
        session_name = data.get('session_name', '')
        
        if not lesson_uuid:
            return jsonify({
                "success": False,
                "message": "Ders UUID'si gereklidir."
            }), 400
        
        # Use the model function to create attendance session
        result = create_attendance_session(
            lesson_uuid=lesson_uuid,
            teacher_uuid=g.user['user_uuid'],
            session_name=session_name
        )
        
        if not result["success"]:
            return jsonify(result), 400
            
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error creating attendance session: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Yoklama oturumu oluşturulurken bir hata oluştu."
        }), 500

@lessons_api.route('/api/dashboard/attendance/close/<int:attendance_uuid>', methods=['POST'])
@AuthMiddleware.login_required
def close_attendance_session_route(attendance_uuid):
    """Close an active attendance session"""
    try:
        # Use the model function to close attendance session
        result = close_attendance_session(
            attendance_uuid=attendance_uuid,
            teacher_uuid=g.user['user_uuid']
        )
        
        if not result["success"]:
            return jsonify(result), 404
            
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error closing attendance session: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Yoklama oturumu kapatılırken bir hata oluştu."
        }), 500

@lessons_api.route('/api/dashboard/attendance/students/<int:attendance_id>', methods=['GET'])
@AuthMiddleware.login_required
def get_attendance_students(attendance_id):
    """Get students who attended a specific attendance session"""
    try:
        # Get current user ID
        teacher_uuid = g.user['user_uuid']
        if not teacher_uuid:
            return jsonify({
                "success": False,
                "message": "Kullanıcı kimliği bulunamadı."
            }), 401
        
        # Use a model function to get students
        students = get_attendance_students_list(attendance_id, teacher_uuid)
        
        if not students["success"]:
            return jsonify(students), 404
            
        return jsonify(students)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching attendance students: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Yoklama katılımcıları yüklenirken bir hata oluştu."
        }), 500

@lessons_api.route('/api/dashboard/lessons/report/<lesson_uuid>', methods=['GET'])
@AuthMiddleware.login_required
def generate_lesson_report(lesson_uuid):
    """Generate a PDF report for a specific lesson"""
    try:
        # Get current user ID
        teacher_uuid = g.user['user_uuid']
        if not teacher_uuid:
            return jsonify({
                "success": False,
                "message": "Kullanıcı kimliği bulunamadı."
            }), 401
        
        # Get lesson details and attendance data
        lesson_data = get_lesson_detail(lesson_uuid, teacher_uuid)
        
        if not lesson_data["success"]:
            return jsonify(lesson_data), 404
        
        # Get all attendance sessions for this lesson
        all_sessions = lesson_data["data"]["sessions"]
        
        # Create PDF using a helper function (defined in modal/__init__.py)
        pdf_result = generate_lesson_pdf_report(lesson_uuid, teacher_uuid, all_sessions)
        
        if not pdf_result["success"]:
            return jsonify(pdf_result), 500
            
        # Return the PDF file URL
        return jsonify({
            "success": True,
            "message": "Rapor başarıyla oluşturuldu.",
            "data": {
                "pdf_url": pdf_result["pdf_url"],
                "filename": pdf_result["filename"]
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating lesson report: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Rapor oluşturulurken bir hata oluştu."
        }), 500

@lessons_api.route('/api/dashboard/attendance/report/<int:attendance_id>', methods=['GET'])
@AuthMiddleware.login_required
def generate_attendance_report(attendance_id):
    """Generate a PDF report for a specific attendance session"""
    try:
        # Get current user ID
        teacher_uuid = g.user['user_uuid']
        if not teacher_uuid:
            return jsonify({
                "success": False,
                "message": "Kullanıcı kimliği bulunamadı."
            }), 401
        
        # Use model function to get attendance session with permission check
        attendance_result = get_attendance_session(attendance_id, teacher_uuid)
        
        if not attendance_result["success"]:
            return jsonify(attendance_result), 404
        
        attendance = attendance_result["data"]
        
        # Generate PDF using the helper function
        lesson_uuid = attendance.lesson_uuid
        pdf_result = generate_lesson_single_attendance_report(lesson_uuid, teacher_uuid, attendance_id)
        
        if not pdf_result["success"]:
            return jsonify(pdf_result), 500
            
        # Return the PDF file URL
        return jsonify({
            "success": True,
            "message": "Yoklama raporu başarıyla oluşturuldu.",
            "data": {
                "pdf_url": pdf_result["pdf_url"],
                "filename": pdf_result["filename"],
                "title": pdf_result["title"]
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating attendance report: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Rapor oluşturulurken bir hata oluştu."
        }), 500