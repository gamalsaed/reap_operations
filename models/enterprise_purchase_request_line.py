from odoo import fields, models, api


class EnterpricePurchaseRequestLine(models.Model):

    _name = "enterprise.purchase.request.line"

    request_id = fields.Many2one(
        "enterprise.request", string="Request", required=True, ondelete="cascade")
    purchase_request_id = fields.Many2one(
        "enterprise.purchase.request", string="Purchase Request ID")
    product_id = fields.Many2one(
        "product.product", string="Product", required=True)
    requested_qty = fields.Float(string="QTY", required=True)
    available_qty = fields.Float(
        string="Avaliable QTY", related="product_id.qty_available")
    purchase_qty = fields.Float(
        string="Purchase QTY")
    uom_id = fields.Many2one("uom.uom", required=True, string="UOM")
    currency_id = fields.Many2one(
        "res.currency",
        related="request_id.site_id.project_id.x_currency_id",
        store=True,
        readonly=True,
    )
    estimated_unit_price = fields.Monetary(
        string="Estimated Unit Price", required=True, currency_field="currency_id")

    @api.depends("requested_qty", "available_qty")
    def _compute_purchase_qty(self):
        for rec in self:
            rec.purchase_qty = max(
                rec.requested_qty - rec.available_qty,
                0
            )
