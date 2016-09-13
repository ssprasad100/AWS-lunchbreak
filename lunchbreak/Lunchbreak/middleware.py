from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from subdomains.middleware import UNSET, SubdomainURLRoutingMiddleware


class SubdomainHostMiddleWare(SubdomainURLRoutingMiddleware):

    def get_domain_for_request(self, request):
        # Return the host without the port
        host = request.get_host().split(':')[0]
        domains = host.split('.')
        domain = '.'.join(domains[1:] if len(domains) > 2 else domains[:2])
        return domain

    def process_request(self, request):
        super().process_request(request)

        if getattr(request, 'subdomain', UNSET) is None:
            redirect_url = '{scheme}://{subdomain}.{host}{path}'.format(
                scheme=request.scheme,
                subdomain=settings.SUBDOMAIN_DEFAULT,
                host=request.get_host(),
                path=request.get_full_path()
            )
            return HttpResponsePermanentRedirect(redirect_url)
