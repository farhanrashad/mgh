import datetime as dt
import locale

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api



class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'



    def get_sale_order_date(self):
        date_done = self.date_order.date().strftime('%d %b %Y')

        return date_done

    def get_line_last(self):
        try:
           if self.order_line:
                
               line_last = self.order_line[-1]
               return line_last
        except Exception as e:
            print(e.args) 
