from odoo import api, fields, models


class ProductBundle(models.Model):
    _name = 'product.bundle'
    _description = "Product Bundle"
    name = fields.Char(required=True, string='Bundle Product')
    bundle_lines = fields.One2many('product.bundle.line', 'bundle_id', string="Add a line")


class ProductBundleLine(models.Model):
    _name = 'product.bundle.line'
    _description = "Product Bundle Line"
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string="Quantity")
    bundle_id = fields.Many2one('product.bundle')


class ProductBundleSale(models.Model):
    _name = 'product.bundle.sale'
    _description = "Product Bundle Sale"
    bundle_id = fields.Many2one('product.bundle', string='Product Bundle')
    order_id = fields.Many2one('sale.order')

    @api.model
    def unlink(self):
        order_line = self.env['sale.order.line'].search([('bundle_id', '=', self.id)])
        for line in order_line:
            line.unlink()
        res = super(ProductBundleSale, self).unlink()
        return res

    @api.model
    def create(self, vals):
        rec = super(ProductBundleSale, self).create(vals)
        product_bundle = self.env['product.bundle'].search([('id', '=', rec.bundle_id.id)])
        new_sale_section = self.env['sale.order.line'].create({
            'name': product_bundle.name,
            'display_type': 'line_section',
            'order_id': rec.order_id.id,
            'bundle_id': rec.id
        })
        for line in product_bundle.bundle_lines:
            new_sale_line = self.env['sale.order.line'].create({
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'order_id': rec.order_id.id,
                'bundle_id': rec.id
            })
        return rec

    def write(self, vals):
        if vals.get('bundle_id'):
            order_line = self.env['sale.order.line'].search([('bundle_id', '=', self.id)])
            for line in order_line:
                line.unlink()
            rec = super(ProductBundleSale, self).write(vals)
            bundle_id = vals.get('bundle_id')
            bundle_rec = self.env['product.bundle'].browse(bundle_id)
            new_sale_section = self.env['sale.order.line'].create({
                'name': bundle_rec.name,
                'display_type': 'line_section',
                'order_id': self.order_id.id,
                'bundle_id': self.id})

            for line in bundle_rec.bundle_lines:
                new_sale_line = self.env['sale.order.line'].create({
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'order_id': self.order_id.id,
                    'bundle_id': self.id})


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    bundle_ids = fields.One2many('product.bundle.sale', 'order_id')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    
    bundle_id = fields.Many2one('product.bundle.sale')
    #markup = fields.Float(string="Markup%")
    #@api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'markup')
    def _compute_amount1(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

            total = 0.0
            total = (line.markup / 100) * line.price_subtotal
            line.price_subtotal = line.price_subtotal + total




