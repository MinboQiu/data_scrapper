from sqlalchemy.orm import sessionmaker
from landchina.landchina_com.models.models import create_engine, create_table
from scrapy.utils.project import get_project_settings


engine = create_engine(get_project_settings().get("CONNECTION_STRING"))
create_table(engine)
# session = sessionmaker(bind=engine)()
#
# rec = models.Record()
# rec.name = "test1"
# rec.payments = [models.Payment(id=1, amount=1.7)]
#
# try:
#     session.add(rec)
#     session.commit()
# except:
#     session.rollback()
#     raise
# finally:
#     session.close()
