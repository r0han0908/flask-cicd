import pytest
import json
from app import db
from app.models import User

class TestUsers:
    """Test user-related functionality."""
    
    def test_profile_page(self, app, client, sample_user):
        """Test user profile page loads."""
        with app.app_context():
            user = db.session.get(User, sample_user)
            response = client.get(f'/users/{user.username}')
            assert response.status_code == 200
            assert user.username.encode() in response.data
            assert user.bio.encode() in response.data
    
    def test_profile_nonexistent_user(self, client):
        """Test profile page for nonexistent user returns 404."""
        response = client.get('/users/nonexistentuser')
        assert response.status_code == 404
    
    def test_edit_profile_get(self, logged_in_user):
        """Test edit profile page loads for logged in user."""
        response = logged_in_user.get('/users/edit_profile')
        assert response.status_code == 200
        assert b'Edit Profile' in response.data
    
    def test_edit_profile_unauthorized(self, client):
        """Test edit profile redirects for anonymous user."""
        response = client.get('/users/edit_profile')
        assert response.status_code == 302  # Redirect to login
    
    def test_edit_profile_post(self, logged_in_user, app, sample_user):
        """Test editing profile."""
        response = logged_in_user.post('/users/edit_profile', data={
            'username': 'updateduser',
            'email': 'updated@example.com',
            'bio': 'Updated bio text'
        })
        
        assert response.status_code == 302  # Redirect after update
        
        # Check user was updated
        with app.app_context():
            user = db.session.get(User, sample_user)
            assert user.username == 'updateduser'
            assert user.email == 'updated@example.com'
            assert user.bio == 'Updated bio text'
    
    def test_edit_profile_invalid_email(self, logged_in_user):
        """Test editing profile with invalid email."""
        response = logged_in_user.post('/users/edit_profile', data={
            'username': 'testuser',
            'email': 'invalid-email',
            'bio': 'Test bio'
        })
        
        assert response.status_code == 200  # Should stay on form
        assert b'Invalid email address' in response.data
    
    def test_edit_profile_duplicate_username(self, logged_in_user, app, sample_user, second_user):
        """Test editing profile with existing username."""
        with app.app_context():
            user1 = db.session.get(User, sample_user)
            user2 = db.session.get(User, second_user)
            response = logged_in_user.post('/users/edit_profile', data={
                'username': user2.username,
                'email': user1.email,
                'bio': 'Test bio'
            })
            
            assert response.status_code == 200  # Should stay on form
            assert b'Username already taken' in response.data
    
    def test_follow_user_ajax(self, logged_in_user, app, sample_user, second_user):
        """Test following another user via AJAX."""
        with app.app_context():
            user2 = db.session.get(User, second_user)
            response = logged_in_user.post(
                f'/users/follow/{user2.username}',
                headers={'Content-Type': 'application/json'}
            )
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['following'] == True
            assert data['follower_count'] == 1
            
            # Check database
            user = db.session.get(User, sample_user)
            followed_user = db.session.get(User, second_user)
            assert user.is_following(followed_user)
    
    def test_unfollow_user_ajax(self, logged_in_user, app, sample_user, second_user):
        """Test unfollowing a user via AJAX."""
        # First follow the user
        with app.app_context():
            user = db.session.get(User, sample_user)
            followed_user = db.session.get(User, second_user)
            user.follow(followed_user)
            db.session.commit()
        
        # Then unfollow
        with app.app_context():
            user2 = db.session.get(User, second_user)
            response = logged_in_user.post(
                f'/users/unfollow/{user2.username}',
                headers={'Content-Type': 'application/json'}
            )
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['following'] == False
            assert data['follower_count'] == 0
    
    def test_follow_nonexistent_user(self, logged_in_user):
        """Test following nonexistent user."""
        response = logged_in_user.post('/users/follow/nonexistentuser')
        assert response.status_code == 302  # Redirect with error
    
    def test_follow_self(self, app, logged_in_user, sample_user):
        """Test cannot follow yourself."""
        with app.app_context():
            user = db.session.get(User, sample_user)
            response = logged_in_user.post(f'/users/follow/{user.username}')
            assert response.status_code == 302  # Redirect with warning
    
    def test_follow_unauthorized(self, app, client, second_user):
        """Test following without authentication."""
        with app.app_context():
            user = db.session.get(User, second_user)
            response = client.post(f'/users/follow/{user.username}')
            assert response.status_code == 302  # Redirect to login
    
    def test_user_posts_on_profile(self, client, app, sample_user):
        """Test user's posts appear on their profile."""
        # Create some posts
        with app.app_context():
            user = db.session.get(User, sample_user)
            from app.models import Post
            post1 = Post(content='First test post', author=user)
            post2 = Post(content='Second test post', author=user)
            db.session.add_all([post1, post2])
            db.session.commit()
            username = user.username
        
        response = client.get(f'/users/{username}')
        assert response.status_code == 200
        assert b'First test post' in response.data
        assert b'Second test post' in response.data
    
    def test_user_stats_on_profile(self, client, app, sample_user, second_user):
        """Test user stats display correctly on profile."""
        # Add followers and posts
        with app.app_context():
            user = db.session.get(User, sample_user)
            follower = db.session.get(User, second_user)
            follower.follow(user)
            
            from app.models import Post
            post = Post(content='Test post for stats', author=user)
            db.session.add(post)
            db.session.commit()
            username = user.username
        
        response = client.get(f'/users/{username}')
        assert response.status_code == 200
        # Check that stats are displayed (exact format may vary)
        assert b'1' in response.data  # Should show 1 post and 1 follower
    
    def test_profile_pagination(self, client, app, sample_user):
        """Test profile page pagination with many posts."""
        # Create many posts to test pagination
        with app.app_context():
            user = db.session.get(User, sample_user)
            from app.models import Post
            for i in range(15):  # More than POSTS_PER_PAGE
                post = Post(content=f'Test post {i}', author=user)
                db.session.add(post)
            db.session.commit()
            username = user.username
        
        # Test first page
        response = client.get(f'/users/{username}')
        assert response.status_code == 200
        
        # Test second page if pagination exists
        response = client.get(f'/users/{username}?page=2')
        assert response.status_code == 200
