# from rest_framework import serializers

# from.models import Project

# from.models import AssignedProjects

# class ProjectSerializer(serializers.ModelSerializer):

#     class Meta:

#         model=Project

#         fields='__all__'

#         read_only_fields = ['active_status']

# class AssignedProjectsSerializer(serializers.ModelSerializer):

#     class Meta:

#         model=Project

#         fields='__all__'

#         read_only_fields = ['active_status']        
from rest_framework import serializers


from .models import Project
from .models import AssignedProjects

from authentication.models import Profile
from authentication.serializers import ProfileSerializer
from.models import Task

class ProjectSerializer(serializers.ModelSerializer):

    class Meta:

        model = Project

        fields = '__all__'
        read_only_fields = ['active_status']

class ProjectField(serializers.PrimaryKeyRelatedField):

    def get_attribute(self, instance):

        return getattr(instance,self.source_attrs[0])

    def to_representation(self, value):
        return ProjectSerializer(value).data
       #this is to convert that instance (category object) into json format

class ProfileField(serializers.PrimaryKeyRelatedField):

    def get_attribute(self, instance):

        return getattr(instance,self.source_attrs[0])

    def to_representation(self, value):
        return ProfileSerializer(value).data
       #this is to convert that instance (category object) into json format

class AssignedProjectsSerializer(serializers.ModelSerializer):

    project = ProjectField(queryset=Project.objects.all())

    coordinator = ProfileField(queryset=Profile.objects.filter(role = 'Project_Coordinator'))
    
    developers = ProfileField(queryset=Profile.objects.filter(role='developer'),many=True)

    class Meta:

        model = AssignedProjects

        fields = '__all__'
        read_only_fields = ['active_status']

class AssignedProjectField(serializers.PrimaryKeyRelatedField):

    def get_attribute(self, instance):

        return getattr(instance,self.source_attrs[0])

    def to_representation(self, value):
        return AssignedProjectsSerializer(value).data        






class TaskSerializer(serializers.ModelSerializer):

    assigned_projects=AssignedProjectField(read_only=True)

    assigned_to=ProfileField(queryset=Profile.objects.filter(role='Developer'))
    
   

    class Meta:

        model=Task
        
        fields = '__all__'
        read_only_fields = ['active_status']        