from django.test import override_settings, TestCase
from django.urls import path
from django_mock_queries.query import MockSet, MockModel as MockModelBase, ObjectDoesNotExist, \
    MockOptions as MockOptionsBase, PropertyMock
from djangorestframework_camel_case.parser import CamelCaseJSONParser
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from parameterized import parameterized
from rest_framework import viewsets, serializers, generics
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.tokens import AccessToken

from apps.annotation.tests.utils import get_or_create_user
from apps.api import permissions


class MockOptions(MockOptionsBase):
    object_name = 'mock_object'


class MockModel(MockModelBase):
    DoesNotExist = ObjectDoesNotExist

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Extend
        self.delete = PropertyMock
        # Override
        self.__meta = MockOptions(*self.get_fields())


class PlainViewSetSerializer(serializers.BaseSerializer):
    # Plain serializer needs implementation of create to be viewset compatible
    def create(self, validated_data):
        return MockModel(**validated_data)

    def to_internal_value(self, data):
        return MockModel(**data)

    def to_representation(self, instance):
        # Strip all mocked properties to avoid infinite recursion
        return dict((f, instance.get(f)) for f in instance.get_fields() if isinstance(instance.get(f), (int, str)))

    def update(self, instance, validated_data):
        return instance


JohnTheOwner = MockModel(id=1, pk=1, name='john')
BillTheStranger = MockModel(id=2, pk=2, name='bill')


BoringBook = MockModel(id='10', pk='10', user_id=JohnTheOwner.id, user=JohnTheOwner, title='Boring book')
InterestingBook = MockModel(id='11', pk='11', user_id=JohnTheOwner.id, user=JohnTheOwner, title='Interesting book')

mock_book_queryset = MockSet(
    BoringBook, InterestingBook,
    model=BoringBook
)


class BaseViewMixin:
    renderer_classes = (CamelCaseJSONRenderer,)
    parser_classes = (CamelCaseJSONParser,)

    queryset = mock_book_queryset
    serializer_class = PlainViewSetSerializer
    permission_classes = ()


class BaseListCreateAPIView(BaseViewMixin, generics.ListCreateAPIView):
    pass


class BaseRetrieveUpdateDestroyAPIView(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    pass


class BaseViewSet(BaseViewMixin, viewsets.ModelViewSet):
    pass


class OnlyOwnerCanReadDetailView(BaseRetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.OnlyOwnerCanRead,)
    owner_field = 'user'


class OnlyOwnerCanReadListView(BaseListCreateAPIView):
    permission_classes = (permissions.OnlyOwnerCanRead,)
    owner_field = 'user'


class OnlyOwnerCanWriteViewSet(BaseViewSet):
    permission_classes = (permissions.OnlyOwnerCanWrite,)
    owner_field = 'user'


class OnlyEditorCanWriteViewSet(BaseViewSet):
    permission_classes = (permissions.OnlyEditorCanWrite,)
    owner_field = 'user'


class OnlyEditorOwnerCanWriteViewSet(BaseViewSet):
    permission_classes = (permissions.OnlyEditorCanWrite & permissions.OnlyOwnerCanWrite,)
    owner_field = 'user'


router = DefaultRouter()
router.register('only-owner-can-write-viewset', OnlyOwnerCanWriteViewSet)
router.register('only-editor-can-write-viewset', OnlyEditorCanWriteViewSet)
router.register('only-editor-owner-can-write-viewset', OnlyEditorOwnerCanWriteViewSet)

urlpatterns = router.urls + [
    path('only-owner-can-read-list-view/', OnlyOwnerCanReadListView.as_view()),
    path('only-owner-can-read-detail-view/<pk>/', OnlyOwnerCanReadDetailView.as_view()),
]


@override_settings(ROOT_URLCONF=__name__)
class PermissionsTestCase(TestCase):

    def setUp(self):
        self.john_owner = get_or_create_user(pk=JohnTheOwner.id)
        self.bill_stranger = get_or_create_user(pk=BillTheStranger.id)
        self.john_owner_token = str(AccessToken.for_user(self.john_owner))
        self.bill_stranger_token = str(AccessToken.for_user(self.bill_stranger))
        self.john_owner_header = 'JWT %s' % self.john_owner_token
        self.bill_stranger_header = 'JWT %s' % self.bill_stranger_token

    def get(self, url, token_header):
        return self.client.get(url, HTTP_AUTHORIZATION=token_header, content_type='application/json')

    def post(self, url, token_header):
        return self.client.post(url, HTTP_AUTHORIZATION=token_header, content_type='application/json')

    def put(self, url, token_header):
        return self.client.put(url, HTTP_AUTHORIZATION=token_header, content_type='application/json')

    def patch(self, url, token_header):
        return self.client.patch(url, HTTP_AUTHORIZATION=token_header, content_type='application/json')
    
    def delete(self, url, token_header):
        return self.client.put(url, HTTP_AUTHORIZATION=token_header, content_type='application/json')

    def assert_access_is(self, allowed, response):
        if allowed:
            self.assertTrue(200 <= response.status_code < 300, response.status_code)
        else:
            self.assertTrue(400 <= response.status_code < 404, response.status_code)

    @parameterized.expand([
        ('get', True, False),
        ('put', True, False),
        ('patch', True, False),
        ('delete', True, False),
    ])
    def test_only_owner_can_read__detail(self, method_name, john_access, bill_access):
        method = getattr(self, method_name)
        response = method(f'/only-owner-can-read-detail-view/{BoringBook.id}/', self.john_owner_header)
        self.assert_access_is(john_access, response)

        response = method(f'/only-owner-can-read-detail-view/{BoringBook.id}/', self.bill_stranger_header)
        self.assert_access_is(bill_access, response)

    @parameterized.expand([
        ('get', True, True),
        ('post', True, True),
    ])
    def test_only_owner_can_read__list(self, method_name, john_access, bill_access):
        method = getattr(self, method_name)
        response = method(f'/only-owner-can-read-list-view/', self.john_owner_header)
        self.assert_access_is(john_access, response)

        response = method(f'/only-owner-can-read-list-view/', self.bill_stranger_header)
        self.assert_access_is(bill_access, response)

    @parameterized.expand([
        ('get', True, True),
        ('put', True, False),
        ('patch', True, False),
        ('delete', True, False),
    ])
    def test_only_owner_can_write(self, method_name, john_access, bill_access):
        method = getattr(self, method_name)
        response = method(f'/only-owner-can-write-viewset/{BoringBook.id}/', self.john_owner_header)
        self.assert_access_is(john_access, response)

        response = method(f'/only-owner-can-write-viewset/{BoringBook.id}/', self.bill_stranger_header)
        self.assert_access_is(bill_access, response)

    @parameterized.expand([
        ('get', True, True),
        ('put', True, False),
        ('patch', True, False),
        ('delete', True, False),
    ])
    def test_only_editor_can_write__detail(self, method_name, editor_access, other_access):
        method = getattr(self, method_name)

        self.bill_stranger.role = self.bill_stranger.ROLE_EDITOR
        self.bill_stranger.save()
        response = method(f'/only-editor-can-write-viewset/{BoringBook.id}/', self.bill_stranger_header)
        self.assert_access_is(editor_access, response)

        self.bill_stranger.role = self.bill_stranger.ROLE_READER
        self.bill_stranger.save()
        response = method(f'/only-editor-can-write-viewset/{BoringBook.id}/', self.bill_stranger_header)
        self.assert_access_is(other_access, response)

    @parameterized.expand([
        ('get', True, True),
        ('post', True, False),
    ])
    def test_only_editor_can_write__list(self, method_name, editor_access, other_access):
        method = getattr(self, method_name)

        self.bill_stranger.role = self.bill_stranger.ROLE_EDITOR
        self.bill_stranger.save()
        response = method(f'/only-editor-can-write-viewset/', self.bill_stranger_header)
        self.assert_access_is(editor_access, response)

        self.bill_stranger.role = self.bill_stranger.ROLE_READER
        self.bill_stranger.save()
        response = method(f'/only-editor-can-write-viewset/', self.bill_stranger_header)
        self.assert_access_is(other_access, response)

    @parameterized.expand([
        ('get', True, True, True),
        ('put', True, False, False),
        ('patch', True, False, False),
        ('delete', True, False, False),
    ])
    def test_only_editor_owner_can_write__detail(self, method_name, editor_owner_access, owner_access, reader_access):
        method = getattr(self, method_name)

        self.john_owner.role = self.john_owner.ROLE_EDITOR
        self.john_owner.save()
        response = method(f'/only-editor-owner-can-write-viewset/{BoringBook.id}/', self.john_owner_header)
        self.assert_access_is(editor_owner_access, response)

        self.john_owner.role = self.john_owner.ROLE_READER
        self.john_owner.save()
        response = method(f'/only-editor-owner-can-write-viewset/{BoringBook.id}/', self.john_owner_header)
        self.assert_access_is(owner_access, response)

        response = method(f'/only-editor-owner-can-write-viewset/{BoringBook.id}/', self.bill_stranger_header)
        self.assert_access_is(reader_access, response)

    @parameterized.expand([
        ('get', True, True, True),
        ('post', True, False, False),
    ])
    def test_only_editor_owner_can_write__list(self, method_name, editor_owner_access, owner_access, reader_access):
        method = getattr(self, method_name)

        self.john_owner.role = self.john_owner.ROLE_EDITOR
        self.john_owner.save()
        response = method(f'/only-editor-owner-can-write-viewset/', self.john_owner_header)
        self.assert_access_is(editor_owner_access, response)

        self.john_owner.role = self.john_owner.ROLE_READER
        self.john_owner.save()
        response = method(f'/only-editor-owner-can-write-viewset/', self.john_owner_header)
        self.assert_access_is(owner_access, response)

        response = method(f'/only-editor-owner-can-write-viewset/', self.bill_stranger_header)
        self.assert_access_is(reader_access, response)



