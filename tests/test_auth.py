import pytest
from app import db
from app.models import User

class TestAuth:
    """Test authentication routes."""
    
    def test_register_get(self, client):
        """Test register page loads."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_register_post_success(self, client, app):
        """Test successful user registration."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'password123'
        })
        
        # Should redirect after successful registration
        assert response.status_code == 302
        
        # Check user was created in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.check_password('password123')
    
    def test_register_existing_user(self, app, client, sample_user):
        """Test registration with existing username."""
        with app.app_context():
            user = db.session.get(User, sample_user)
            response = client.post('/auth/register', data={
                'username': user.username,
                'email': 'different@example.com',
                'password': 'password123',
                'password2': 'password123'
            })
            
            # Should stay on the form (not redirect)
            assert response.status_code == 200
            # Should show some form validation error
            assert b'Register' in response.data  # Still showing register form
    
    def test_register_duplicate_email(self, app, client, sample_user):
        """Test registration with duplicate email."""
        with app.app_context():
            user = db.session.get(User, sample_user)
            response = client.post('/auth/register', data={
                'username': 'differentuser',
                'email': user.email,
                'password': 'password123',
                'password2': 'password123'
            })
            
            assert response.status_code == 200
            assert b'Email already registered' in response.data
    
    def test_register_password_mismatch(self, client):
        """Test registration with password mismatch."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'differentpassword'
        })
        
        assert response.status_code == 200
        assert b'Field must be equal to password' in response.data
    
    def test_login_get(self, client):
        """Test login page loads."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_success(self, app, client, sample_user):
        """Test successful login."""
        with app.app_context():
            user = db.session.get(User, sample_user)
            response = client.post('/auth/login', data={
                'username': user.username,
                'password': 'testpassword'
            })
            
            # Should redirect after successful login
            assert response.status_code == 302
    
    def test_login_invalid_username(self, client):
        """Test login with invalid username."""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'password'
        })
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_login_invalid_password(self, app, client, sample_user):
        """Test login with invalid password."""
        with app.app_context():
            user = db.session.get(User, sample_user)
            response = client.post('/auth/login', data={
                'username': user.username,
                'password': 'wrongpassword'
            })
            
            assert response.status_code == 200
            assert b'Invalid username or password' in response.data
    
    def test_logout(self, logged_in_user):
        """Test user logout."""
        response = logged_in_user.get('/auth/logout')
        assert response.status_code == 302
        
        # Try to access protected page after logout
        response = logged_in_user.get('/posts/create')
        assert response.status_code == 302  # Should redirect to login
    
    def test_redirect_to_login_for_protected_routes(self, client):
        """Test that protected routes redirect to login."""
        protected_routes = [
            '/posts/create',
            '/users/edit_profile'
        ]
        
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 302
            assert '/auth/login' in response.location
    
    def test_remember_me_functionality(self, app, client, sample_user):
        """Test remember me checkbox functionality."""
        with app.app_context():
            user = db.session.get(User, sample_user)
            response = client.post('/auth/login', data={
                'username': user.username,
                'password': 'testpassword',
                'remember_me': True
            })
            
            assert response.status_code == 302
