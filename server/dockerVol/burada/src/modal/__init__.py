from flask import Request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import text
from typing import Type, Any
from logging import error
from datetime import datetime
import uuid

db = SQLAlchemy()

from modal.RequestInfo import RequestInfo
from modal.User import User
from modal.Lesson import Lesson
from modal.LessonTeacher import LessonTeacher
from modal.Student import Student
from modal.Attenation import Attenation
from modal.AttenationDetail import AttenationDetail


def add_and_commit(db=db, obj: SQLAlchemy = None) -> None:
    """Add an object to the session and commit it."""
    if obj is None:
        return None
    db.session.add(obj)
    db.session.commit()

def save_request_info(db=db, request: Request = None, dust: str=None, dust_device: str=None) -> None:
    """Save request information to the database."""
    if request is None:
        return None
    request_info = RequestInfo.create_request_info(request, dust, dust_device)
    add_and_commit(db, request_info)

def select_uuid(db=db) -> str:
    """Select a UUID from the database."""
    result = db.session.execute(text("SELECT UUID()")).fetchone()
    return result[0]

def get_teacher_lessons(teacher_uuid, db=db) -> list:
    """Get all lessons assigned to a teacher using SQLAlchemy ORM"""
    try:
        # Query lessons for the teacher
        lessons = (
            db.session.query(Lesson)
            .join(LessonTeacher, Lesson.lesson_uuid == LessonTeacher.lesson_uuid)
            .filter(LessonTeacher.teacher_uuid == teacher_uuid)
            .order_by(Lesson.name)
            .all()
        )

        result = []
        for lesson in lessons:
            # Active sessions
            active_sessions = (
                db.session.query(Attenation)
                .filter(Attenation.lesson_uuid == lesson.lesson_uuid, Attenation.is_active == True)
                .all()
            )
            active_session_uuid = active_sessions[0].lesson_uuid if active_sessions else None

            # Last session date
            last_session = (
                db.session.query(Attenation)
                .filter(Attenation.lesson_uuid == lesson.lesson_uuid)
                .order_by(Attenation.created_at.desc())
                .first()
            )
            last_session_str = last_session.created_at.strftime('%d.%m.%Y %H:%M') if last_session else None

            # Total sessions
            total_sessions = (
                db.session.query(Attenation)
                .filter(Attenation.lesson_uuid == lesson.lesson_uuid)
                .count()
            )
            print(active_sessions)
            result.append({
                "lesson_uuid": lesson.lesson_uuid,
                "lesson_name": lesson.name,
                "active_session_id": active_sessions[0].id if active_sessions else None,
                "active_sessions": len(active_sessions),
                "active_session_uuid": active_session_uuid,
                "last_session": last_session_str,
                "total_sessions": total_sessions
            })
        return result
    except Exception as e:
        error(f"Error fetching teacher lessons: {str(e)}")
        return []

def get_lesson_detail(lesson_uuid, teacher_uuid, db=db):
    """Get lesson details for a specific lesson"""
    try:
        # Check if lesson exists and belongs to this teacher
        lesson = (
            db.session.query(Lesson)
            .join(LessonTeacher, Lesson.lesson_uuid == LessonTeacher.lesson_uuid)
            .filter(Lesson.lesson_uuid == lesson_uuid, LessonTeacher.teacher_uuid == teacher_uuid)
            .first()
        )
        
        if not lesson:
            return {
                "success": False,
                "message": "Bu ders bulunamadı veya erişim izniniz yok."
            }
        
        # Get attendance sessions for the lesson
        sessions = (
            db.session.query(Attenation)
            .filter(Attenation.lesson_uuid == lesson_uuid)
            .order_by(Attenation.id.desc())
            .all()
        )
        active_session = False
        session_list = []
        for session in sessions:
            if session.is_active:
                active_session = {
                    "id": session.id,
                    "session_name": session.session_name,
                    "status": session.is_active,
                    "created_at": session.created_at.strftime('%d.%m.%Y %H:%M'),
                    "closed_at": session.closed_at.strftime('%d.%m.%Y %H:%M') if session.closed_at else None,
                    "student_count": db.session.query(AttenationDetail).filter(AttenationDetail.attenation_id == session.id).count(),
                }
            session_list.append({
                "id": session.id,
                "session_name": session.session_name,
                "status": session.is_active,
                "created_at": session.created_at.strftime('%d.%m.%Y %H:%M'),
                "closed_at": session.closed_at.strftime('%d.%m.%Y %H:%M') if session.closed_at else None,
                "student_count": db.session.query(AttenationDetail).filter(AttenationDetail.attenation_id == session.id).count(),
            })
        
        return {
            "success": True,
            "data": {
                "lesson_uuid": lesson.lesson_uuid,
                "lesson_name": lesson.name,
                "sessions": session_list,
                "active_session": active_session ,
                "total_sessions": len(sessions),
                "total_students": None
            }
        }
    except Exception as e:
        error(f"Error fetching lesson details: {str(e)}")
        return {
            "success": False,
            "message": f"Ders detayları yüklenirken bir hata oluştu: {str(e)}"
        }

def create_attendance_session(lesson_uuid, teacher_uuid, session_name="", db=db):
    """Create a new attendance session for a lesson"""
    try:
        # Check if lesson exists and belongs to this teacher
        lesson = (
            db.session.query(Lesson)
            .join(LessonTeacher, Lesson.lesson_uuid == LessonTeacher.lesson_uuid)
            .filter(Lesson.lesson_uuid == lesson_uuid, LessonTeacher.teacher_uuid == teacher_uuid)
            .first()
        )
        
        if not lesson:
            return {
                "success": False,
                "message": "Bu ders bulunamadı veya erişim izniniz yok."
            }
        
        # Check if there's already an active session
        active_sessions = (
            db.session.query(Attenation)
            .filter(Attenation.lesson_uuid == lesson_uuid, Attenation.is_active == True)
            .count()
        )
        
        if active_sessions > 0:
            return {
                "success": False,
                "message": "Bu ders için zaten aktif bir yoklama oturumu var."
            }
        
        # Create new attendance session
        now = datetime.now()
        session_uuid = str(uuid.uuid4())
        
        new_session = Attenation(
            teacher_uuid=teacher_uuid,
            lesson_uuid=lesson_uuid,
            session_name=session_name,
            is_active=True
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        return {
            "success": True,
            "message": "Yoklama oturumu başarıyla oluşturuldu.",
            "data": {
                "session_id": new_session.id,
                "session_uuid": session_uuid
            }
        }
    except Exception as e:
        db.session.rollback()
        error(f"Error creating attendance session: {str(e)}")
        return {
            "success": False,
            "message": f"Yoklama oturumu oluşturulurken bir hata oluştu: {str(e)}"
        }

def close_attendance_session(attendance_uuid, teacher_uuid, db=db):
    """Close an active attendance session"""
    try:
        # Check if session exists and belongs to this teacher's lesson
        session = (
            db.session.query(Attenation)
            .join(Lesson, Attenation.lesson_uuid == Lesson.lesson_uuid)
            .join(LessonTeacher, Lesson.lesson_uuid == LessonTeacher.lesson_uuid)
            .filter(
                Attenation.id == attendance_uuid,
                Attenation.is_active == True,
                LessonTeacher.teacher_uuid == teacher_uuid
            )
            .first()
        )
        
        if not session:
            return {
                "success": False,
                "message": "Bu yoklama oturumu bulunamadı, zaten kapatılmış veya erişim izniniz yok."
            }
        
        # Close the attendance session
        session.is_active = False
        session.closed_at = datetime.now()
        session.closed_by = teacher_uuid
        
        db.session.commit()
        
        return {
            "success": True,
            "message": "Yoklama oturumu başarıyla kapatıldı."
        }
    except Exception as e:
        db.session.rollback()
        error(f"Error closing attendance session: {str(e)}")
        return {
            "success": False,
            "message": f"Yoklama oturumu kapatılırken bir hata oluştu: {str(e)}"
        }

def get_attendance_students_list(attendance_id, teacher_uuid, db=db):
    """Get list of students who attended a specific attendance session"""
    try:
        # First, verify that the attendance session belongs to a course taught by this teacher
        attendance = (
            db.session.query(Attenation)
            .join(Lesson, Attenation.lesson_uuid == Lesson.lesson_uuid)
            .join(LessonTeacher, Lesson.lesson_uuid == LessonTeacher.lesson_uuid)
            .filter(
                Attenation.id == attendance_id,
                LessonTeacher.teacher_uuid == teacher_uuid
            )
            .first()
        )
        
        if not attendance:
            return {
                "success": False,
                "message": "Bu yoklama oturumu bulunamadı veya erişim izniniz yok."
            }
        
        # Get the attendance details (students who attended)
        attendance_details = (
            db.session.query(AttenationDetail, Student)
            .join(Student, AttenationDetail.student_uuid == Student.student_uuid)
            .filter(AttenationDetail.attenation_id == attendance_id)
            .order_by(AttenationDetail.id.desc())
            .all()
        )
        
        students_list = []
        for detail, student in attendance_details:
            students_list.append({
                "student_uuid": student.student_uuid,
                "name": student.name,
                "surname": student.surname,
                "timestamp": detail.timestamp.strftime('%d.%m.%Y %H:%M:%S')
            })
        
        return {
            "success": True,
            "student_count": len(students_list),
            "attendance_id": attendance_id,
            "lesson_uuid": attendance.lesson_uuid,
            "lesson_name": attendance.session_name,
            "teacher_uuid": attendance.teacher_uuid,
            "data": students_list
        }
    except Exception as e:
        error(f"Error fetching attendance students: {str(e)}")
        return {
            "success": False,
            "message": f"Yoklama katılımcıları yüklenirken bir hata oluştu: {str(e)}"
        }
    
def generate_lesson_single_attendance_report(lesson_uuid, teacher_uuid, attendance_id, db=db):
    """Generate a PDF report for a single attendance session"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        import os
        from flask import current_app
        
        # Önce yoklama oturumunun bu derse ve öğretmene ait olduğunu kontrol et
        attendance = (
            db.session.query(Attenation)
            .join(Lesson, Attenation.lesson_uuid == Lesson.lesson_uuid)
            .join(LessonTeacher, Lesson.lesson_uuid == LessonTeacher.lesson_uuid)
            .filter(
                Attenation.id == attendance_id,
                Lesson.lesson_uuid == lesson_uuid,
                LessonTeacher.teacher_uuid == teacher_uuid
            )
            .first()
        )
        
        if not attendance:
            return {
                "success": False,
                "message": "Yoklama oturumu bulunamadi veya erisim izniniz yok."
            }
        
        # Ders bilgilerini al
        lesson = (
            db.session.query(Lesson)
            .filter(Lesson.lesson_uuid == lesson_uuid)
            .first()
        )
        
        # Yoklamaya katılan öğrencileri al
        students_data = (
            db.session.query(AttenationDetail, Student)
            .join(Student, AttenationDetail.student_uuid == Student.student_uuid)
            .filter(AttenationDetail.attenation_id == attendance_id)
            .order_by(AttenationDetail.timestamp.desc())
            .all()
        )
        
        # Dosya adını belirle
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        attendance_name = attendance.session_name if attendance.session_name else f"Oturum_{attendance.id}"
        attendance_name = attendance_name.replace(' ', '_').replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ç', 'c').replace('ö', 'o')
        filename = f"yoklama_{attendance_name}_{timestamp}.pdf"
        
        # PDF'i kaydetmek için dizin
        static_dir = os.path.join(current_app.root_path, 'static', 'reports')
        os.makedirs(static_dir, exist_ok=True)
        filepath = os.path.join(static_dir, filename)
        
        # PDF dokümanı oluştur
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        
        # Stiller
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Cell stili
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=normal_style,
            wordWrap='CJK',
            fontSize=9
        )
        
        # Türkçe karakterleri temizle
        def clean_text(text):
            if not isinstance(text, str):
                text = str(text)
            replacements = {
                'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G', 
                'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S', 
                'ç': 'c', 'Ç': 'C', 'ö': 'o', 'Ö': 'O'
            }
            for old, new in replacements.items():
                text = text.replace(old, new)
            return text
        
        # Başlık ekle
        elements.append(Paragraph(f"Yoklama Oturumu Raporu: {clean_text(attendance.session_name or 'Belirtilmemis')}", title_style))
        elements.append(Spacer(1, 20))
        
        # Ders ve yoklama bilgileri ekle
        elements.append(Paragraph("Ders ve Yoklama Bilgileri", subtitle_style))
        elements.append(Spacer(1, 10))
        
        info_data = [
            ["Ders Adi:", clean_text(lesson.name)],
            ["Ders UUID:", lesson.lesson_uuid],
            ["Yoklama ID:", str(attendance.id)],
            ["Oturum Adi:", clean_text(attendance.session_name or "Belirtilmemis")],
            ["Baslangic Zamani:", attendance.created_at.strftime('%d.%m.%Y %H:%M')],
            ["Bitis Zamani:", attendance.closed_at.strftime('%d.%m.%Y %H:%M') if attendance.closed_at else "Aktif"],
            ["Durum:", "Aktif" if attendance.is_active else "Kapali"],
            ["Katilimci Sayisi:", str(len(students_data))],
            ["Rapor Tarihi:", datetime.now().strftime('%d.%m.%Y %H:%M')]
        ]
        
        # Her bir hücre için Paragraph kullan
        for i in range(len(info_data)):
            for j in range(len(info_data[i])):
                info_data[i][j] = Paragraph(str(info_data[i][j]), cell_style)
        
        info_table = Table(info_data, colWidths=[120, 350])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Öğrenci listesi
        elements.append(Paragraph("Katilan Ogrenciler", subtitle_style))
        elements.append(Spacer(1, 10))
        
        if students_data:
            students_header = [
                Paragraph("Ogrenci Adi Soyadi", cell_style),
                Paragraph("Ogrenci ID", cell_style),
                Paragraph("Katilim Zamani", cell_style)
            ]
            students_rows = [students_header]
            
            for detail, student in students_data:
                # Öğrenci numarası veya UUID
                student_id = student.student_number if hasattr(student, 'student_number') and student.student_number else student.student_uuid
                
                student_row = [
                    Paragraph(clean_text(f"{student.name} {student.surname}"), cell_style),
                    Paragraph(str(student_id), cell_style),
                    Paragraph(detail.timestamp.strftime('%d.%m.%Y %H:%M:%S'), cell_style)
                ]
                students_rows.append(student_row)
            
            students_table = Table(students_rows, colWidths=[180, 180, 120])
            students_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # Katılım zamanı ortala
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            elements.append(students_table)
        else:
            elements.append(Paragraph("Bu oturuma henuz hicbir ogrenci katilmamis.", normal_style))
        
        # PDF'i oluştur
        doc.build(elements)
        
        # URL ve dosya bilgilerini döndür
        pdf_url = f"/static/reports/{filename}"
        
        return {
            "success": True,
            "filename": filename,
            "pdf_url": pdf_url,
            "title": f"Yoklama Raporu - {clean_text(attendance.session_name or f'Oturum {attendance.id}')}"
        }
    except Exception as e:
        error(f"Error generating single attendance report: {str(e)}")
        return {
            "success": False,
            "message": f"PDF rapor olusturulurken bir hata olustu: {str(e)}"
        }

def get_attendance_session(attendance_id, teacher_uuid, db=db):
    """Get attendance session information with permission check"""
    try:
        # Find the attendance session with permission check
        attendance = (
            db.session.query(Attenation)
            .join(Lesson, Attenation.lesson_uuid == Lesson.lesson_uuid)
            .join(LessonTeacher, Lesson.lesson_uuid == LessonTeacher.lesson_uuid)
            .filter(
                Attenation.id == attendance_id,
                LessonTeacher.teacher_uuid == teacher_uuid
            )
            .first()
        )
        
        if not attendance:
            return {
                "success": False,
                "message": "Yoklama oturumu bulunamadı veya erişim izniniz yok."
            }
        
        return {
            "success": True,
            "data": attendance
        }
    
    except Exception as e:
        error(f"Error fetching attendance session: {str(e)}")
        return {
            "success": False,
            "message": f"Yoklama oturumu yüklenirken bir hata oluştu: {str(e)}"
        }
        
def generate_lesson_pdf_report(lesson_uuid, teacher_uuid, sessions, db=db):
    """Generate a PDF report for a lesson with attendance statistics"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        import os
        from flask import current_app
        
        # Get lesson details
        lesson = (
            db.session.query(Lesson)
            .filter(Lesson.lesson_uuid == lesson_uuid)
            .first()
        )
        
        if not lesson:
            return {
                "success": False,
                "message": "Ders bulunamadi."
            }
        
        # Create a unique filename - Türkçe karakterleri ingilizce harflerle değiştir
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        lesson_name_safe = lesson.name.replace(' ', '_')
        lesson_name_safe = lesson_name_safe.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ç', 'c').replace('ö', 'o')
        filename = f"yoklama_raporu_{lesson_name_safe}_{timestamp}.pdf"
        
        # Set the path to save the PDF
        static_dir = os.path.join(current_app.root_path, 'static', 'reports')
        os.makedirs(static_dir, exist_ok=True)
        filepath = os.path.join(static_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Özel paragraf stili oluştur - word wrap için
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=normal_style,
            wordWrap='CJK',
            fontSize=9
        )
        
        # Replace problematic characters in text
        def clean_text(text):
            if not isinstance(text, str):
                text = str(text)
            # Replace Turkish special characters with ASCII equivalents
            replacements = {
                'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G', 
                'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S', 
                'ç': 'c', 'Ç': 'C', 'ö': 'o', 'Ö': 'O'
            }
            for old, new in replacements.items():
                text = text.replace(old, new)
            return text
        
        # Add title
        elements.append(Paragraph(f"Yoklama Raporu: {clean_text(lesson.name)}", title_style))
        elements.append(Spacer(1, 20))
        
        # Add lesson information
        elements.append(Paragraph("Ders Bilgileri", subtitle_style))
        elements.append(Spacer(1, 10))
        
        lesson_data = [
            ["Ders Adi:", clean_text(lesson.name)],
            ["Ders UUID:", lesson.lesson_uuid],
            ["Toplam Oturum Sayisi:", str(len(sessions))],
            ["Rapor Tarihi:", datetime.now().strftime('%d.%m.%Y %H:%M')]
        ]
        
        # Her bir hücre için Paragraph kullan
        for i in range(len(lesson_data)):
            for j in range(len(lesson_data[i])):
                lesson_data[i][j] = Paragraph(str(lesson_data[i][j]), cell_style)
        
        lesson_table = Table(lesson_data, colWidths=[120, 350])
        lesson_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Dikey ortalama
        ]))
        
        elements.append(lesson_table)
        elements.append(Spacer(1, 20))
        
        # Add sessions information
        elements.append(Paragraph("Yoklama Oturumlari", subtitle_style))
        elements.append(Spacer(1, 10))
        
        # Table header
        sessions_data = [["ID", "Oturum Adi", "Baslangic", "Bitis", "Durum", "Katilim"]]
        
        # Add session data
        for session in sessions:
            # Get student count for this session
            student_count = db.session.query(AttenationDetail).filter(
                AttenationDetail.attenation_id == session["id"]
            ).count()
            
            session_status = "Aktif" if session["status"] else "Kapali"
            
            # Her bir hücre normal metin yerine Paragraph olacak
            session_row = [
                Paragraph(str(session["id"]), cell_style),
                Paragraph(clean_text(session["session_name"] or "Belirtilmemis"), cell_style),
                Paragraph(session["created_at"], cell_style),
                Paragraph(session["closed_at"] or "Aktif", cell_style),
                Paragraph(session_status, cell_style),
                Paragraph(str(student_count), cell_style)
            ]
            sessions_data.append(session_row)
        
        # Oturum isimlerinin çok uzun olması durumunda 2. sütunun genişliğini arttır
        session_table = Table(sessions_data, colWidths=[40, 150, 80, 80, 50, 50])
        session_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # ID centered
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),  # Status centered
            ('ALIGN', (5, 0), (5, -1), 'CENTER'),  # Student count centered
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Dikey ortalama
        ]))
        
        elements.append(session_table)
        elements.append(Spacer(1, 20))
        
        # Add detailed statistics
        elements.append(Paragraph("Katilim Istatistikleri", subtitle_style))
        elements.append(Spacer(1, 10))
        
        # Get all students in the course
        all_students = (
            db.session.query(Student)
            .join(Attenation, Attenation.lesson_uuid == lesson_uuid)
            .join(AttenationDetail, AttenationDetail.attenation_id == Attenation.id)
            .filter(AttenationDetail.student_uuid == Student.student_uuid)
            .distinct()
            .all()
        )
        
        if all_students:
            # Create table for students and their attendance
            student_header = [
                Paragraph("Ogrenci Adi Soyadi", cell_style),
                Paragraph("Ogrenci ID", cell_style),
                Paragraph("Katilim", cell_style),
                Paragraph("Oran", cell_style)
            ]
            student_data = [student_header]
            
            for student in all_students:
                # Count sessions this student attended
                attended_sessions = db.session.query(AttenationDetail) \
                    .join(Attenation, Attenation.id == AttenationDetail.attenation_id) \
                    .filter(
                        Attenation.lesson_uuid == lesson_uuid,
                        AttenationDetail.student_uuid == student.student_uuid
                    ).count()
                
                # Calculate attendance rate
                attendance_rate = (attended_sessions / len(sessions)) * 100 if sessions else 0
                
                # Kullan öğrenci numarası varsa, yoksa UUID
                student_id = student.student_number if hasattr(student, 'student_number') and student.student_number else student.student_uuid
                
                student_row = [
                    Paragraph(clean_text(f"{student.name} {student.surname}"), cell_style),
                    Paragraph(str(student_id), cell_style),
                    Paragraph(f"{attended_sessions} / {len(sessions)}", cell_style),
                    Paragraph(f"%{attendance_rate:.1f}", cell_style)
                ]
                student_data.append(student_row)
            
            # Değiştirilen kolon genişlikleri - Katılım sütunu daraltıldı, Oran sütunu genişletildi
            student_table = Table(student_data, colWidths=[150, 200, 50, 50])  # Katılım 60->50, Oran 40->50
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('ALIGN', (2, 0), (3, -1), 'CENTER'),  # Katılım ve oran centered
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Dikey ortalama
            ]))
            
            elements.append(student_table)
        else:
            elements.append(Paragraph("Bu derse henuz hicbir ogrenci katilmamis.", normal_style))
        
        # Build the PDF
        doc.build(elements)
        
        # Get the URL to access the file
        pdf_url = f"/static/reports/{filename}"
        
        return {
            "success": True,
            "filename": filename,
            "pdf_url": pdf_url,
            "title": f"Yoklama Raporu - {clean_text(lesson.name)}"
        }
    except Exception as e:
        error(f"Error generating PDF report: {str(e)}")
        return {
            "success": False,
            "message": f"PDF rapor olusturulurken bir hata olustu: {str(e)}"
        }