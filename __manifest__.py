{
    "name": "Enterprise Operations Management Suite",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "summary": "Learning project",
    "depends": ["hr","project", "mail"],
    "data": [
        # Data
        "data/sequance.xml",
        
        # Security
        "security/groups.xml",
        "security/ir.model.access.csv",
        # Views
        "views/inherited_project_view.xml",
        "wizard/rejection_reason_view.xml",
        "wizard/enterprise_product_mapping_wizard_view.xml",
        "views/enterprise_site_view.xml",
        "views/enterprise_request_view.xml",
        "views/enterprise_request_line_view.xml",
        "views/menu_view.xml",
    ],
}
