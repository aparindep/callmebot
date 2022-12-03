import unittest
from callmebot import create_app,db
import datetime
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
        self.assertTrue(response.status_code == 200)

        # logout TODO: add logout test
        response = self.client.get('/auth/logout')
        self.assertTrue(response.status_code == 302)
    
    def test_new_reminder(self):
        # register 
        response = self.client.post('/auth/register', data=USER)
        self.assertTrue(response.status_code == 302)

        # test new reminder view
        response = self.client.get('/new')
        self.assertTrue(response.status_code == 200)
        
        # test post form
        response = self.client.post('/new', data={
                                'subject':  'test',
                                'content': 'test',
                                'date': datetime.date(2023, 1, 1)
                            })
        self.assertTrue(response.status_code == 302)
        
if __name__=='__main__':
    unittest.main()