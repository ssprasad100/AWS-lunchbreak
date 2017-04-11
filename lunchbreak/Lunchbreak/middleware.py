from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from subdomains.middleware import UNSET, SubdomainURLRoutingMiddleware


class SubdomainHostMiddleware(SubdomainURLRoutingMiddleware):

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


class RedirectHostMiddleware:

    def process_request(self, request):
        # Remove the port from the host.
        split_host = request.get_host().split(':')
        host = split_host[0]

        redirected_host = settings.REDIRECTED_HOSTS.get(host)
        if redirected_host is not None:
            port = None
            if len(split_host) > 1:
                port = split_host[1]

            redirect_url = '{scheme}://{host}{port}{path}'.format(
                scheme=request.scheme,
                host=redirected_host,
                port=':' + port if port is not None else '',
                path=request.get_full_path()
            )
            return HttpResponsePermanentRedirect(redirect_url)
