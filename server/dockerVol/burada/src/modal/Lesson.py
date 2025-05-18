from modal import db
from typing import Tuple, Optional, List, Self
from sqlalchemy.exc import SQLAlchemyError
import logging

from modal.messages.Messages import LessonModelMessages as LMM

class Lesson(db.Model):
    __tablename__ = 'lessons'
    __table_args__ = (
        db.Index('idx_lesson_name', 'name'),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_turkish_ci"
        }
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    lesson_uuid = db.Column(db.String(36), unique=True, default=db.func.uuid())
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f"<Lesson {self.id}-{self.lesson_uuid}-{self.name}>"
    
    @classmethod
    def create(cls, name: str) -> Tuple[bool, str, Optional["Lesson"]]:
        """Create a new lesson in the database.
        
        Args:
            name (str): Name of the lesson
            
        Returns:
            Tuple: (success: bool, message: str, lesson: Optional[Lesson])
        """
        try:
            # Check if a lesson with the same name already exists
            existing_lesson = Lesson.query.filter_by(name=name).first()
            if existing_lesson:
                return (False, LMM.LESSON_ALREADY_EXISTS, None)
            
            lesson = Lesson(
                name=name,
                lesson_uuid=db.func.uuid()
            )
            
            db.session.add(lesson)
            db.session.commit()
            
            return (True, LMM.LESSON_CREATED_SUCCESSFULLY, lesson)
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{LMM.ERROR_CREATING_LESSON} {str(e)}")
            return (False, LMM.ERROR_CREATING_LESSON, None)
    
    @classmethod
    def get_by_uuid(cls, lesson_uuid: str) -> Optional["Lesson"]:
        """Get a lesson by UUID.
        
        Args:
            lesson_uuid (str): UUID of the lesson
            
        Returns:
            Optional[Lesson]: Lesson object if found, None otherwise
        """
        return cls.query.filter_by(lesson_uuid=lesson_uuid).first()
    
    @classmethod
    def get_all(cls) -> List["Lesson"]:
        """Get all lessons.
        
        Returns:
            List[Lesson]: List of all lessons
        """
        return cls.query.all()
    
    def update(self, name: str = None) -> Tuple[bool, str, Optional[Self]]:
        """Update a lesson in the database.
        
        Args:
            name (str, optional): New name for the lesson
            
        Returns:
            Tuple: (success: bool, message: str, lesson: Optional[Lesson])
        """
        if name:
            # Check if another lesson with the same name exists
            existing_lesson = Lesson.query.filter(
                (Lesson.name == name) & (Lesson.id != self.id)
            ).first()
            
            if existing_lesson:
                return (False, LMM.LESSON_NAME_ALREADY_EXISTS, None)
            
            self.name = name
        
        try:
            db.session.commit()
            return (True, LMM.LESSON_UPDATED_SUCCESSFULLY, self)
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{LMM.ERROR_UPDATING_LESSON} {str(e)}")
            return (False, LMM.ERROR_UPDATING_LESSON, None)
    
    def delete(self) -> Tuple[bool, str]:
        """Delete a lesson from the database.
        
        Returns:
            Tuple: (success: bool, message: str)
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return (True, LMM.LESSON_DELETED_SUCCESSFULLY)
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{LMM.ERROR_DELETING_LESSON} {str(e)}")
            return (False, LMM.ERROR_DELETING_LESSON)