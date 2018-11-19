from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.http import urlunquote

from coin_exchange.models import UserLimit
from coin_user.constants import VERIFICATION_LEVEL, VERIFICATION_STATUS
from coin_user.models import ExchangeUser


class UserLimitInline(admin.StackedInline):
    model = UserLimit
    fields = ('limit', 'usage')
    readonly_fields = ('limit', 'usage')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ExchangeUser)
class ExchangeUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'id_name', 'id_number', 'id_type',
                    'display_front_image', 'display_back_image', 'display_selfie_image',
                    'display_level', 'display_status', 'country', 'user_actions']
    inlines = (UserLimitInline,)
    list_filter = ('country', 'verification_level', 'verification_status')

    def changelist_view(self, request, *args, **kwargs):
        self.request = request
        return super().changelist_view(request, *args, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False

    def display_level(self, obj):
        return VERIFICATION_LEVEL[obj.verification_level]

    display_level.short_description = 'Level'

    def display_status(self, obj):
        return VERIFICATION_STATUS[obj.verification_status]

    display_status.short_description = 'Status'

    def display_front_image(self, obj):
        return self._get_image_tag(obj.front_image)

    display_front_image.short_description = 'Front Image'

    def display_back_image(self, obj):
        return self._get_image_tag(obj.back_image)

    display_back_image.short_description = 'Front Image'

    def display_selfie_image(self, obj):
        return self._get_image_tag(obj.selfie_image)

    display_selfie_image.short_description = 'Selfie Image'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('verify-process/<int:user_id>',
                 self.admin_site.admin_view(self.user_verify_process),
                 name='user-verify-process'),
            path('verify-approve/<int:user_id>',
                 self.admin_site.admin_view(self.user_verify_approve),
                 name='user-verify-approve'),
            path('verify-reject/<int:user_id>',
                 self.admin_site.admin_view(self.user_verify_reject),
                 name='user-verify-reject'),
        ]
        return custom_urls + urls

    def user_verify_process(self, request, user_id, *args, **kwargs):
        return self.do_action(request, user_id, self._do_change_verify_process)

    def user_verify_approve(self, request, user_id, *args, **kwargs):
        return self.do_action(request, user_id, self._do_change_verify_approve)

    def user_verify_reject(self, request, user_id, *args, **kwargs):
        return self.do_action(request, user_id, self._do_change_verify_reject)

    def do_action(self, request, user_id, action_func):
        user = self.get_object(request, user_id)
        action_func(user)

        # Get it back
        changelist_filters = request.GET.get('_changelist_filters')
        return HttpResponseRedirect('../?{}'.format(urlunquote(changelist_filters)))

    def _do_change_verify_process(self, user):
        user.verification_status = VERIFICATION_STATUS.processing
        user.save()

    def _do_change_verify_approve(self, user):
        user.verification_status = VERIFICATION_STATUS.approved
        user.save()

    def _do_change_verify_reject(self, user):
        user.verification_status = VERIFICATION_STATUS.rejected
        user.save()

    def user_actions(self, obj):
        if obj.verification_status == VERIFICATION_STATUS.pending:
            return self._get_process_button(obj)
        if obj.verification_status == VERIFICATION_STATUS.processing:
            return self._get_approve_button(obj) + format_html('&nbsp;') + self._get_reject_button(obj)

    def _get_process_button(self, obj):
        return format_html(
            '<a class="button" href="{}?{}">Process</a>',
            reverse('admin:user-verify-process', args=[obj.pk]),
            self.get_preserved_filters(self.request),
        )

    def _get_approve_button(self, obj):
        return format_html(
            '''<a class="button" href="{}?{}" onclick="return confirm('Are you sure?')">Approve</a>''',
            reverse('admin:user-verify-approve', args=[obj.pk]),
            self.get_preserved_filters(self.request),
        )

    def _get_reject_button(self, obj):
        return format_html(
            '''<a class="button" href="{}?{}" onclick="return confirm('Are you sure?')">Reject</a>''',
            reverse('admin:user-verify-reject', args=[obj.pk]),
            self.get_preserved_filters(self.request),
        )

    def _get_image_tag(self, image_url: str):
        return format_html('''<a href="{}"
        onclick="return !window.open(this.href, 'Google', 'width=500, height=500, top=200, left=500')" target="_blank">
            <img src="{}" width="75" height="75" />
        </a>
        ''', image_url, image_url) if image_url else ''

    user_actions.short_description = 'Actions'
    user_actions.allow_tags = True
