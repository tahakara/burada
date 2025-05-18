from modal import db
from typing import Tuple, Optional, List, Self
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

from modal.messages.Messages import AttenationDetailModelMessages as ADMM

class AttenationDetail(db.Model):
    __tablename__ = 'attenation_details'
    print("AttenationDetail")
    __table_args__ = (
        db.Index('idx_attenation_detail', 'attenation_id', 'student_uuid'),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_turkish_ci"
        }
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attenation_id = db.Column(db.Integer, db.ForeignKey('attenations.id'), nullable=False)
    student_uuid = db.Column(db.String(36), db.ForeignKey('students.student_uuid'), nullable=False)
    card_id = db.Column(db.String(255), nullable=True)  # RFID card ID
    timestamp = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    def __repr__(self):
        return f"<AttenationDetail {self.id}-{self.attenation_id}-{self.student_uuid}>"
    
    @classmethod
    def create(cls, attenation_id: int, student_uuid: str, card_id: str = None) -> Tuple[bool, str, Optional["AttenationDetail"]]:
        """Record a student attendance.
        
        Args:
            attenation_id (int): ID of the attendance session
            student_uuid (str): UUID of the student
            card_id (str, optional): RFID card ID used
            
        Returns:
            Tuple: (success: bool, message: str, detail: Optional[AttenationDetail])
        """
        try:
            # Check if the student is already marked for this session
            existing = AttenationDetail.query.filter_by(
                attenation_id=attenation_id,
                student_uuid=student_uuid
            ).first()
            
            if existing:
                return (False, ADMM.ALREADY_MARKED_PRESENT, None)
            
            detail = AttenationDetail(
                attenation_id=attenation_id,
                student_uuid=student_uuid,
                card_id=card_id,
                timestamp=datetime.now()
            )
            
            db.session.add(detail)
            db.session.commit()
            
            return (True, ADMM.ATTENDANCE_RECORDED_SUCCESSFULLY, detail)
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"{ADMM.ERROR_RECORDING_ATTENDANCE} {str(e)}")
            return (False, ADMM.ERROR_RECORDING_ATTENDANCE, None)
    
    @classmethod
    def get_by_attenation(cls, attenation_id: int) -> List["AttenationDetail"]:
        """Get all attendance records for a session.
        
        Args:
            attenation_id (int): ID of the attendance session
            
        Returns:
            List[AttenationDetail]: List of attendance records
        """
        return cls.query.filter_by(attenation_id=attenation_id).all()
    
    @classmethod
    def get_by_student(cls, student_uuid: str) -> List["AttenationDetail"]:
        """Get all attendance records for a student.
        
        Args:
            student_uuid (str): UUID of the student
            
        Returns:
            List[AttenationDetail]: List of attendance records
        """
        return cls.query.filter_by(student_uuid=student_uuid).all()
    
    @classmethod
    def is_present(cls, attenation_id: int, student_uuid: str) -> bool:
        """Check if a student is marked present for a session.
        
        Args:
            attenation_id (int): ID of the attendance session
            student_uuid (str): UUID of the student
            
        Returns:
            bool: True if present, False otherwise
        """
        return cls.query.filter_by(
            attenation_id=attenation_id,
            student_uuid=student_uuid
        ).first() is not None