from modal import db
from typing import Tuple, Optional, List, Self, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime, timedelta
from sqlalchemy import func

from modal.messages.Messages import AttenationModelMessages as AMM

class Attenation(db.Model):
    __tablename__ = 'attenations'
    __table_args__ = (
        db.Index('idx_attenation_lesson', 'lesson_uuid'),
        db.Index('idx_attenation_teacher', 'teacher_uuid'),
        db.Index('idx_attenation_date', 'created_at'),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_turkish_ci"
        }
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lesson_uuid = db.Column(db.String(36), db.ForeignKey('lessons.lesson_uuid'), nullable=False)
    teacher_uuid = db.Column(db.String(36), db.ForeignKey('users.uniqueID'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    session_name = db.Column(db.String(255), nullable=True)  # Örn: "1. Hafta Dersi"
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    closed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Attenation {self.id}-{self.lesson_uuid}>"
    
    @classmethod
    def create(cls, lesson_uuid: str, teacher_uuid: str, session_name: str = None) -> Tuple[bool, str, Optional["Attenation"]]:
        """Create a new attendance session.
        
        Args:
            lesson_uuid (str): UUID of the lesson
            teacher_uuid (str): UUID of the teacher
            session_name (str, optional): Optional name for the session
            
        Returns:
            Tuple: (success: bool, message: str, attenation: Optional[Attenation])
        """
        try:
            # Aynı ders için aktif yoklama var mı?
            active_session = Attenation.query.filter_by(
                lesson_uuid=lesson_uuid,
                is_active=True
            ).first()
            
            if active_session:
                return (False, AMM.ACTIVE_SESSION_EXISTS, None)
            
            # Öğretmenin bu dersi verip vermediğini kontrol et
            from modal.LessonTeacher import LessonTeacher
            teacher_lesson = LessonTeacher.query.filter_by(
                lesson_uuid=lesson_uuid,
                teacher_uuid=teacher_uuid
            ).first()
            
            if not teacher_lesson:
                return (False, AMM.NOT_AUTHORIZED_FOR_LESSON, None)
            
            # Yeni yoklama oturumu oluştur
            attenation = Attenation(
                lesson_uuid=lesson_uuid,
                teacher_uuid=teacher_uuid,
                is_active=True,
                session_name=session_name
            )
            
            db.session.add(attenation)
            db.session.commit()
            
            return (True, AMM.SESSION_CREATED_SUCCESSFULLY, attenation)
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{AMM.ERROR_CREATING_SESSION} {str(e)}")
            return (False, AMM.ERROR_CREATING_SESSION, None)
    
    def close(self) -> Tuple[bool, str, Optional[Self]]:
        """Close an attendance session.
        
        Returns:
            Tuple: (success: bool, message: str, attenation: Optional[Attenation])
        """
        if not self.is_active:
            return (False, AMM.SESSION_ALREADY_CLOSED, None)
            
        self.is_active = False
        self.closed_at = datetime.now()
        
        try:
            db.session.commit()
            return (True, AMM.SESSION_CLOSED_SUCCESSFULLY, self)
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{AMM.ERROR_CLOSING_SESSION} {str(e)}")
            return (False, AMM.ERROR_CLOSING_SESSION, None)
    
    @classmethod
    def get_active_session(cls, lesson_uuid: str) -> Optional["Attenation"]:
        """Get the active attendance session for a lesson.
        
        Args:
            lesson_uuid (str): UUID of the lesson
            
        Returns:
            Optional[Attenation]: Attenation object if found, None otherwise
        """
        return cls.query.filter_by(lesson_uuid=lesson_uuid, is_active=True).first()
    
    @classmethod
    def get_lesson_attendance_report(cls, lesson_uuid: str) -> Dict[str, Any]:
        """Bir ders için tüm yoklama oturumlarının raporunu oluşturur.
        
        Args:
            lesson_uuid (str): Dersin UUID'si
            
        Returns:
            Dict[str, Any]: Yoklama raporu
        """
        try:
            from modal.Lesson import Lesson
            from modal.Student import Student
            from modal.AttenationDetail import AttenationDetail
            
            # Ders bilgilerini al
            lesson = Lesson.query.filter_by(lesson_uuid=lesson_uuid).first()
            if not lesson:
                return {"error": "Ders bulunamadı"}
            
            # Bu ders için tüm yoklama oturumlarını al
            sessions = cls.query.filter_by(lesson_uuid=lesson_uuid).order_by(cls.created_at.desc()).all()
            
            # Hiç yoklama yoksa boş rapor döndür
            if not sessions:
                return {
                    "lesson_info": {
                        "lesson_uuid": lesson.lesson_uuid,
                        "name": lesson.name
                    },
                    "attendance_summary": {
                        "total_sessions": 0,
                        "students_count": 0
                    },
                    "sessions": [],
                    "students": []
                }
            
            # İlgili oturum ID'lerini topla
            session_ids = [session.id for session in sessions]
            
            # Tüm oturumlar için katılan öğrencileri bul
            student_uuids_query = db.session.query(AttenationDetail.student_uuid).filter(
                AttenationDetail.attenation_id.in_(session_ids)
            ).distinct().all()
            
            student_uuids = [uuid[0] for uuid in student_uuids_query]
            
            # Tüm öğrencileri getir
            students = Student.query.filter(Student.student_uuid.in_(student_uuids)).all()
            students_dict = {student.student_uuid: {"name": student.name, "surname": student.surname} for student in students}
            
            # Her oturum için detaylı bilgileri topla
            sessions_data = []
            for session in sessions:
                # Bu oturum için katılan öğrencileri bul
                attendance_records = AttenationDetail.query.filter_by(attenation_id=session.id).all()
                
                # Katılan öğrenci UUID'lerini topla
                attended_students = [record.student_uuid for record in attendance_records]
                
                # Oturum bilgilerini ekle
                sessions_data.append({
                    "id": session.id,
                    "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "closed_at": session.closed_at.strftime("%Y-%m-%d %H:%M:%S") if session.closed_at else None,
                    "is_active": session.is_active,
                    "session_name": session.session_name,
                    "student_count": len(attended_students),
                    "students": attended_students
                })
            
            # Her öğrenci için katıldığı oturumları bul
            students_attendance = []
            for student_uuid in student_uuids:
                # Bu öğrenci için tüm yoklama kayıtlarını al
                attendance_records = AttenationDetail.query.filter(
                    AttenationDetail.student_uuid == student_uuid,
                    AttenationDetail.attenation_id.in_(session_ids)
                ).all()
                
                # Öğrencinin katıldığı oturum ID'lerini bul
                attended_session_ids = [record.attenation_id for record in attendance_records]
                
                # Katılım oranını hesapla
                attendance_rate = round((len(attended_session_ids) / len(sessions)) * 100, 1)
                
                students_attendance.append({
                    "student_uuid": student_uuid,
                    "name": students_dict.get(student_uuid, {}).get("name", "Bilinmeyen"),
                    "surname": students_dict.get(student_uuid, {}).get("surname", "Öğrenci"),
                    "attended_sessions": attended_session_ids,
                    "attendance_rate": attendance_rate,
                    "total_attended": len(attended_session_ids),
                    "total_sessions": len(sessions)
                })
            
            return {
                "lesson_info": {
                    "lesson_uuid": lesson.lesson_uuid,
                    "name": lesson.name
                },
                "attendance_summary": {
                    "total_sessions": len(sessions),
                    "active_sessions": len([s for s in sessions if s.is_active]),
                    "students_count": len(student_uuids)
                },
                "sessions": sessions_data,
                "students": students_attendance
            }
            
        except Exception as e:
            logging.error(f"Yoklama raporu oluşturulurken hata: {str(e)}")
            return {"error": f"Yoklama raporu oluşturulurken hata: {str(e)}"}
    
    @classmethod
    def get_teacher_lessons_report(cls, teacher_uuid: str) -> List[Dict[str, Any]]:
        """Bir öğretmenin tüm derslerinin yoklama özetini getirir.
        
        Args:
            teacher_uuid (str): Öğretmenin UUID'si
            
        Returns:
            List[Dict[str, Any]]: Her ders için özet yoklama raporu
        """
        try:
            from modal.Lesson import Lesson
            from modal.LessonTeacher import LessonTeacher
            from modal.AttenationDetail import AttenationDetail
            
            # Öğretmenin derslerini bul
            teacher_lessons = LessonTeacher.query.filter_by(teacher_uuid=teacher_uuid).all()
            lesson_uuids = [record.lesson_uuid for record in teacher_lessons]
            
            # Ders bilgilerini al
            lessons = Lesson.query.filter(Lesson.lesson_uuid.in_(lesson_uuids)).all()
            lessons_dict = {lesson.lesson_uuid: lesson.name for lesson in lessons}
            
            reports = []
            
            for lesson_uuid in lesson_uuids:
                # Bu ders için tüm yoklama oturumlarını al
                sessions = cls.query.filter_by(
                    lesson_uuid=lesson_uuid,
                    teacher_uuid=teacher_uuid
                ).all()
                
                # Tamamlanan ve aktif oturumları say
                active_sessions = [s for s in sessions if s.is_active]
                completed_sessions = [s for s in sessions if not s.is_active]
                
                # Yoklama yapılan tek oturum varsa bu oturuma katılan öğrenci sayısını bul
                total_student_count = 0
                if sessions:
                    session_ids = [s.id for s in sessions]
                    total_student_count = db.session.query(func.count(db.distinct(AttenationDetail.student_uuid))).filter(
                        AttenationDetail.attenation_id.in_(session_ids)
                    ).scalar() or 0
                
                reports.append({
                    "lesson_uuid": lesson_uuid,
                    "lesson_name": lessons_dict.get(lesson_uuid, "Bilinmeyen Ders"),
                    "active_sessions": len(active_sessions),
                    "completed_sessions": len(completed_sessions),
                    "total_sessions": len(sessions),
                    "last_session": sessions[-1].created_at.strftime("%Y-%m-%d %H:%M:%S") if sessions else None,
                    "total_students": total_student_count
                })
            
            return reports
            
        except Exception as e:
            logging.error(f"Öğretmen dersleri raporu oluşturulurken hata: {str(e)}")
            return [{"error": f"Öğretmen dersleri raporu oluşturulurken hata: {str(e)}"}]

    @classmethod
    def add_student_to_active_session(cls, lesson_uuid: str, student_uuid: str, card_id: str = None) -> Tuple[bool, str, Optional["AttenationDetail"]]:
        """Aktif yoklama oturumuna öğrenci ekler.
        
        Args:
            lesson_uuid (str): Dersin UUID'si
            student_uuid (str): Öğrencinin UUID'si
            card_id (str, optional): RFID kart ID'si
            
        Returns:
            Tuple: (success: bool, message: str, detail: Optional[AttenationDetail])
        """
        try:
            # Aktif yoklama oturumunu bul
            active_session = cls.get_active_session(lesson_uuid)
            if not active_session:
                return (False, AMM.NO_ACTIVE_SESSION, None)
            
            # Öğrenciyi bu oturuma ekle
            from modal.AttenationDetail import AttenationDetail
            return AttenationDetail.create(
                attenation_id=active_session.id,
                student_uuid=student_uuid,
                card_id=card_id
            )
            
        except Exception as e:
            logging.error(f"Öğrenci yoklamaya eklenirken hata: {str(e)}")
            return (False, str(e), None)