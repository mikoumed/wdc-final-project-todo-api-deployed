def serialize_todo_as_json(todo):
    return {
        'id' : todo.id,
        'title': todo.title,
        'completed': todo.completed
    }
