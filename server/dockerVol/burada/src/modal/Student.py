from modal import db
from typing import Tuple, Optional, List, Self
from sqlalchemy.exc import SQLAlchemyError
import logging

from modal.messages.Messages import StudentModelMessages as SMM

class Student(db.Model):
    __tablename__ = 'students'
    __table_args__ = (
        db.Index('idx_student_name', 'name', 'surname'),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_turkish_ci"
        }
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(255), nullable=False)
    student_uuid = db.Column(db.String(36), unique=True, default=db.func.uuid())
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f"<Student {self.id}-{self.student_uuid}-{self.name} {self.surname}>"
    
    @classmethod
    def create(cls, name: str, surname: str) -> Tuple[bool, str, Optional["Student"]]:
        """Create a new student in the database.
        
        Args:
            name (str): First name of the student
            surname (str): Last name of the student
            
        Returns:
            Tuple: (success: bool, message: str, student: Optional[Student])
        """
        try:
            student = Student(
                name=name,
                surname=surname,
                student_uuid=db.func.uuid()
            )
            
            db.session.add(student)
            db.session.commit()
            
            return (True, SMM.STUDENT_CREATED_SUCCESSFULLY, student)
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{SMM.ERROR_CREATING_STUDENT} {str(e)}")
            return (False, SMM.ERROR_CREATING_STUDENT, None)
    
    @classmethod
    def get_by_uuid(cls, student_uuid: str) -> Optional["Student"]:
        """Get a student by UUID.
        
        Args:
            student_uuid (str): UUID of the student
            
        Returns:
            Optional[Student]: Student object if found, None otherwise
        """
        return cls.query.filter_by(student_uuid=student_uuid).first()
    
    @classmethod
    def get_all(cls) -> List["Student"]:
        """Get all students.
        
        Returns:
            List[Student]: List of all students
        """
        return cls.query.all()
    
    def update(self, name: str = None, surname: str = None) -> Tuple[bool, str, Optional[Self]]:
        """Update a student in the database.
        
        Args:
            name (str, optional): New first name for the student
            surname (str, optional): New last name for the student
            
        Returns:
            Tuple: (success: bool, message: str, student: Optional[Student])
        """
        if name:
            self.name = name
        if surname:
            self.surname = surname
        
        try:
            db.session.commit()
            return (True, SMM.STUDENT_UPDATED_SUCCESSFULLY, self)
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{SMM.ERROR_UPDATING_STUDENT} {str(e)}")
            return (False, SMM.ERROR_UPDATING_STUDENT, None)
    
    def delete(self) -> Tuple[bool, str]:
        """Delete a student from the database.
        
        Returns:
            Tuple: (success: bool, message: str)
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return (True, SMM.STUDENT_DELETED_SUCCESSFULLY)
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{SMM.ERROR_DELETING_STUDENT} {str(e)}")
            return (False, SMM.ERROR_DELETING_STUDENT)