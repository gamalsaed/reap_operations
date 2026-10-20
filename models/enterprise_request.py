from odoo import models, fields, api, exceptions
from ..utils import auto_sequence


class EnterpriseRequest(models.Model):
    _name = "enterprise.request"
    _description = "Enterprise Request"

    name = fields.Char(readyonly=True, default='New')
    request_date = fields.Datetime(default=fields.Datetime.now, readonly=True)
    requester_id = fields.Many2one(
        "hr.employee", string="Employee", required=True)
    department_id = fields.Many2one("hr.department", string="Department")
    partner_id = fields.Many2one("res.partner", string="Partner")
    project_id = fields.Many2one("project.project", string="Project")
    site_id = fields.Many2one(
        "enterprise.project.site", string="Site", domain="[('project_id', '=', project_id)]")
    request_type = fields.Selection([
        ("material", "Material"),
        ("service", "Service"),
        ("mixed", "Mixed"),
    ], required=True)
    required_date = fields.Date(string="Required Date", required=True)
    priority = fields.Selection([
        ("low", "Low"),
        ("normal", "Normal"),
        ("medium", "Medium"),
        ("high", "High"),
    ], default="normal", required=True)

    description = fields.Text(string="Description")
    line_ids = fields.One2many("enterprise.request.line", "request_id")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("manager_review", "Manager Review"),
        ("procurement", "Procurement"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("need_info", "Need Info"),
        ("cancelled", "Cancelled"),
        ("closed", "Closed"),
    ], default="draft")
    rejection_reason = fields.Char(string="Rejection Reason", readonly=True)

    total_estimated = fields.Integer(
        string="Total Estimated", compute="_compute_total_estimated")

    @api.model_create_multi
    def create(self, vals):
        auto_sequence(self, vals, "request_seq", "name")
        return super().create(vals)

    @api.constrains("required_date")
    def _check_request_date(self):
        for rec in self:
            if rec.required_date and rec.request_date and rec.required_date <= fields.Date.to_date(rec.request_date):
                raise exceptions.ValidationError("Required date is invalid")

    def _compute_total_estimated(self):
        for rec in self:
            rec.total_estimated = 0
            for line in rec.line_ids.mapped("subtotal"):
                rec.total_estimated += line

    def submit_handler(self):
        if fields.Date.to_date(self.required_date) <= fields.Date.today():
            raise exceptions.ValidationError("Required date is invalid")
        elif len(self.line_ids) == 0:
            raise exceptions.ValidationError(
                "You must submit at least one product")
        else:
            self.state = "submitted"

    def approved_handler(self):
        if self.env.user.has_group("reap_operations.group_reap_manager"):
            if self.state in ("submitted", "rejected"):
                # if there's a record dosen't have a product will case an error
                for line in self.line_ids:
                    if line.product_status == "unknown":
                        raise exceptions.UserError(
                            "All products must be known")
                self.state = "approved"
                sequence = self.env["ir.sequence"].next_by_code(
                    "purchase_request_seq"
                )
                purchase_request = self.env["enterprise.purchase.request"].sudo().create({
                    "name": sequence,
                    "source_request_id": self.id,
                    "project_id": self.project_id.id,
                    "site_id": self.site_id.id,
                    "requester_id": self.requester_id.id,
                    "required_date": self.required_date,
                    "partner_id": self.partner_id.id
                })
                products_rfq = []
                for line in self.line_ids:
                    p_qty = max(
                        line.quantity - line.product_id.qty_available,
                        0
                    )
                    product = self.env["enterprise.purchase.request.line"].sudo().create({
                        "request_id": self.id,
                        "purchase_request_id": purchase_request.id,
                        "product_id": line.product_id.id,
                        "requested_qty": line.quantity,
                        "uom_id": line.product_uom_id.id,
                        "estimated_unit_price": line.subtotal,
                        "purchase_qty": p_qty
                    })
                    if p_qty > 0:
                        products_rfq.append((0, 0, {
                            "product_id": product.product_id.id,
                            "product_qty": product.purchase_qty,
                            "price_unit": 0.0,
                        }))
                self.env["purchase.order"].sudo().create({
                    "partner_id": self.partner_id.id,
                    "date_order": self.required_date,
                    "state": "draft",
                    "order_line": products_rfq,
                })
            else:
                raise exceptions.UserError(
                    "You must submit at least one product")
        else:
            raise exceptions.UserError(
                "You are not authorized to approve this request")

    def action_open_rejection_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Rejection Wizard",
            "res_model": "rejection.reason",
            "view_mode": "form",
            "target": "new",
            "context": {"default_request_id": self.id},
        }
