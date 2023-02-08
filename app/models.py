from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, LargeBinary, DateTime
# from sqlalchemy.orm import relationship

from datetime import datetime

from database import Base


class UserModel(Base):
    __tablename__ = 'artusers'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    password_hash = Column(String())


class FileContent(Base):
    __tablename__ = 'filecontent'

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    filename = Column(Text)
    data = Column(LargeBinary, nullable=False)  # Actual data, needed for Download
    rendered_data = Column(Text, nullable=False)  # Data to render the pic in browser
    pic_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    url = Column(Text)
    user_id = Column(Integer, ForeignKey('artusers.id'))

    def __repr__(self):
        return f'Pic Name: {self.title}, created on: {self.pic_date}'
