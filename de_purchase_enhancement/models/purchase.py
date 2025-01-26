from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    auto_complete_id = fields.Many2one('sale.order', string="Auto Complete")

    @api.onchange('auto_complete_id')
    def onchange_sale_order(self):
        for other_input in self.order_line:
            other_input.unlink()
        data = []
        if self.auto_complete_id:
            for line in self.auto_complete_id.order_line:
                cost = 0
                for vendor in line.product_id.seller_ids:
                    if vendor.name.id == self.partner_id.id:
                        cost = vendor.total_cost
                data.append((0, 0, {
                    'order_id': self.id,
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'product_qty': line.product_uom_qty,
                    'date_planned': fields.Date.today(),
                    'price_unit': cost,
                    'product_uom': line.product_id.uom_po_id.id,
                }))
            self.order_line = data


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # @api.onchange('product_id')
    # def product_onchange(self):
    #     print(self.price_unit)
    #     if self.product_id:
    #         cost = 0
    #         print(self.product_id.seller_ids)
    #         for vendor in self.product_id.seller_ids:
    #             print(self.order_id.partner_id.id)
    #             if vendor.name.id == self.order_id.partner_id.id:
    #                 cost = vendor.total_cost
    #                 print(cost)
    #         self.write({'price_unit': cost})
    #         print(self.price_unit)

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        # If not seller, use the standard price. It needs a proper currency conversion.
        if not seller:
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                self.product_id.uom_id._compute_price(self.product_id.standard_price, self.product_id.uom_po_id),
                self.product_id.supplier_taxes_id,
                self.taxes_id,
                self.company_id,
            )
            if price_unit and self.order_id.currency_id and self.order_id.company_id.currency_id != self.order_id.currency_id:
                price_unit = self.order_id.company_id.currency_id._convert(
                    price_unit,
                    self.order_id.currency_id,
                    self.order_id.company_id,
                    self.date_order or fields.Date.today(),
                )
            self.price_unit = price_unit
            return

        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price,
                                                                             self.product_id.supplier_taxes_id,
                                                                             self.taxes_id,
                                                                             self.company_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        self.price_unit = price_unit

        if self.product_id:
            cost = 0
            print(self.product_id.seller_ids)
            for vendor in self.product_id.seller_ids:
                print(self.order_id.partner_id.id)
                if vendor.name.id == self.order_id.partner_id.id:
                    cost = vendor.total_cost
                    print(cost)
            self.write({'price_unit': cost})


