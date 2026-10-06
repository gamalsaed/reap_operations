from odoo import api, fields, models, exceptions
from ..utils import auto_sequence
class EnterpriseProjectSite(models.Model):
    _name = 'enterprise.project.site'

    site_sequence = fields.Char(default="New", readonly=True)
    name = fields.Char(string="Name", required=True)
    project_id = fields.Many2one("project.project", string="Project", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    manager_id = fields.Many2one("res.users", string="Manager")
    state = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("hold", "Hold"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    ], default="draft")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="Deadline")

    @api.model_create_multi
    def create(self, vals):
        auto_sequence(self, vals, "site_seq", "site_sequence")
        return super().create(vals)

    @api.constrains("date_end")
    def _check_date_end(self):
        if self.date_end <= self.date_start:
            raise exceptions.ValidationError("End date must be after start date.")


