from peewee import *
import datetime
import bcrypt

db = SqliteDatabase('db/restaurnt.db')

class BaseModel(Model):
    class Meta:
        database = db

class Dish(BaseModel):
    id = PrimaryKeyField()
    name = CharField(unique=True)
    price = DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        table_name = 'dishes'

class Receipt(BaseModel):
    id = PrimaryKeyField()
    final_price = DecimalField(max_digits=9, decimal_places=2)
    date_create = DateField(default=datetime.date.today)

    class Meta:
        table_name = 'receipts'
        order_by = ('date_create',)

class Waiter(BaseModel):
    id = PrimaryKeyField()
    username = CharField(unique=True) 
    password_hash = CharField() 
    first_name = CharField(null=True) 
    second_name = CharField(null=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    class Meta:
        table_name = 'waiters'

class Table(BaseModel):
    id = PrimaryKeyField()
    table_number = IntegerField(unique=True)
    capacity = IntegerField(default=4)

    class Meta:
        table_name = 'tables'

class Order(BaseModel):
    id = PrimaryKeyField()
    waiter = ForeignKeyField(Waiter, backref='orders')
    table = ForeignKeyField(Table, backref='orders')
    order_date = DateTimeField(default=datetime.datetime.now)
    is_completed = BooleanField(default=False)
    is_paid = BooleanField(default=False) 
    receipt = ForeignKeyField(Receipt, backref='orders', null=True) # Чек может быть не создан сразу.

    class Meta:
        table_name = 'orders'
        order_by = ('order_date',)

class OrderItem(BaseModel):  
    order = ForeignKeyField(Order, backref='items')
    dish = ForeignKeyField(Dish)
    quantity = IntegerField(default=1)

    class Meta:
        table_name = 'order_items'
        primary_key = CompositeKey('order', 'dish')



