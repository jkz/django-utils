class SubdomainMiddleware:
    def process_request(self, request):
        """Parse out the subdomain from the request"""
        request.subdomain = None
        host = request.get_host()
        host_s = host.replace('www.', '').split('.')
        if len(host_s) > 2:
            request.subdomain = '.'.join(host_s[:-2])

