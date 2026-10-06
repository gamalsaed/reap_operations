from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.orm.decorators import ondelete


class EnterpriseRequestLine(models.Model):
    _name = "enterprise.request.line"
    _description = "Enterprise Request Line"

    request_id = fields.Many2one("enterprise.request", string="Request", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Product")
    requested_description = fields.Char(string="Description")
    currency_id = fields.Many2one(
        "res.currency",
        related="request_id.site_id.project_id.x_currency_id",
        store=True,
        readonly=True,
    )
    product_status = fields.Selection([
        ("known", "Known"),
        ("unknown", "Unknown")
    ], default="known", required=True)
    product_uom_id = fields.Many2one("uom.uom", string="UOM", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    estimated_unit_price = fields.Monetary(string="Estimated Unit Price", required=True, currency_field="currency_id")
    subtotal = fields.Monetary(string="Subtotal", required=True, compute="_compute_subtotal", currency_field="currency_id")

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError("Quantity must be greater than 0")

    @api.constrains("estimated_unit_price")
    def _check_estimated_unit_price(self):
        for line in self:
            if line.estimated_unit_price < 0:
                raise ValidationError("Estimated Unit Price must be greater than 0")

    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.estimated_unit_price

    @api.constrains("product_id")
    def _check_product_id(self):
        if self.product_status == "known" and not self.product_id:
            raise ValidationError("Product is required")

    @api.constrains("requested_description")
    def _check_product_description(self):
        if self.product_status == "unknown" and not self.requested_description:
            raise ValidationError("You must provide a description for the product")

    def write(self, vals):
        if self.request_id.state == "approved" and self.env.user.has_group("reap_operations.group_reap_users"):
            raise UserError("You can't edit this line because Your request is already approved")
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get("request_id"):
                request = self.env["enterprise.request"].browse(val.get("request_id"))
                if request.state == "approved" and self.env.user.has_group("reap_operations.group_reap_users"):
                    raise UserError("You can't create a new line because your request is already approved")
        return super().create(vals)

    def unlink(self):
        for record in self:
            if record.request_id.state == "approved" and self.env.user.has_group("reap_operations.group_reap_users"):
                raise UserError("You can't remove this line because your request is already approved")
        return super().unlink()

    def map_product_action(self):
        return {
            "name": "Map Product Wizard",
            "type": "ir.actions.act_window",
            "res_model": "enterprise.product.mapping.wizard",
            "target": "new",
            "view_mode": "form",
            "context": {
                "default_request_line_id": self.id
            }
        }