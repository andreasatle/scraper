import urllib.parse


class URLNormalizer:
    """Handles URL normalization and domain comparison"""
    
    @staticmethod
    def normalize_host(url: str) -> str:
        """Normalize host for domain comparison"""
        try:
            netloc = urllib.parse.urlparse(url).netloc.lower()
            # strip default ports
            if netloc.endswith(":80"):
                netloc = netloc[:-3]
            if netloc.endswith(":443"):
                netloc = netloc[:-4]
            # strip leading www. and trailing dot
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc.rstrip(".")
        except Exception:
            return ""

    @staticmethod
    def same_domain(u1: str, u2: str) -> bool:
        """Check if two URLs belong to the same domain"""
        return URLNormalizer.normalize_host(u1) == URLNormalizer.normalize_host(u2)

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL for deduplication"""
        try:
            p = urllib.parse.urlparse(url)
            scheme = p.scheme.lower()
            host = p.netloc.lower()

            # remove default ports
            if scheme == "http" and host.endswith(":80"):
                host = host.rsplit(":", 1)[0]
            elif scheme == "https" and host.endswith(":443"):
                host = host.rsplit(":", 1)[0]

            # strip leading www. and trailing dot
            if host.startswith("www."):
                host = host[4:]
            host = host.rstrip(".")

            # normalize path
            path = p.path or ""
            if path == "/":
                path = ""  # collapse root to empty
            else:
                path = path.rstrip("/")

            # keep query; drop fragment
            return urllib.parse.urlunparse((scheme, host, path, "", p.query, ""))
        except Exception:
            return url

    @staticmethod
    def absolutize(base: str, href: str) -> str:
        """Convert relative URL to absolute URL"""
        return urllib.parse.urljoin(base, href)
