import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Post
from app.forms import EditProfileForm

users_bp = Blueprint('users', __name__)

def save_avatar(form_picture):
    """Save uploaded avatar with a random name"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads/avatars', picture_fn)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    # Resize image to square
    output_size = (200, 200)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    
    return picture_fn

@users_bp.route('/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('users/profile.html', user=user, posts=posts)

@users_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        # Handle avatar upload
        if form.avatar.data:
            # Delete old avatar if it's not the default
            if current_user.avatar != 'default_avatar.png':
                old_avatar_path = os.path.join(current_app.root_path, 'static/uploads/avatars', current_user.avatar)
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            
            avatar_file = save_avatar(form.avatar.data)
            current_user.avatar = avatar_file
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('users.profile', username=current_user.username))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    
    return render_template('users/edit_profile.html', title='Edit Profile', form=form)

@users_bp.route('/follow/<username>', methods=['POST'])
@login_required 
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('main.index'))
    
    if user == current_user:
        flash('You cannot follow yourself!', 'warning')
        return redirect(url_for('users.profile', username=username))
    
    current_user.follow(user)
    db.session.commit()
    
    if request.is_json:
        return jsonify({
            'following': True,
            'follower_count': user.followers.count()
        })
    
    flash(f'You are now following {username}!', 'success')
    return redirect(url_for('users.profile', username=username))

@users_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('main.index'))
    
    if user == current_user:
        flash('You cannot unfollow yourself!', 'warning')
        return redirect(url_for('users.profile', username=username))
    
    current_user.unfollow(user)
    db.session.commit()
    
    if request.is_json:
        return jsonify({
            'following': False,
            'follower_count': user.followers.count()
        })
    
    flash(f'You are no longer following {username}.', 'info')
    return redirect(url_for('users.profile', username=username))
