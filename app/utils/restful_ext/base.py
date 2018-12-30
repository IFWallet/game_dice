#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_restful import Resource
from flask_restful import marshal
from .pagination import NumberPagination
from app.utils.xhr import response_ok


class ListResource(Resource):
    def response_data(self, queryset, fields=None):
        fields = fields or self.base_fields
        number_pagination = NumberPagination()
        page = number_pagination.paginate_queryset(queryset)
        if page is not None:
            data = marshal(page, fields)
            return number_pagination.get_paginated_response(data)

        return marshal(queryset.all(), fields)

    def response_page(self, queryset, fields=None):
        return response_ok(self.response_data(queryset, fields))


class OffsetToNumberPageResource(Resource):
    @staticmethod
    def response_data(data, list_name='records'):
        limit = data['limit'] - 1
        offset = data['offset']
        list_data = data[list_name]
        count = len(list_data)

        if count > limit:
            count = limit
            has_next = True
            list_data = data[list_name][:count]
        else:
            has_next = False

        data = dict(
                has_next=has_next,
                curr_page=offset / limit + 1,
                count=count,
                data=list_data
        )
        return data

    def response_page(self, data, list_name='records'):
        return response_ok(self.response_data(data, list_name))
