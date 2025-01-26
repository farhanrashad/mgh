from odoo import api, fields, models
from odoo.exceptions import UserError
from _datetime import date


class Producttemplate(models.Model):
    _inherit = 'product.template'

    sale_price_comp = fields.Selection([('cost price', 'Cost Price'), ('vendor total cost', 'Vendor Total Cost')],
                                       default='cost price', required=True, string='Sale Price Computation')
    percentage_addition = fields.Float(string='Percentage addition')
    min_profit = fields.Float(string='Minimum Profit')
    min_sale = fields.Float(string='Minimum Sale')
    vendor_id = fields.Many2one('res.partner')

    @api.constrains('seller_ids')
    def check_is_applicable(self):
        if self.seller_ids:
            flag = 0
            if self.seller_ids:
                for rec in self.seller_ids:
                    if rec.is_applicable == True:
                        flag += 1
                    if flag > 1:
                        raise UserError("You Cannot Select Multiple Vendor select Just Single Vendor")

    def update_sale_price_upon_cost(self):
        product_template_ids = self.search([('sale_price_comp', '=', 'cost price')])

        for product in product_template_ids:
            percentage = 0
            if product.standard_price > 0:
                percentage = (product.standard_price / 100) * product.percentage_addition
                product.list_price = product.standard_price + percentage

            percentage_min_sale = product.list_price - ((product.list_price / 100) * product.min_profit)
            product.min_sale = percentage_min_sale


        product_template_ids = self.search([('sale_price_comp', '=', ('cost price', 'vendor total cost'))])
        for product in product_template_ids:
            print('-------------------name',product.name)
            product.cost_cal()
            
    @api.onchange('seller_ids')
    @api.depends('seller_ids')
    def _onchange_vendors(self):
        ids = []
        if self.seller_ids:
            for seller in self.seller_ids:
                ids.append(seller.name.id)
        return {'domain': {'vendor_id': [('id', '=', ids)]}}

    @api.constrains('min_sale', 'min_profit', 'percentage_addition')
    def compute_min_amount(self):
        if self.min_profit > 100 or self.min_profit < 0:
            raise UserError("**Minimum Profit percent** cannot be greater than 100")

        if self.percentage_addition > 100 or self.percentage_addition < 0:
            raise UserError("**Addition percent** cannot be greater than 100")

    def cost_cal(self):
        flag = 0
        if self.sale_price_comp == 'vendor total cost':
            if self.percentage_addition >= 0:
                if self.seller_ids:
                    for vendor in self.seller_ids:
                        if vendor.is_applicable == True:
                            flag = 1
                            total = vendor.total_cost + ((vendor.total_cost / 100) * self.percentage_addition)

                            if vendor.company_id.currency_id.id != vendor.currency_id.id:
                                currency = self.env['res.currency'].search(
                                    [('active', '=', True), ('id', '=', vendor.currency_id.id)])
                                if currency:
                                    total = total / currency.rate
                                    self.list_price = total
                            else:
                                self.list_price = total
                    if flag == 0:
                        self.list_price = 0

        if self.sale_price_comp == 'cost price':
            if self.percentage_addition >= 0:
                for purchase in self:
                    total = purchase.standard_price + ((purchase.standard_price / 100) * self.percentage_addition)
                    self.list_price = total
                    break

    @api.onchange('seller_ids')
    def onchange_seller_ids(self):
        self.cost_cal()

    @api.onchange('standard_price')
    def onchange_standard_price(self):
        self.cost_cal()

    @api.onchange('percentage_addition', 'sale_price_comp')
    def onchange_sale_price(self):
        self.cost_cal()

    @api.onchange('min_profit', 'list_price')
    def onchange_profit_sale_price(self):
        for rec in self:
            total_profit = rec.list_price - ((rec.list_price / 100) * rec.min_profit)
            rec.min_sale = total_profit


class ProductVendorPrice(models.Model):
    _inherit = 'product.supplierinfo'

    is_applicable = fields.Boolean(string="Applicable", default=False)
    est_landed_cost = fields.Float(string="Estimated Landed Cost %")
    total_cost = fields.Float(string="Total Cost", compute='_compute_amount')

    @api.depends('price', 'est_landed_cost')
    def _compute_amount(self):
        for line in self:
            total = line.price + ((line.price / 100) * line.est_landed_cost)
            line.total_cost = total


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def round_up_multiple_five(self, x, base=5):
        res = base * round(x/base)
        if res < x:
            res = res + 5
        return res
    
    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit_a = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit_a = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
            self.price_unit_a = self.round_up_multiple_five(self.price_unit_a)
            
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
            self.price_unit = self.round_up_multiple_five(self.price_unit)
    
    
    @api.constrains('price_unit')
    def constraint_price_unit(self):
        for rec in self:
            if rec.price_unit < rec.product_id.min_sale:
                raise UserError("Unit price cannot be less than Min Sale Amount")

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                company = self.env['res.company'].search([], order="id asc", limit=1)
                
                if rec.product_id.product_tmpl_id.sale_price_comp == 'vendor total cost':
                    if rec.product_id.product_tmpl_id.seller_ids:
                        for vendor in rec.product_id.product_tmpl_id.seller_ids:
                            if vendor.is_applicable == True:
                                
                                if vendor.currency_id.id != rec.order_id.pricelist_id.currency_id.id:
                                    to_currency = rec.order_id.pricelist_id.currency_id
                                    from_currency = vendor.currency_id
                                    
                                    print('from_currency',from_currency.name)
                                    print('to_currency',to_currency.name)
                                    if to_currency:
                                        converted_amount = from_currency._convert(vendor.total_cost, to_currency, company, date.today(), round=True)
                                        print('coverted amount-----------',converted_amount) 
                                        rec.cost_price = converted_amount
                                    else:
                                        rec.cost_price = vendor.total_cost
                                else:
                                    rec.cost_price = vendor.total_cost
        
                else:
                    if company.currency_id.id != rec.order_id.pricelist_id.currency_id.id:
                        to_currency = rec.order_id.pricelist_id.currency_id
                        from_currency = company.currency_id
                        if to_currency:
                            converted_amount = from_currency._convert(rec.product_id.standard_price, to_currency, company, date.today(), round=True)
                            rec.cost_price = converted_amount
                        else:
                            rec.cost_price = rec.product_id.standard_price
    
                    else:
                        rec.cost_price = rec.product_id.standard_price

    cost_price = fields.Float('Est Cost')
   


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity_set_price(self):
        for i in self:
            if i.product_id:
                if i.product_id.product_tmpl_id.seller_ids:
                    for vendor in i.product_id.product_tmpl_id.seller_ids:
                        if vendor.is_applicable == True:
                            i.price_unit = vendor.price