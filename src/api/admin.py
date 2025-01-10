import os
from flask import redirect, request, session, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from .models import db, User

class SecureModelView(ModelView):
    def is_accessible(self):
        return session.get('admin_logged_in', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.login_view'))

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not session.get('admin_logged_in'):
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login', methods=['GET', 'POST'])
    def login_view(self):
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if username == os.getenv("ADMIN_USERNAME", "admin") and password == os.getenv("ADMIN_PASSWORD", "admin"):
                session['admin_logged_in'] = True
                return redirect(url_for('.index'))
        return self.render('admin_login.html')

    @expose('/logout')
    def logout_view(self):
        session.pop('admin_logged_in', None)
        return redirect(url_for('.login_view'))

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'sandstone'
    
    admin = Admin(app, name='devMentor Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())

    admin.add_view(SecureModelView(User, db.session))

    return admin