from django.shortcuts import render
from django.views.generic import View

from utils.common import LoginRequiredMixin


class PlaceOrderView(LoginRequiredMixin, View):

    def post(self):
        pass