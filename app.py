import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, make_response

app = Flask(__name__)

def get_common_data():
    username = request.cookies.get('username', '')
    theme = request.cookies.get('theme', 'light')
    last_visit = request.cookies.get('last_visit', 'Це ваше перше відвідування')
    return username, theme, last_visit

def update_last_visit(response):
    now = datetime.now().strftime("%d.%m.%Y о %H:%M:%S")
    response.set_cookie('last_visit', now, max_age=60*60*24*30)
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    username, theme, last_visit = get_common_data()

    if request.method == 'POST':
        new_name = request.form.get('username', '').strip()
        new_theme = request.form.get('theme', 'light')
        
        resp = make_response(redirect(url_for('index')))
        if new_name:
            resp.set_cookie('username', new_name, max_age=60*60*24*30)
        resp.set_cookie('theme', new_theme, max_age=60*60*24*30)
        return update_last_visit(resp)

    resp = make_response(render_template(
        'index.html',
        username=username,
        theme=theme,
        last_visit=last_visit
    ))
    return update_last_visit(resp)

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    username, theme, last_visit = get_common_data()
    
    tasks_cookie = request.cookies.get('tasks', '[]')
    try:
        task_list = json.loads(tasks_cookie)
    except json.JSONDecodeError:
        task_list = []

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            new_task = request.form.get('task', '').strip()
            if new_task:
                task_list.append(new_task)
                
        elif action == 'delete':
            index_to_delete = int(request.form.get('index', -1))
            if 0 <= index_to_delete < len(task_list):
                task_list.pop(index_to_delete)

        resp = make_response(redirect(url_for('tasks')))
        resp.set_cookie('tasks', json.dumps(task_list), max_age=60*60*24*30)
        return update_last_visit(resp)

    resp = make_response(render_template(
        'tasks.html',
        username=username,
        theme=theme,
        tasks=task_list,
        total_tasks=len(task_list)
    ))
    return update_last_visit(resp)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    username, theme, last_visit = get_common_data()

    if request.method == 'POST':
        action = request.form.get('action')
        resp = make_response(redirect(url_for('settings')))

        if action == 'change_theme':
            new_theme = request.form.get('theme', 'light')
            resp.set_cookie('theme', new_theme, max_age=60*60*24*30)
            
        elif action == 'delete_name':
            resp.delete_cookie('username')
            
        elif action == 'clear_tasks':
            resp.delete_cookie('tasks')
            
        elif action == 'delete_dark_theme':
            if theme == 'dark':
                resp.delete_cookie('theme')

        return update_last_visit(resp)

    resp = make_response(render_template(
        'settings.html',
        username=username,
        theme=theme
    ))
    return update_last_visit(resp)

if __name__ == '__main__':
    app.run(debug=True)