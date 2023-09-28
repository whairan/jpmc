from nameko.events import EventDispatcher
from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession

from orders.exceptions import NotFound
from orders.models import DeclarativeBase, Order, OrderDetail
from orders.schemas import OrderSchema, OrderDetailSchema
from sqlalchemy.orm import joinedload
# from typing import List
# import sqlalchemy as sa
from datetime import datetime
import datetime

from sqlalchemy import and_

class OrdersService:
    name = 'orders'

    db = DatabaseSession(DeclarativeBase)
    event_dispatcher = EventDispatcher()

    cutoff_timestamp = datetime.datetime(2023, 9, 28)

    @rpc
    def get_order(self, order_id):
        order = self.db.query(Order).filter(Order.id == order_id).options(joinedload(Order.order_details)).first()

        if not order:
            raise NotFound(f'Order with id {order_id} not found')

        return OrderSchema().dump(order).data

    @rpc
    def create_order(self, order_details):
        order = Order()
        order.order_details = [
            OrderDetail(
                product_id=order_detail['product_id'],
                price=order_detail['price'],
                quantity=order_detail['quantity']
            )
            for order_detail in order_details
        ]
        
        self.db.add(order)
        self.db.commit()

        order = OrderSchema().dump(order).data

        self.event_dispatcher('order_created', {
            'order': order,
        })

        return order


#Original methods that I thought could use minor improvements to optimize for response time.
    # @rpc
    # def get_order(self, order_id):

    #     order = self.db.query(Order).get(order_id)

    #     if not order:
    #         raise NotFound('Order with id {} not found'.format(order_id))

    #     return OrderSchema().dump(order).data


    # @rpc
    # def create_order(self, order_details):
    #     order = Order(
    #         order_details=[
    #             OrderDetail(
    #                 product_id=order_detail['product_id'],
    #                 price=order_detail['price'],
    #                 quantity=order_detail['quantity']
    #             )
    #             for order_detail in order_details
    #         ]
    #     )
    #     self.db.add(order)
    #     self.db.commit()

    #     order = OrderSchema().dump(order).data

    #     self.event_dispatcher('order_created', {
    #         'order': order,
    #     })

    #     return order
    
    @rpc
    def update_order(self, order):
        order_details = {
            order_details['id']: order_details
            for order_details in order['order_details']
        }

        order = self.db.query(Order).get(order['id'])

        for order_detail in order.order_details:
            order_detail.price = order_details[order_detail.id]['price']
            order_detail.quantity = order_details[order_detail.id]['quantity']

        self.db.commit()
        return OrderSchema().dump(order).data

    @rpc
    def delete_order(self, order_id):
        order = self.db.query(Order).get(order_id)
        self.db.delete(order)
        self.db.commit()



    # Method A --- Avg Response time 62 ms
    @rpc
    def list_orders(self):
        # Using the indexed 'created_at' column for filtering the newly created orders
        query = self.db.query(Order).filter(Order.created_at <= datetime.datetime.utcnow())
        # Records as a list of orders with associated order details
        records = query.all()
        # Serializing the queried records into a list of dicts
        serialized_orders = [
            {
                "order": OrderSchema().dump(record).data,
                "order_details": [OrderDetailSchema().dump(detail).data for detail in record.order_details]
            }
            for record in records
    ]
        return serialized_orders


    # Method B --- 

    # Method deleting older data --- https://a.blazemeter.com/app/?public-token=aj9HvcE9YujbqE7kfgzkgzTaWNdAssuBDayG4V0Di14udt1IZO#/accounts/-1/workspaces/-1/projects/-1/sessions/r-ext-6513c648a2eb4955156788/summary/summary
    # def delete_old_orders(self):
    #     # Filter out/del orders created before the cutoff date
    #     self.db.query(Order).filter(Order.created_at < self.cutoff_timestamp).delete()
    #     self.db.commit()

    # # Good average performance 53 ms with original/unmodified database
    # @rpc
    # def list_orders(self):
    #     self.delete_old_orders()
    #     orders = self.db.query(Order).options(joinedload(Order.order_details)).all()
    #     # print([OrderSchema().dump(order).data for order in orders]) #for debugging purposes
    #     return [OrderSchema().dump(order).data for order in orders]

    #_______


    #Method C   
    # If we don't want to filter orders and want to qury the whole list using eager loading, then the following method can be used instead:
    # Performance is ok (higher response time average 116 ms) compared to filtering
    # @rpc
    # def list_orders(self):
    #     orders = self.db.query(Order).options(joinedload(Order.order_details)).all()
    #     return [OrderSchema().dump(order).data for order in orders]
    #_________


    # Methods with higher response times: 
    #_________


    # High latency average  887
    # @rpc
    # def list_orders(self):
    #     # Define a cutoff date (e.g., orders created after Sep 26, 2023)
    #     cutoff_date = datetime(2023, 9, 27)
    #     orders = self.db.query(Order).filter(Order.created_at > cutoff_date).options(joinedload(Order.order_details)).all()
    #     return [OrderSchema().dump(order).data for order in orders]

    #Super High latency  --- https://a.blazemeter.com/app/?public-token=dPlYw9oC0qR6FCnaZBwmqa4IeOxhsGXGVPfrYVLmdm1jiMVXEj#/accounts/-1/workspaces/-1/projects/-1/sessions/r-ext-6513a6a45518f553799367/summary/summary
    # @rpc
    # def list_orders(self):
    #     orders = self.db.query(Order).all()
    #     return [OrderSchema().dump(order).data for order in orders]
    
    # List orders rpc call 
    # @rpc
    # def orders_list(self):
    #     orders = self.db.query(Order).all()
    #     return OrderSchema(many=True).dump(orders).data


    # Fast, but it returns empty list -- needs debugging
    # @rpc
    # def list_orders(self):
    #     # Filter orders created before or up to the cutoff timestamp as to decrease the response time.
    #     orders = self.db.query(Order).filter(Order.created_at <= self.cutoff_timestamp).options(joinedload(Order.order_details)).all()
    #     print([OrderSchema().dump(order).data for order in orders])
    #     return [OrderSchema().dump(order).data for order in orders]

    #_________
