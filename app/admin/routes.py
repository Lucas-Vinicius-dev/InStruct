from flask import render_template, redirect, url_for, flash, session
import csv
import os
from app.admin import admin_bp

ADMIN_USERS = ['harry1', 'admin']

def is_admin():
    user = session.get('usuario_logado')
    return user in ADMIN_USERS

def read_csv(filename):
    data = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    return data

def write_csv(filename, fieldnames, data):
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

@admin_bp.route('/dashboard')
def dashboard():
    if not is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.home'))
    
    usuarios = []
    posts = []
    comentarios = []
    
    # USERS
    if os.path.exists('data/usuarios.csv'):
        with open('data/usuarios.csv', 'r', encoding='utf-8') as f:
            content = f.readlines()[1:]
            for line in content:
                if line.strip():
                    parts = line.split(';')
                    usuarios.append({
                        'name': parts[0],
                        'username': parts[2],
                        'email': parts[1],
                        'is_admin': parts[2] in ADMIN_USERS
                    })
    
    # POSTS
    posts = read_csv('data/publish_data.csv')
    for idx, post in enumerate(posts):
        post['id'] = idx
    
    # COMENTARIOS
    comments = read_csv('data/comments_data.csv')
    for idx, c in enumerate(comments):
        comentarios.append({
            'id': idx,
            'author': c.get('username', ''),
            'content': c.get('comment_text', ''),
            'post_id': c.get('post_title', '')
        })
    
    return render_template( 'admin/dashboard.html', 
                         usuarios=usuarios, 
                         posts=posts, 
                         comentarios=comentarios)

@admin_bp.route('/delete-user/<username>', methods=['POST'])
def delete_user(username):
    if not is_admin():
        return redirect(url_for('main.home'))
    
    if username == session.get('usuario_logado'):
        flash('Não pode excluir sua própria conta.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    if username in ADMIN_USERS:
        flash('Não pode excluir admin.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    usuarios_novo = []
    with open('data/usuarios.csv', 'r', encoding='utf-8') as f:
        content = f.readlines()[1:]
        for line in content:
            if line.strip():
                parts = line.split(';')
                if parts[2] != username:
                    usuarios_novo.append(line)
    
    with open('data/usuarios.csv', 'w', encoding='utf-8') as f:
        f.write('nome_completo;email;nome_usuario;senha;bio;localizacao;link_github;avatar\n')
        f.writelines(usuarios_novo)
    
    flash(f'Usuário {username} deletado.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete-post/<int:post_id>', methods=['POST'])
def delete_post( post_id):
    if not is_admin():
        return redirect(url_for('main.home'))
    
    posts = read_csv('data/publish_data.csv')
    fieldnames = ['username' , 'title', 'description', 'topico_principal', 'tipo_de_post', 'linguagem_selecionada', 'image', 'visibility']
    
    if post_id < len(posts):
        post_titulo = posts[post_id].get('title', '')
        posts.pop(post_id)
        write_csv('data/publish_data.csv' , fieldnames, posts)
        
        comments = read_csv('data/comments_data.csv')
        comments_novo = [c for c in comments if c.get('post_title') != post_titulo]
        comment_fieldnames = ['post_title', 'username', 'comment_text', 'timestamp']
        write_csv('data/comments_data.csv', comment_fieldnames, comments_novo)
        
        flash('Post deletado.', 'success')
    else:
        flash('Post não encontrado.', 'warning')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete-comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if not is_admin():
        return redirect(url_for('main.home'))
    
    comments = read_csv('data/comments_data.csv')
    fieldnames = ['post_title', 'username', 'comment_text', 'timestamp']
    
    if comment_id < len(comments):
        comments.pop(comment_id)
        write_csv('data/comments_data.csv', fieldnames, comments)
        flash('Comentário deletado.', 'success')
    else:
        flash('Comentário não encontrado.', 'warning')
    
    return redirect(url_for('admin.dashboard'))