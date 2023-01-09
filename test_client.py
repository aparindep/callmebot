import unittest
import pytz
import datetime
from app import create_app, db
from app.models import User, Reminder

EMAIL = 'someemail@gmail.com'
USER = {
    'email': EMAIL,
    'username': 'username',
    'password': 'password',
    'password2': 'password',
    'timezone': pytz.timezone('America/Argentina/Buenos_Aires')
}

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
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

        # confirm    
        user = User.query.filter_by(email=EMAIL).first()
        token = user.generate_confirmation_token()
        response = self.client.get('/auth/confirm/' + token.decode('utf-8'))
        self.assertTrue(response.status_code == 200)

        response = self.client.get('/auth/logout')
        self.assertTrue(response.status_code == 302)
    
    def test_new_reminder(self):
        # register 
        response = self.client.post('/auth/register', data=USER)
        self.assertTrue(response.status_code == 302)
        
        # confirm
        user = User.query.filter_by(email=EMAIL).first()
        token = user.generate_confirmation_token()
        response = self.client.get('/auth/confirm/' + token.decode('utf-8'))
        self.assertTrue(response.status_code == 200)

        # test new deadline reminder
        response = self.client.get('/new/deadline')
        self.assertTrue(response.status_code == 200)
        
        response = self.client.post('/new/deadline', data={
                                'subject':  'test',
                                'content': 'test',
                                'date': datetime.date(2023, 1, 1)
                            })
        self.assertTrue(response.status_code == 302)

        # test new periodic reminder
        response = self.client.get('/new/periodic')
        self.assertTrue(response.status_code == 200)
        
        response = self.client.post('/new/periodic', data={
                                'subject':  'test',
                                'content': 'test',
                                'days': ['Mon', 'Tue']
                            })
        self.assertTrue(response.status_code == 302)

        # response = self.client.get('/')
        # self.assertTrue(render_template('_reminder.html', user=))

    def test_delete_reminder(self):
        # register 
        response = self.client.post('/auth/register', data=USER)
        self.assertTrue(response.status_code == 302)

        # new reminder
        u = User.query.filter_by(email = USER['email']).first()
        r = Reminder(
            subject='subject',
            content='content',
            date=datetime.datetime(2022, 12, 12),
            time= datetime.time(0,0),
            author_id=u.id
        )
        db.session.add(r)
        db.session.commit()

        # delete
        response = self.client.post(f'/delete/{r.id}')
        self.assertTrue(response.status_code == 302)

        
if __name__=='__main__':
    unittest.main()