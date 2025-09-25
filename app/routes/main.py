from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from app.models import User, Post
from app.forms import SearchForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    if current_user.is_authenticated:
        posts = current_user.followed_posts().paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    else:
        posts = Post.query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    
    return render_template('index.html', title='Home', posts=posts)

@main_bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('explore.html', title='Explore', posts=posts)

@main_bp.route('/search')
def search():
    form = SearchForm()
    users = []
    
    if request.args.get('query'):
        query = request.args.get('query')
        page = request.args.get('page', 1, type=int)
        users = User.query.filter(
            User.username.contains(query)).paginate(
                page=page, per_page=current_app.config['USERS_PER_PAGE'], error_out=False)
    
    return render_template('search.html', title='Search', form=form, users=users)
