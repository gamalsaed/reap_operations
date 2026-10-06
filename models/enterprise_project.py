from odoo import fields, models, api, exceptions
from ..utils import auto_sequence
class EnterpriseProject(models.Model):
    _inherit = "project.project"

    project_sequence = fields.Char(default="New", readonly=True)
    business_unit_id = fields.Many2one("res.company", string="Business Unit")
    project_type = fields.Selection([ ("new", "New")
                                        , ("modernization", "Modernization")
                                        , ("relocation", "Relocation")
                                        , ("upgrade", "Upgrade"), ("swap", "Swap")
                                        , ("dismantle", "Dismantle") ]
                                        , string="Project Type"
                                        , default="new"
                                        , required=True)

    x_currency_id = fields.Many2one('res.currency', string="Currency", readyonly=False, required=True)
    budget = fields.Monetary(string="Budget", currency_field="x_currency_id")
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
    )
    x_site_ids = fields.One2many("enterprise.project.site", "project_id")


    @api.model_create_multi
    def create(self, vals):
        auto_sequence(self, vals, "project_seq", "project_sequence")
        return super().create(vals)

    def avail_sites(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Site List View",
            "view_mode": "list,form",
            "target": "current",
            "res_model": "enterprise.project.site",
            "domain": [('project_id', '=', self.id)],
        }

