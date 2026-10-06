def auto_sequence(self, vals, code, field_name):
    for val in vals:
        if val.get(field_name, "New") == "New":
            val[field_name] = self.env["ir.sequence"].next_by_code(code)