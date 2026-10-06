from odoo import fields, models


class RejectionReason(models.TransientModel):
    _name = 'rejection.reason'
    _description = 'Rejection Reason'

    request_id = fields.Many2one('enterprise.request')
    reason = fields.Char(string='Reason', required=True)

    def handle_rejection_save(self):
        request = self.env["enterprise.request"].browse(self.request_id.id)
        print(self.request_id)
        print(request)
        request.write({'rejection_reason': self.reason, "state": "rejected"})