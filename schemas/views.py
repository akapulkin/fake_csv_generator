import json

from celery.result import AsyncResult
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.http import Http404, JsonResponse
from .tasks import create_csv
from .models import Schema, SchemaColumn, SchemaDataset
from .choices import TYPES


def login_page(request):
    if request.user.is_authenticated:
        return redirect('schemas')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('schemas')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')


class SchemaListView(ListView):
    template_name = 'schemas.html'
    model = Schema
    queryset = Schema.objects.all()

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super(SchemaListView, self).dispatch(*args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        context = super(SchemaListView, self).get_context_data(**kwargs)
        return context


# TODO UpdateView

class SchemaCreateView(CreateView):
    model = Schema
    fields = ['name', 'column_separator', 'string_character']
    template_name = 'schema_new.html'

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super(SchemaCreateView, self).dispatch(*args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        context = super(SchemaCreateView, self).get_context_data(**kwargs)
        context['status'] = TYPES
        return context

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            schema_data = json.loads(self.request.POST.get('item_text'))
            schema = schema_data['schema']
            columns = schema_data['columns']
            if len(columns) == 0:
                return JsonResponse({'data': False}, safe=False)
            new_schema = Schema(name=schema['id_name'],
                column_separator=schema['id_column_separator'],
                string_character=schema['id_string_character'])
            new_schema.save()
            for key, a in columns.items():
                new_column = SchemaColumn(schema=new_schema, column_name=a['column_name'],
                    column_type=a['type_value'], range_from=a['from_range'],
                    range_to=a['to_range'], order=a['order'])
                new_column.save()
            return JsonResponse({'data': True}, safe=False)
        return Http404


def schema_delete(request, pk):
    try:
        schema = Schema.objects.get(pk=pk)
        schema.delete()
        return redirect("schemas")
    except Schema.DoesNotExist:
        return redirect("schemas")


class SchemaDatasetListView(ListView):
    model = SchemaDataset
    template_name = 'schema_dataset.html'

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_staff or not self.request.user.is_superuser:
            raise Http404
        return super(SchemaDatasetListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return SchemaDataset.objects.filter(schema_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(SchemaDatasetListView, self).get_context_data(**kwargs)
        context['schema_id'] = self.kwargs['pk']
        return context

    def post(self, *args, **kwargs):
        if self.request.is_ajax():
            datasets_task_uuid = json.loads(self.request.POST.get('uuid'))
            response = {}
            for a in datasets_task_uuid['uuid']:
                task_result = AsyncResult(a)
                response[a] = task_result.status
                if task_result.status == 'SUCCESS':
                    schema_dataset = SchemaDataset.objects.get(task_id=a)
                    schema_dataset.status = 'ready'
                    schema_dataset.save()
            return JsonResponse(response, safe=False)
        new_dataset = SchemaDataset(schema_id=self.kwargs['pk'],
                                    rows_quantity=self.request.POST['rows_quant'])
        new_dataset.save()
        schema = new_dataset.schema
        columns = SchemaColumn.objects.filter(schema_id=schema.id).order_by('order')
        columns_data = {'dataset_id': new_dataset.id,
                        'rows_quantity': int(new_dataset.rows_quantity),
                        'delimiter': schema.column_separator,
                        'quotechar': schema.string_character,
                        'columns': {}}
        for col in columns:
            columns_data['columns'][col.column_name] = {'type': col.column_type,
                                                        'from': col.range_from,
                                                        'to': col.range_to}
        task = create_csv.delay(columns_data)
        new_dataset.task_id = task.id
        new_dataset.link = 'https://s3-eu-central-1.amazonaws.com/csvgenerator/'\
                           + str(new_dataset.id) + '.csv'
        new_dataset.save()
        return redirect('schema_datasets', pk=schema.id)

