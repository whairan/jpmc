import datetime
from sqlalchemy import (
    DECIMAL, Column, DateTime, ForeignKey, Integer, DECIMAL, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


#using indexing
class Base(object):
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )

DeclarativeBase = declarative_base(cls=Base)

class Order(DeclarativeBase):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    # Using lazy loading to speed things up
    order_details = relationship("OrderDetail", lazy="joined", backref="order")

    # Create an index on the 'created_at' column
    orders_created_at_idx = Index('orders_created_at_idx', created_at)

class OrderDetail(DeclarativeBase):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id", name="fk_order_details_orders"),
        nullable=False
    )
    product_id = Column(Integer, nullable=False)
    price = Column(DECIMAL(18, 2), nullable=False)
    quantity = Column(Integer, nullable=False)

    # Create an index on the 'product_id' column
    order_details_product_id_idx = Index('order_details_product_id_idx', product_id)





# Use the following database with with the Method B
# class Base(object):
#     created_at = Column(
#         DateTime,
#         default=datetime.datetime.utcnow,
#         nullable=False
#     )
#     updated_at = Column(
#         DateTime,
#         default=datetime.datetime.utcnow,
#         onupdate=datetime.datetime.utcnow,
#         nullable=False
#     )


# DeclarativeBase = declarative_base(cls=Base)


# class Order(DeclarativeBase):
#     __tablename__ = "orders"

#     id = Column(Integer, primary_key=True, autoincrement=True)


# class OrderDetail(DeclarativeBase):
#     __tablename__ = "order_details"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     order_id = Column(
#         Integer,
#         ForeignKey("orders.id", name="fk_order_details_orders"),
#         nullable=False
#     )
#     order = relationship(Order, backref="order_details")
#     product_id = Column(Integer, nullable=False)
#     price = Column(DECIMAL(18, 2), nullable=False)
#     quantity = Column(Integer, nullable=False)
