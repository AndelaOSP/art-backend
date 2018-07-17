from rest_framework.pagination import PageNumberPagination


def _positive_int(integer_string, strict=False, cutoff=None):
        """
        Cast a string to a strictly positive integer.
        """
        ret = int(integer_string)
        if ret < 0 or (ret == 0 and strict):
            raise ValueError()
        if cutoff:
            return min(ret, cutoff)
        return ret


class PageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 20
    max_page_size = None

    def get_page_size(self, request):
        paginate = request.query_params.get('paginate', None)
        if paginate and paginate.lower() == 'false':
            return None
        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size
