from sqlalchemy import Column, Integer, String, BOOLEAN
from .base import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=False)
    name = Column(String)
    tg_user_name = Column(String)
    phone_number = Column(String)
    active = Column(BOOLEAN)

    def __str__(self):
        return 'tg id: {0}\n' \
               'Имя: {1}\n' \
               'tg username: {2}\n' \
               'Номер телефона: {3}\n' \
               '{4}'.format(self.user_id,
                            self.name,
                            self.tg_user_name,
                            self.phone_number,
                            'Заблокирован' if not self.active else None)
