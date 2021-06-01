from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils.regex_helper import contains
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from .models import Task
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin           #LoginRequiredMixin will restrict user from accessing pages without logging in
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


class CustomLoginView(LoginView):          
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')



class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm                         #builtin user creation form
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')               #redirecting registered user to tasks page

    def form_valid(self, form):
        user = form.save()                #user detaisl saved after registration
        if user is not None:                
            login(self.request, user)       #login directly after registering
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):                 #function to restrict loggedin users from accessing register page
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

    
class TaskList(LoginRequiredMixin ,ListView):              #LoginRequiredMixin argument will restrict TaskList page from accessing without logging in
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):                      #function to pass user specific data
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)       #filtering tasks user specific
        context['count'] = context['tasks'].filter(complete=False).count()         #counting incomplete tasks

        search_input = self.request.GET.get('search-area') or ''                    #storing serch input from sear-area in search_input
        if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith = search_input) #fitering tasks according to search_input
        
        context['search_input'] = search_input
        return context

class TaskDetail(LoginRequiredMixin ,DetailView):           
    model = Task
    context_object_name = 'task'
    template_name= 'base/task.html'

class TaskCreate(LoginRequiredMixin ,CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):                #built in function to automatically trigger added task to logedin user
        form.instance.user = self.request.user
        return super(TaskCreate , self).form_valid(form)

class TaskUpdate(LoginRequiredMixin ,UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
