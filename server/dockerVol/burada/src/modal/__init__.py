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

