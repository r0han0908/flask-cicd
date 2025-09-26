import pytest
import tempfile
import os
from app import create_app, db
from app.models import User, Post, Comment, Like

@pytest.fixture
def app():
    """Create application for testing."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'UPLOAD_FOLDER': tempfile.mkdtemp()
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test runner."""
    return app.test_cli_runner()

@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            bio='Test bio'
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
    # Return just the ID, tests can query for the user when needed
    return user_id

@pytest.fixture
def second_user(app):
    """Create a second user for testing follow functionality."""
    with app.app_context():
        user = User(
            username='seconduser',
            email='second@example.com',
            bio='Second user bio'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
    return user_id

@pytest.fixture
def sample_post(app, sample_user):
    """Create a sample post for testing."""
    with app.app_context():
        user = db.session.get(User, sample_user)
        post = Post(
            content='This is a test post',
            author=user
        )
        db.session.add(post)
        db.session.commit()
        post_id = post.id
        
    return post_id

@pytest.fixture
def logged_in_user(app, client, sample_user):
    """Create a logged-in user for testing."""
    with app.app_context():
        user = db.session.get(User, sample_user)
        client.post('/auth/login', data={
            'username': user.username,
            'password': 'testpassword'
        })
    return client
