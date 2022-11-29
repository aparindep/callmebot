import unittest
from callmebot import create_app,db
from callmebot.models import User
from config import TestingConfig

EMAIL = 'alejoparinelli@gmail.com'
USER = {
    'email': EMAIL,
    'username': 'zephord',
    'password': 'hello',
    'password2': 'hello',
}

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_and_login(self):
        # test register
        response = self.client.post('/auth/register', data=USER)
        self.assertTrue(response.status_code == 302)

        # try confirmation token    
        user = User.query.filter_by(email=EMAIL).first()
        token = user.generate_confirmation_token()
        response = self.client.get('/auth/confirm/' + token.decode('utf-8'))
        print(response.get_data(as_text=True))
        self.assertTrue('succesfully' in response.get_data(as_text=True))

        # logout TODO: add logout test
    
    # TODO: add "new reminder" button test
        
