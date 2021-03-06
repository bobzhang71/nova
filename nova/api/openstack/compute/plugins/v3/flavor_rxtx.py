#   Copyright 2012 Nebula, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

"""The Flavor Rxtx API extension."""

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api.openstack import xmlutil

ALIAS = 'os-flavor-rxtx'
authorize = extensions.soft_extension_authorizer('compute', 'v3:' + ALIAS)


class FlavorRxtxController(wsgi.Controller):
    def _extend_flavors(self, req, flavors):
        for flavor in flavors:
            db_flavor = req.get_db_flavor(flavor['id'])
            key = 'rxtx_factor'
            flavor[key] = db_flavor['rxtx_factor'] or ""

    def _show(self, req, resp_obj):
        if not authorize(req.environ['nova.context']):
            return
        if 'flavor' in resp_obj.obj:
            resp_obj.attach(xml=FlavorRxtxTemplate())
            self._extend_flavors(req, [resp_obj.obj['flavor']])

    @wsgi.extends
    def show(self, req, resp_obj, id):
        return self._show(req, resp_obj)

    @wsgi.extends(action='create')
    def create(self, req, resp_obj, body):
        return self._show(req, resp_obj)

    @wsgi.extends
    def detail(self, req, resp_obj):
        if not authorize(req.environ['nova.context']):
            return
        resp_obj.attach(xml=FlavorsRxtxTemplate())
        self._extend_flavors(req, list(resp_obj.obj['flavors']))


class FlavorRxtx(extensions.V3APIExtensionBase):
    """Support to show the rxtx status of a flavor."""

    name = "FlavorRxtx"
    alias = ALIAS
    namespace = "http://docs.openstack.org/compute/ext/%s/api/v3" % ALIAS
    version = 1

    def get_controller_extensions(self):
        controller = FlavorRxtxController()
        extension = extensions.ControllerExtension(self, 'flavors', controller)
        return [extension]

    def get_resources(self):
        return []


def make_flavor(elem):
    # NOTE(vish): this was originally added without a namespace
    elem.set('rxtx_factor', xmlutil.EmptyStringSelector('rxtx_factor'))


class FlavorRxtxTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('flavor', selector='flavor')
        make_flavor(root)
        return xmlutil.SlaveTemplate(root, 1)


class FlavorsRxtxTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('flavors')
        elem = xmlutil.SubTemplateElement(root, 'flavor', selector='flavors')
        make_flavor(elem)
        return xmlutil.SlaveTemplate(root, 1)
