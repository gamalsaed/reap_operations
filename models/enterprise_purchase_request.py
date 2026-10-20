from odoo import api, models, fields
from ..utils import auto_sequence


class EnterprisePurchaseRequest(models.Model):
    _name = "enterprise.purchase.request"

    name = fields.Char(readyonly=True, default="New")
    source_request_id = fields.Many2one(
        "enterprise.request", readonly=True, required=True, string="Source ID")
    project_id = fields.Many2one(
        "project.project", string="Project ID", required=True)
    site_id = fields.Many2one(
        "enterprise.project.site", string="Site ID")
    purchase_type = fields.Selection([
        ("direct", "Direct"),
        ("indirect", "Indirect")
    ], default="direct")
    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True)
    requester_id = fields.Many2one(
        "hr.employee", related="source_request_id.requester_id", string="Employee", required=True)
    required_date = fields.Date(
        related="source_request_id.required_date", required=True)
    line_ids = fields.One2many(
        related="source_request_id.line_ids", readonly=True, required=True)
    purchase_request_lines = fields.One2many(
        "enterprise.purchase.request.line", "purchase_request_id")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rfq", "RFQ"),
        ("closed", "Closed"),
        ("cancel", "Cancel"),
    ], default="draft", required=True)

    @api.model_create_multi
    def create(self, vals):
        return super().create(vals)

    def handle_submit(self):
        self.state = "submitted"

    def handel_cancel(self):
        self.state = "cancel"

    def handle_approve(self):
        products_rfq = []
        for line in self.line_ids:
            p_qty = max(
                line.quantity - line.product_id.qty_available,
                0
            )
            if p_qty > 0:
                products_rfq.append((0, 0, {
                    "product_id": line.product_id.id,
                    "product_qty": p_qty,
                    "price_unit": 0.0,
                }))
        self.env["purchase.order"].create({
            "partner_id": self.partner_id.id,
            "date_order": self.required_date,
            "state": "draft",
            "order_line": products_rfq,
        })
