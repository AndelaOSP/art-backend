from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import DefaultIndexDashboard


class CustomIndexDashboard(DefaultIndexDashboard):
    def init_with_context(self, context):
        super().init_with_context(context)
        self.available_children.append(modules.LinkList)
        self.available_children.append(modules.AppList)

        self.children.append(modules.LinkList(
            _('Performance Profile'),
            children=[
                {
                    'title': _('Summary'),
                    'url': '/performance',
                    'external': True
                },
                {
                    'title': _('Requests'),
                    'url': '/performance/requests',
                    'external': True
                },
                {
                    'title': _('Profiling'),
                    'url': '/performance/profiling',
                    'external': True
                },
            ],
            column=0,
            order=0
        ))
