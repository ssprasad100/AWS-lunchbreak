from subdomains.middleware import SubdomainURLRoutingMiddleware


class SubdomainHostMiddleWare(SubdomainURLRoutingMiddleware):

    def get_domain_for_request(self, request):
        # Return the host without the port
        host = request.get_host().split(':')[0]
        return '.'.join(host.split('.')[1:])
