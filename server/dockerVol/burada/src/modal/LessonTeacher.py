from modal import db
from typing import Tuple, Optional, List, Self
from sqlalchemy.exc import SQLAlchemyError
import logging

from modal.messages.Messages import LessonTeacherModelMessages as LTMM

class LessonTeacher(db.Model):
    __tablename__ = 'lessons_teachers'  # Tablo adının doğru olduğundan emin olun
    __table_args__ = (
        db.Index('idx_lesson_teacher', 'lesson_uuid', 'teacher_uuid'),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_turkish_ci"
        }
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lesson_uuid = db.Column(db.String(36), db.ForeignKey('lessons.lesson_uuid'), nullable=False)
    teacher_uuid = db.Column(db.String(36), db.ForeignKey('users.uniqueID'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f"<LessonTeacher {self.id}-{self.lesson_uuid}-{self.teacher_uuid}>"
    
    @classmethod
    def create(cls, lesson_uuid: str, teacher_uuid: str) -> Tuple[bool, str, Optional["LessonTeacher"]]:
        """Assign a teacher to a lesson.
        
        Args:
            lesson_uuid (str): UUID of the lesson
            teacher_uuid (str): UUID of the teacher
            
        Returns:
            Tuple: (success: bool, message: str, lesson_teacher: Optional[LessonTeacher])
        """
        try:
            # Check if this assignment already exists
            existing = LessonTeacher.query.filter_by(
                lesson_uuid=lesson_uuid, 
                teacher_uuid=teacher_uuid
            ).first()
            
            if existing:
                return (False, LTMM.ASSIGNMENT_ALREADY_EXISTS, None)
            
            lesson_teacher = LessonTeacher(
                lesson_uuid=lesson_uuid,
                teacher_uuid=teacher_uuid
            )
            
            db.session.add(lesson_teacher)
            db.session.commit()
            
            return (True, LTMM.ASSIGNMENT_CREATED_SUCCESSFULLY, lesson_teacher)
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{LTMM.ERROR_CREATING_ASSIGNMENT} {str(e)}")
            return (False, LTMM.ERROR_CREATING_ASSIGNMENT, None)
    
    @classmethod
    def get_teachers_for_lesson(cls, lesson_uuid: str) -> List["LessonTeacher"]:
        """Get all teachers assigned to a lesson.
        
        Args:
            lesson_uuid (str): UUID of the lesson
            
        Returns:
            List[LessonTeacher]: List of teacher assignments
        """
        return cls.query.filter_by(lesson_uuid=lesson_uuid).all()
    
    @classmethod
    def get_lessons_for_teacher(cls, teacher_uuid: str) -> List["LessonTeacher"]:
        """Get all lessons assigned to a teacher.
        
        Args:
            teacher_uuid (str): UUID of the teacher
            
        Returns:
            List[LessonTeacher]: List of lesson assignments
        """
        return cls.query.filter_by(teacher_uuid=teacher_uuid).all()
    
    def delete(self) -> Tuple[bool, str]:
        """Remove a teacher-lesson assignment.
        
        Returns:
            Tuple: (success: bool, message: str)
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return (True, LTMM.ASSIGNMENT_DELETED_SUCCESSFULLY)
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{LTMM.ERROR_DELETING_ASSIGNMENT} {str(e)}")
            return (False, LTMM.ERROR_DELETING_ASSIGNMENT)