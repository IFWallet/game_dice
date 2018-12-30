#!/usr/bin/python
# -*- coding: utf-8 -*-

def _get_count(queryset):
    """
    Determine an object count, supporting either querysets or regular lists.
    """
    try:
        return queryset.count()
    except (AttributeError, TypeError):
        return len(queryset)


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        ret = min(ret, cutoff)
    return ret


class NumberPagination(object):
    default_limit = 50
    default_page = 1
    limit_query_param = 'limit'
    page_query_param = 'page'
    max_limit = None

    def __init__(self):
        self.count = 0
        self.total_page = 0
        self.page = 0
        self.start_pos = 0
        self.end_pos = 0

    def paginate_queryset(self, queryset):
        self.count = _get_count(queryset)
        limit = self.get_limit()
        if limit is None:
            return None
        self.total_page = (self.count + limit - 1) / limit
        self.page = self.get_current_page()
        self.start_pos = min((self.page - 1) * limit, self.count)
        self.end_pos = min(self.start_pos + limit, self.count)
        return list(queryset[self.start_pos:self.end_pos])

    def get_paginated_response(self, data):
        return dict(
            total_page=self.total_page,
            total=self.count,
            has_next=self.end_pos < self.count,
            curr_page=self.page,
            count=self.end_pos - self.start_pos,
            data=data
        )

    def get_limit(self):
        from flask import request
        if self.limit_query_param:
            try:
                return _positive_int(
                    request.args[self.limit_query_param],
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return self.max_limit

    def get_current_page(self):
        from flask import request

        if self.page_query_param:
            try:
                return _positive_int(
                    request.args[self.page_query_param],
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return self.default_page
