import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Post, Comment, Like
from app.forms import PostForm, CommentForm

posts_bp = Blueprint('posts', __name__)

def save_picture(form_picture, folder):
    """Save uploaded picture with a random name"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads', folder, picture_fn)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    # Resize image
    output_size = (800, 800)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    
    return picture_fn

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        image_file = None
        if form.image.data:
            image_file = save_picture(form.image.data, 'posts')
        
        post = Post(content=form.content.data, image=image_file, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('posts/create_post.html', title='Create Post', form=form)

@posts_bp.route('/<int:id>')
def post_detail(id):
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=id).order_by(Comment.created_at.desc()).all()
    form = CommentForm()
    return render_template('posts/post_detail.html', title='Post', post=post, comments=comments, form=form)

@posts_bp.route('/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
    return redirect(url_for('posts.post_detail', id=id))

@posts_bp.route('/<int:id>/like', methods=['POST'])
@login_required
def toggle_like(id):
    post = Post.query.get_or_404(id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=id).first()
    
    if like:
        # Unlike the post
        db.session.delete(like)
        liked = False
    else:
        # Like the post
        like = Like(user_id=current_user.id, post_id=id)
        db.session.add(like)
        liked = True
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({
            'liked': liked,
            'like_count': post.like_count()
        })
    
    return redirect(request.referrer or url_for('main.index'))

@posts_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        flash('You can only delete your own posts!', 'danger')
        return redirect(url_for('main.index'))
    
    # Delete associated image file
    if post.image:
        image_path = os.path.join(current_app.root_path, 'static/uploads/posts', post.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.index'))
