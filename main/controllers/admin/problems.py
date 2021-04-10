from main import app
from main import auth


@app.route('/admin/problems', methods=['GET'])
@auth.requires_token_auth('admin')
def log_in_admin_google(args):
    return {}
