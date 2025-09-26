import pytest
from app import db
from app.models import Post, User

class TestMain:
    """Test main routes."""
    
    def test_index_anonymous(self, client):
        """Test index page for anonymous user."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Welcome to SocialConnect' in response.data or b'Latest Posts' in response.data
    
    def test_index_logged_in_no_posts(self, logged_in_user):
        """Test index page for logged in user with no posts."""
        response = logged_in_user.get('/')
        assert response.status_code == 200
        assert b'Your Feed' in response.data or b'No posts' in response.data
    
    def test_index_logged_in_with_posts(self, logged_in_user, app, sample_user, sample_post):
        """Test index page shows user's own posts."""
        with app.app_context():
            post = db.session.get(Post, sample_post)
            response = logged_in_user.get('/')
            assert response.status_code == 200
            assert post.content.encode() in response.data
    
    def test_index_shows_followed_posts(self, app, client, sample_user, second_user):
        """Test index shows posts from followed users."""
        # Create posts and follow relationship
        with app.app_context():
            user1 = db.session.get(User, sample_user)
            user2 = db.session.get(User, second_user)
            
            # User1 follows user2
            user1.follow(user2)
            
            # User2 creates a post
            post = Post(content='Post from followed user', author=user2)
            db.session.add(post)
            db.session.commit()
            user1_username = user1.username
        
        # Login as user1 and check feed
        client.post('/auth/login', data={
            'username': user1_username,
            'password': 'testpassword'
        })
        
        response = client.get('/')
        assert response.status_code == 200
        assert b'Post from followed user' in response.data
    
    def test_explore_page(self, client):
        """Test explore page loads."""
        response = client.get('/explore')
        assert response.status_code == 200
        assert b'Explore' in response.data
    
    def test_explore_shows_all_posts(self, client, app, sample_user, sample_post):
        """Test explore page shows posts from all users."""
        with app.app_context():
            post = db.session.get(Post, sample_post)
            response = client.get('/explore')
            assert response.status_code == 200
            assert post.content.encode() in response.data
    
    def test_explore_pagination(self, client, app, sample_user):
        """Test explore page pagination."""
        # Create many posts
        with app.app_context():
            user = db.session.get(User, sample_user)
            for i in range(15):  # More than POSTS_PER_PAGE
                post = Post(content=f'Explore post {i}', author=user)
                db.session.add(post)
            db.session.commit()
        
        # Test first page
        response = client.get('/explore')
        assert response.status_code == 200
        
        # Test second page
        response = client.get('/explore?page=2')
        assert response.status_code == 200
    
    def test_search_page_get(self, client):
        """Test search page loads."""
        response = client.get('/search')
        assert response.status_code == 200
        assert b'Search' in response.data
    
    def test_search_users(self, app, client, sample_user):
        """Test user search functionality."""
        with app.app_context():
            user = db.session.get(User, sample_user)
            response = client.get(f'/search?query={user.username}')
            assert response.status_code == 200
            assert user.username.encode() in response.data
    
    def test_search_partial_username(self, app, client, sample_user):
        """Test searching with partial username."""
        with app.app_context():
            user = db.session.get(User, sample_user)
            partial_name = user.username[:4]  # First 4 characters
            response = client.get(f'/search?query={partial_name}')
            assert response.status_code == 200
            assert user.username.encode() in response.data
    
    def test_search_no_results(self, client):
        """Test search with no results."""
        response = client.get('/search?query=nonexistentuser')
        assert response.status_code == 200
        assert b'No users found' in response.data
    
    def test_search_empty_query(self, client):
        """Test search with empty query."""
        response = client.get('/search?query=')
        assert response.status_code == 200
        # Should show search tips or empty state
        assert b'Find New People' in response.data or b'Search' in response.data
    
    def test_search_pagination(self, client, app):
        """Test search results pagination."""
        # Create many users with similar names
        with app.app_context():
            for i in range(25):  # More than USERS_PER_PAGE
                user = User(
                    username=f'searchuser{i}',
                    email=f'searchuser{i}@example.com'
                )
                user.set_password('password')
                db.session.add(user)
            db.session.commit()
        
        # Test first page
        response = client.get('/search?query=searchuser')
        assert response.status_code == 200
        
        # Test second page
        response = client.get('/search?query=searchuser&page=2')
        assert response.status_code == 200
    
    def test_index_pagination(self, logged_in_user, app, sample_user):
        """Test index page pagination."""
        # Create many posts
        with app.app_context():
            user = db.session.get(User, sample_user)
            for i in range(15):  # More than POSTS_PER_PAGE
                post = Post(content=f'Feed post {i}', author=user)
                db.session.add(post)
            db.session.commit()
        
        # Test first page
        response = logged_in_user.get('/')
        assert response.status_code == 200
        
        # Test second page
        response = logged_in_user.get('/?page=2')
        assert response.status_code == 200
    
    def test_404_error_page(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
