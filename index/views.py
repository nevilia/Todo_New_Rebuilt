from typing import Any, Dict
from django.shortcuts import redirect, render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

# Create your views here.


class Login(LoginView):
    template_name = 'index/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self) -> str:
        return reverse_lazy('tasks')
    
    
class RegisterPage(FormView):
    template_name = 'index/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user) #from imports
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args,**kwargs)

    
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]: # overwriting it to change who can view the data
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user) #making sure only the logged in user can see the data
        context['count'] = context['tasks'].filter(complete = False).count() #only the count of stuff which is not complete
        
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__icontains = search_input) # filter(title__startswith = search_input) for filtering words that start with the input
        
        context['search_input'] = search_input
        return context
    
class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"
    template_name = 'index/task.html'
    
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks') #url name tasks ie TaskList class
    
    def form_valid(self, form): #setting validity of create form to only the logged in user
        form.instance.user = self.request.user #making sure we have who is logged in and sending that value to the instance
        return super(TaskCreate, self).form_valid(form)    
    
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    
class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    
