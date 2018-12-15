# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-12-14 16:47:56
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-14 17:07:53
# --------------------------------------------
from rest_framework import generics
from registry.models import Project

from .serializers import ProjectSerializer, ReleaseSerializer


class ProjectListAPIView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ReleaseListAPIView(generics.ListAPIView):
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer
