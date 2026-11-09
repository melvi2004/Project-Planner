from django.shortcuts import render

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView

from . models import Project

from . models import AssignedProjects

from.serializers  import ProjectSerializer

from rest_framework.response import Response

from . serializers import AssignedProjectsSerializer

from . serializers import TaskSerializer

from . models import Task

from rest_framework.views import APIView

from planner.utils import generate_tasks

from django.db import transaction

from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.permissions import IsAdmin,IsDeveloper,IsProjectCoordinator

from rest_framework.permissions import IsAuthenticated

# Create your views here.

class ProjectListCreateView(ListCreateAPIView):

    queryset=Project.objects.filter(active_status=True)

    serializer_class=ProjectSerializer

    authentication_classes=[JWTAuthentication]

    def get_permissions(self):

        permissions=[]

        if self.request.method in ['POST']:

            permissions=[IsAdmin]

        else:

             permissions=[IsAuthenticated] 

        return [permission() for permission in permissions]        

class ProjectRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    lookup_field='uuid'

    queryset=Project.objects.filter(active_status=True)

    serializer_class=ProjectSerializer

    authentication_classes=[JWTAuthentication]
    
    def get_permissions(self):
    
            permissions=[]
    
            if self.request.method in ['PATCH','DELETE']:
    
                permissions=[IsAdmin]
    
            else:
    
                 permissions=[IsAuthenticated] 
    
            return [permission() for permission in permissions]        
    

    def perform_destroy(self, instance):

        instance.active_status=False

        instance.save()

class AssignedProjectsListCreateView(ListCreateAPIView):

    queryset=   AssignedProjects.objects.filter(active_status=True).select_related('project','coordinator').prefetch_related('developers')

    serializer_class= AssignedProjectsSerializer 

    authentication_classes=[JWTAuthentication]
    
    def get_permissions(self):
    
            permissions=[]
    
            if self.request.method in ['POST']:
    
                permissions=[IsAdmin,IsProjectCoordinator]
    
            else:
    
                 permissions=[IsAuthenticated] 
    
            return [permission() for permission in permissions]        
     

class AssignedProjectRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    lookup_field='uuid'

    queryset=AssignedProjects.objects.filter(active_status=True).select_related('project','coordinator').prefetch_related('developers')

    serializer_class=AssignedProjectsSerializer

    authentication_classes=[JWTAuthentication]
    
    def get_permissions(self):
    
            permissions=[]
    
            if self.request.method in ['PATCH','DELETE']:
    
                permissions=[IsAdmin]
    
            else:
    
                 permissions=[IsAuthenticated] 
    
            return [permission() for permission in permissions]        
    

    def perform_destroy(self, instance):
    
            instance.active_status=False
    
            instance.save()

class TaskListCreateView(ListCreateAPIView): 
    
    serializer_class=TaskSerializer

    authentication_classes=[JWTAuthentication]
    
    def get_permissions(self):
    
            permissions=[]
    
            if self.request.method in ['POST']:
    
                permissions=[IsProjectCoordinator]
    
            else:
    
                 permissions=[IsAuthenticated] 
    
            return [permission() for permission in permissions]        
    
    
    def get_queryset(self):
        
        uuid=self.kwargs.get('uuid')
        
        assigned_projects=AssignedProjects.objects.get(uuid=uuid)
        
        tasks=Task.objects.filter(active_status=True,assigned_projects=assigned_projects)
        
        return tasks


    def perform_create(self,serializer):

        uuid=self.kwargs.get('uuid')

        assigned_projects=AssignedProjects.objects.get(uuid=uuid)

        serializer.save(assigned_projects=assigned_projects)

class TaskRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    lookup_field = 'uuid'

    queryset = Task.objects.filter(active_status=True).select_related('assigned_projects','assigned_to')

    serializer_class = TaskSerializer

    authentication_classes=[JWTAuthentication]
    
    def get_permissions(self):
    
            permissions=[]
    
            if self.request.method in ['PATCH','DELETE']:
    
                permissions=[IsAdmin]
    
            else:
    
                 permissions=[IsAuthenticated] 
    
            return [permission() for permission in permissions]        
    

    def perform_destroy(self, instance):
        
        instance.active_status=False
        
        instance.save()

class GenerateTasksWithAIView(APIView):

    authentication_classes=[JWTAuthentication]

    permission_classes=[IsProjectCoordinator]

    def post(self,request,*args,**kwargs):

        uuid=kwargs.get('uuid')

        assigned_projects=AssignedProjects.objects.get(uuid=uuid) 

        response=generate_tasks(assigned_projects)

        tasks=[Task(
                    assigned_projects=assigned_projects,
                    assigned_to=task.developer_id,
                    title=task.title,
                    description=task.description,
                    priority=task.priority
                    )
        for task in response.tasks]

        with transaction.atomic():

                   Task.objects.bulk_create(tasks)
        
        return Response(status=200)

        
               
    




                    

  

        