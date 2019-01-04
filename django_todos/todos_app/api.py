import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Todo
from todos_app.serializers import serialize_todo_as_json


class BaseCSRFExemptView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TodoListView(BaseCSRFExemptView):
    def get(self, request):
        todos = Todo.objects.all()
        filter = request.GET.get('status', 'all')

        if filter == 'completed':
            todos = todos.filter(completed=True)
        if filter == 'active':
            todos = todos.filter(completed=False)

        todos = [serialize_todo_as_json(todo) for todo in todos]
        count = len(todos)
        return JsonResponse({
            'count' : count,
            'filter': filter,
            'results' : todos,
        })

    def post(self, request):
        payload = json.loads(request.body)
        if 'title' not in payload:
            return JsonResponse({
                'msg' : 'not a valid format'
            }, status=400)
        title = payload['title']
        completed = payload.get('completed', False)
        todo = Todo.objects.create(title=title, completed=completed)
        return JsonResponse({
            'msg': 'todo created'
        }, status=201)


class TodoDetailView(BaseCSRFExemptView):
    def get(self, request, todo_id):
        todo = get_object_or_404(Todo, id=todo_id)
        todo = serialize_todo_as_json(todo)
        return JsonResponse(todo, status=200)

    def delete(self, request, todo_id):
        todo = get_object_or_404(Todo, id=todo_id)
        todo.delete()
        return HttpResponse(status=204)


    def patch(self, request, todo_id):
        payload = json.loads(request.body)
        todo = get_object_or_404(Todo, id=todo_id)

        if payload.get('action') == 'toggle':
            todo.completed = not todo.completed

        else:
            if 'title' in payload:
                todo.title = payload['title']
            if 'completed' in payload:
                todo.completed = payload['completed']

        todo.save()
        todo = serialize_todo_as_json(todo)
        return JsonResponse(todo, status=200)

    def put(self, request, todo_id):
        payload = json.loads(request.body)
        todo = get_object_or_404(Todo, id=todo_id)

        for field in ['title', 'completed']:
            if not field in payload:
                return JsonResponse({
                        'error': 'Missing argument: {}'.format(field)},
                        status=400)
            try:
                setattr(todo,field,payload[field])
                todo.save()
            except ValueError:
                return JsonResponse(
                    {"success": False, "msg": "Provided payload is not valid"},
                    status=400)
        todo = serialize_todo_as_json(todo)
        return HttpResponse(status=204)
