import pytest
import json
from app import db
from app.models import Post, User, Like, Comment

class TestPosts:
    """Test post-related functionality."""
    
    def test_create_post_get(self, logged_in_user):
        """Test create post page loads for logged in user."""
        response = logged_in_user.get('/posts/create')
        assert response.status_code == 200
        assert b'Create Post' in response.data
    
    def test_create_post_unauthorized(self, client):
        """Test create post redirects for anonymous user."""
        response = client.get('/posts/create')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location
    
    def test_create_post_success(self, logged_in_user, app, sample_user):
        """Test successful post creation."""
        response = logged_in_user.post('/posts/create', data={
            'content': 'This is a test post from the test suite!'
        })
        
        assert response.status_code == 302  # Redirect after creation
        
        # Check post was created in database
        with app.app_context():
            user = db.session.get(User, sample_user)
            post = Post.query.filter_by(content='This is a test post from the test suite!').first()
            assert post is not None
            assert post.author.username == user.username
    
    def test_create_post_empty_content(self, logged_in_user):
        """Test post creation with empty content fails."""
        response = logged_in_user.post('/posts/create', data={
            'content': ''
        })
        
        assert response.status_code == 200  # Should stay on form with errors
        assert b'This field is required' in response.data
    
    def test_create_post_too_long_content(self, logged_in_user):
        """Test post creation with content too long."""
        long_content = 'x' * 501  # Assuming max length is 500
        response = logged_in_user.post('/posts/create', data={
            'content': long_content
        })
        
        assert response.status_code == 200  # Should stay on form with errors
    
    def test_post_detail_view(self, app, client, sample_post):
        """Test viewing a single post."""
        with app.app_context():
            post = db.session.get(Post, sample_post)
            response = client.get(f'/posts/{post.id}')
            assert response.status_code == 200
            assert post.content.encode() in response.data
    
    def test_post_detail_nonexistent(self, client):
        """Test viewing nonexistent post returns 404."""
        response = client.get('/posts/99999')
        assert response.status_code == 404
    
    def test_like_post_ajax(self, logged_in_user, app, sample_post, sample_user):
        """Test liking a post via AJAX."""
        with app.app_context():
            post = db.session.get(Post, sample_post)
            response = logged_in_user.post(
                f'/posts/{post.id}/like',
                headers={'Content-Type': 'application/json'}
            )
            assert response.status_code == 200
            
            # Check response JSON
            data = json.loads(response.data)
            assert data['liked'] == True
            assert data['like_count'] == 1
            
            # Check database
            post = db.session.get(Post, sample_post)
            user = db.session.get(User, sample_user)
            assert user.has_liked_post(post)
    
    def test_unlike_post_ajax(self, logged_in_user, app, sample_post, sample_user):
        """Test unliking a post via AJAX."""
        # First like the post
        with app.app_context():
            like = Like(user_id=sample_user, post_id=sample_post)
            db.session.add(like)
            db.session.commit()
            post = db.session.get(Post, sample_post)
        
        # Then unlike it
        response = logged_in_user.post(
            f'/posts/{post.id}/like',
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['liked'] == False
        assert data['like_count'] == 0
    
    def test_like_post_unauthorized(self, app, client, sample_post):
        """Test liking post without authentication."""
        with app.app_context():
            post = db.session.get(Post, sample_post)
            response = client.post(f'/posts/{post.id}/like')
            assert response.status_code == 302  # Redirect to login
    
    def test_add_comment(self, logged_in_user, app, sample_post):
        """Test adding a comment to a post."""
        with app.app_context():
            post = db.session.get(Post, sample_post)
            response = logged_in_user.post(f'/posts/{post.id}/comment', data={
                'content': 'This is a test comment!'
            })
            
            assert response.status_code == 302  # Redirect after comment
            
            # Check comment was created
            post = db.session.get(Post, sample_post)
            assert post.comment_count() == 1
            comment = post.comments.first()
            assert comment.content == 'This is a test comment!'
    
    def test_add_empty_comment(self, app, logged_in_user, sample_post):
        """Test adding empty comment fails."""
        with app.app_context():
            post = db.session.get(Post, sample_post)
            response = logged_in_user.post(f'/posts/{post.id}/comment', data={
                'content': ''
            })
            
            # Should redirect back with error (flash message)
            assert response.status_code == 302
    
    def test_comment_unauthorized(self, app, client, sample_post):
        """Test commenting without authentication."""
        with app.app_context():
            post = db.session.get(Post, sample_post)
            response = client.post(f'/posts/{post.id}/comment', data={
                'content': 'Test comment'
            })
            assert response.status_code == 302  # Redirect to login
    
    def test_delete_own_post(self, logged_in_user, app, sample_post):
        """Test deleting own post."""
        with app.app_context():
            post = db.session.get(Post, sample_post)
            response = logged_in_user.post(f'/posts/{post.id}/delete')
            assert response.status_code == 302
            
            # Check post was deleted
            post = db.session.get(Post, sample_post)
            assert post is None
    
    def test_delete_other_user_post(self, app, client, sample_post):
        """Test cannot delete another user's post."""
        # Create and login as different user
        with app.app_context():
            other_user = User(username='otheruser', email='other@example.com')
            other_user.set_password('password')
            db.session.add(other_user)
            db.session.commit()
            post = db.session.get(Post, sample_post)
        
        # Login as other user
        client.post('/auth/login', data={
            'username': 'otheruser',
            'password': 'password'
        })
        
        response = client.post(f'/posts/{post.id}/delete')
        assert response.status_code == 302  # Redirect with error
        
        # Check post still exists
        with app.app_context():
            post = db.session.get(Post, sample_post)
            assert post is not None
    
    def test_delete_post_unauthorized(self, app, client, sample_post):
        """Test deleting post without authentication."""
        with app.app_context():
            post = db.session.get(Post, sample_post)
            response = client.post(f'/posts/{post.id}/delete')
            assert response.status_code == 302  # Redirect to login
    
    def test_delete_nonexistent_post(self, logged_in_user):
        """Test deleting nonexistent post."""
        response = logged_in_user.post('/posts/99999/delete')
        assert response.status_code == 404
