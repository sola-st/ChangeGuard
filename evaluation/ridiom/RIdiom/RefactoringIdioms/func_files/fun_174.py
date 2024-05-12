def update_admin_perm_view(self):
    pvms = self.get_session.query(sqla_models.PermissionView).all()
    pvms = [p for p in pvms if p.permission and p.view_menu]
    admin = self.find_role('Admin')
    admin.permissions = list(set(admin.permissions) | set(pvms))
    self.get_session.commit()
