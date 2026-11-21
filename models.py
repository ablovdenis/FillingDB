# Используется только одна таблица "префиксная строка - число вхождений".
# Число вхождений переведу в вероятности на 3-ем задании (если это вообще потребуется).

from sqlalchemy import CheckConstraint, LargeBinary
from sqlalchemy.orm import mapped_column, Mapped

from settings import Base


class PrefixStringModel(Base):
  __tablename__ = 'PrefixString'

  pref_str: Mapped[bytes] = mapped_column(LargeBinary, primary_key=True)
  count: Mapped[int]

  __table_args__ = (
    CheckConstraint('count > 0'),
  )
