# source https://www.safaribooksonline.com/library/view/essential-sqlalchemy-2nd/9781491916544/ch01.html
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import insert
from sqlalchemy import Table, Column, Integer, Numeric, String, ForeignKey
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, CheckConstraint

def get_engine():
    engine = create_engine('mysql+pymysql://root@localhost/alchemy', pool_recycle=3600)
    connection = engine.connect()
    return (engine,connection)

def creation():
    (engine,connection) = get_engine()
    metadata = MetaData()

    cookies = Table('cookies', metadata,
     Column('cookie_id', Integer(), primary_key=True,autoincrement=True),
    Column('cookie_name', String(50), index=True),
    Column('cookie_recipe_url', String(255)),
    Column('cookie_sku', String(55)),
    Column('quantity', Integer()),
    Column('unit_cost', Numeric(12, 2))
    )

    #users = Table('users', metadata, Column('user_id', Integer(), primary_key=True), Column('username', String(15), nullable=False, unique=True), Column('email_address', String(255), nullable=False), Column('phone', String(20), nullable=False), Column('password', String(25), nullable=False), Column('created_on', DateTime(), default=datetime.now), Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now) )
    metadata.create_all(engine)

def insertion():
    (engine,connection) = get_engine()
    cookies = Table('cookies', MetaData(engine),autoload=True)

    #option 1
    ins = cookies.insert().values (cookie_name="chocolate chip", cookie_recipe_url="http://some.aweso.me/cookie/recipe.html", cookie_sku="CC01", quantity="12", unit_cost="0.50")
    result = connection.execute(ins)
    print result.inserted_primary_key

    #option 2
    ins = insert(cookies).values (cookie_name="chocolate chip", cookie_recipe_url="http://some.aweso.me/cookie/recipe.html", cookie_sku="CC01", quantity="12", unit_cost="0.50")
    print(str(ins))
    print ins.compile().params
    result = connection.execute(ins)
    print result.inserted_primary_key

    #option 3
    ins = cookies.insert()
    result = connection.execute(ins,cookie_name="chocolate chip", cookie_recipe_url="http://some.aweso.me/cookie/recipe.html", cookie_sku="CC01", quantity="12", unit_cost="0.50")
    print result.inserted_primary_key

    #option 4 insert multiple
    inventory_list = [
        { 'cookie_name': 'peanut butter', 'cookie_recipe_url': 'http://some.aweso.me/cookie/peanut.html', 'cookie_sku': 'PB01', 'quantity': '24', 'unit_cost': '0.25' },
        { 'cookie_name': 'oatmeal raisin', 'cookie_recipe_url': 'http://some.okay.me/cookie/raisin.html', 'cookie_sku': 'EWW01', 'quantity': '100', 'unit_cost': '1.00' }
    ]
    result = connection.execute(ins,inventory_list)


#creation()
insertion()

