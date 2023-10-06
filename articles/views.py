from django.shortcuts import render, get_object_or_404
from .models import *
from .serializers import *
from rest_framework import viewsets, status, generics, mixins, filters
# Create your views here.
import datetime
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def modify_article(request):

    if request.method == 'POST':
        article = Article.objects.get(pk=request.GET.get('article_pk'))
        check_result = {}
        if request.GET.get('password') == article.password:
            check_result['result'] = 'True'

            return check_result
        
        else:
            check_result['result'] = 'False'

            return check_result



class ArticleView(viewsets.ModelViewSet):

    queryset = Article.objects.all().order_by('-pk')
    serializer_class = ArticleSerializer

    def retrieve(self, request, pk=None, *args, **kwargs):
        # 조회수
        instance = get_object_or_404(self.get_queryset(),pk=pk)
        instance.hits_field +=1
        instance.save()
        
        return super().retrieve(request, *args, **kwargs)
    
    
    

class CommentView(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().order_by('-pk')

    def perform_create(self, serializer):

        serializer.save(
            article=Article.objects.get(pk=self.kwargs.get("article_pk")),
        )

