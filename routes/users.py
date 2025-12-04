from flask import Blueprint, render_template, redirect, url_for, request, session
import sqlite3
from services.user_service import create_user, verify_credentials, get_user_by_id
from flask_login import login_user, logout_user, login_required, current_user

bp = Blueprint('users', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip() or None
        last_name = request.form.get('last_name', '').strip() or None
        try:
            user = create_user(
                email=email,
                password=password,
                role="user",
                first_name=first_name,
                last_name=last_name,
            )
            login_user(user)
            return redirect(url_for('users.profile'))
        except sqlite3.IntegrityError:
            error = "Cet email est déjà utilisé."
    return render_template('auth_register.html', error=error)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = verify_credentials(email, password)
        if user:
            login_user(user)
            return redirect(url_for('users.profile'))
        error = "Email ou mot de passe invalide."
    return render_template('auth_login.html', error=error)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


