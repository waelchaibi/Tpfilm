from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from services.user_service import (
    list_users, get_user_by_id, update_user, delete_user, create_user,
    count_users, count_active_users
)

def roles_required(roles: list[str]):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("Accès refusé.", "error")
                return redirect(url_for('users.login'))
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def create_admin_blueprint(movie_service):
    bp = Blueprint('admin', __name__, url_prefix='/admin')

    @bp.route('/')
    @roles_required(['admin'])
    def dashboard():
        total_users = count_users()
        active_users = count_active_users()
        # movies stats
        stats = movie_service.get_consolidation_stats()
        return render_template('admin/dashboard.html',
                               total_users=total_users,
                               active_users=active_users,
                               movie_stats=stats)

    # Users list
    @bp.route('/users')
    @roles_required(['admin'])
    def users_list():
        q = request.args.get('q')
        page = request.args.get('page', 1, type=int)
        users, has_next = list_users(q, page, 20)
        return render_template('admin/users_list.html', users=users, q=q, page=page, has_next=has_next)

    @bp.route('/users/new', methods=['GET', 'POST'])
    @roles_required(['admin'])
    def users_new():
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            role = request.form.get('role') or 'user'
            first_name = request.form.get('first_name') or None
            last_name = request.form.get('last_name') or None
            is_active = request.form.get('is_active') == 'on'
            create_user(email=email, password=password, role=role,
                        first_name=first_name, last_name=last_name, is_active=is_active)
            return redirect(url_for('admin.users_list'))
        return render_template('admin/users_form.html', form_mode='create', user=None)

    @bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
    @roles_required(['admin'])
    def users_edit(user_id: int):
        user = get_user_by_id(user_id)
        if not user:
            return redirect(url_for('admin.users_list'))
        if request.method == 'POST':
            updates = dict()
            email = request.form.get('email', '').strip()
            role = request.form.get('role') or user.role
            first_name = request.form.get('first_name') or None
            last_name = request.form.get('last_name') or None
            is_active = request.form.get('is_active')
            if email: updates['email'] = email
            updates['role'] = role
            updates['first_name'] = first_name
            updates['last_name'] = last_name
            if is_active is not None:
                updates['is_active'] = (is_active == 'on')
            password = request.form.get('password')
            if password:
                updates['password'] = password
            update_user(user_id, **updates)
            return redirect(url_for('admin.users_list'))
        return render_template('admin/users_form.html', form_mode='edit', user=user)

    @bp.route('/users/<int:user_id>/delete', methods=['POST'])
    @roles_required(['admin'])
    def users_delete(user_id: int):
        delete_user(user_id)
        return redirect(url_for('admin.users_list'))

    # Movies
    @bp.route('/movies')
    @roles_required(['admin'])
    def movies_list():
        q = request.args.get('q')
        page = request.args.get('page', 1, type=int)
        movies, has_next = movie_service.list_movies(q, page, 20)
        return render_template('admin/movies_list.html', movies=movies, q=q, page=page, has_next=has_next)

    @bp.route('/movies/new', methods=['GET', 'POST'])
    @roles_required(['admin'])
    def movies_new():
        if request.method == 'POST':
            data = {
                "show_id": request.form.get('show_id', '').strip(),
                "type": request.form.get('type', '').strip() or None,
                "title": request.form.get('title', '').strip(),
                "director": request.form.get('director', '').strip() or None,
                "cast": request.form.get('cast', '').strip() or None,
                "country": request.form.get('country', '').strip() or None,
                "date_added": request.form.get('date_added', '').strip() or None,
                "release_year": request.form.get('release_year', type=int),
                "rating": request.form.get('rating', '').strip() or None,
                "duration": request.form.get('duration', '').strip() or None,
                "listed_in": request.form.get('listed_in', '').strip() or None,
                "description": request.form.get('description', '').strip() or None,
            }
            movie_service.create_movie(data)
            return redirect(url_for('admin.movies_list'))
        return render_template('admin/movies_form.html', form_mode='create', movie=None)

    @bp.route('/movies/<string:show_id>/edit', methods=['GET', 'POST'])
    @roles_required(['admin'])
    def movies_edit(show_id: str):
        mv = movie_service.get_movie_by_id(show_id)
        if not mv:
            return redirect(url_for('admin.movies_list'))
        if request.method == 'POST':
            updates = {
                "type": request.form.get('type', '').strip() or None,
                "title": request.form.get('title', '').strip(),
                "director": request.form.get('director', '').strip() or None,
                "cast": request.form.get('cast', '').strip() or None,
                "country": request.form.get('country', '').strip() or None,
                "date_added": request.form.get('date_added', '').strip() or None,
                "release_year": request.form.get('release_year', type=int),
                "rating": request.form.get('rating', '').strip() or None,
                "duration": request.form.get('duration', '').strip() or None,
                "listed_in": request.form.get('listed_in', '').strip() or None,
                "description": request.form.get('description', '').strip() or None,
            }
            movie_service.update_movie(show_id, updates)
            return redirect(url_for('admin.movies_list'))
        return render_template('admin/movies_form.html', form_mode='edit', movie=mv)

    @bp.route('/movies/<string:show_id>/delete', methods=['POST'])
    @roles_required(['admin'])
    def movies_delete(show_id: str):
        movie_service.delete_movie(show_id)
        return redirect(url_for('admin.movies_list'))

    return bp


