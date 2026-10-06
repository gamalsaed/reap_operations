from odoo import fields, models

class EnterpriseProductMappingWizard(models.TransientModel):
    _name = "enterprise.product.mapping.wizard"
    _description = "Enterprise Product Mapping Wizard"

    request_line_id = fields.Many2one("enterprise.request.line")
    request_description = fields.Char(related="request_line_id.requested_description", readonly=True, string="Requested Description")
    product_id = fields.Many2one("product.product", string="Product", required=True)

    def handle_map_save(self):
        line = self.env["enterprise.request.line"].browse(self.request_line_id.id)
        line.write({"product_id": self.product_id, "product_status": "known"})