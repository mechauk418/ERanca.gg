from rest_framework import serializers
from .models import *



class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            'pk',
            'content',
            'created_at',
            'article',
            'createuser',
            'password'
        ]


class PostImageSerializers(serializers.ModelSerializer):

    class Meta:
        model = PostImage
        fields = [
            'image',
            'image_original'
        ]


class ArticleSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    hits = serializers.ReadOnlyField(source = 'hits_field')
    comments = CommentSerializer(many=True, read_only=True)

    def get_images(self,obj):
        image = obj.image.all()
        return PostImageSerializers(instance=image, many = True, context = self.context).data
    
    class Meta:
        model = Article
        fields = [
            'pk',
            'subject',
            'title',
            'content',
            'createuser',
            'password',
            'created_at',
            'updated_at',
            'hits',
            'comments',
            'images',
        ]


    def create(self, validated_data):
        instance = Article.objects.create(**validated_data)
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('image'):
            ext = str(image_data).split('.')[-1]
            ext = ext.lower()
            if ext in ['jpg', 'jpeg','png',]:
                PostImage.objects.create(article=instance, image=image_data, image_original=image_data)
            elif ext in ['gif','webp']:
                PostImage.objects.create(article=instance, image_original=image_data)
        return instance



