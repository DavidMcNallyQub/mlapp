from flask import jsonify, request
from flask.views import MethodView
from mlapp.extensions import dbase as db

def generate_validator(model, create=False):
    validator = None
    if create:
        validator = model.validator()
    else:
        validator = model.validator()
    return validator

class ItemAPI(MethodView):
    init_every_request = False

    def __init__(self, model):
        self.model = model
        self.validator = generate_validator(model, create=True)

    def _get_item(self, id):
        return self.model.query.get_or_404(id)

    def get(self, id):
        item = self._get_item(id)
        return jsonify(item.as_dict())

    def patch(self, id):
        # TODO This currently doesn't abide by foreign key and update values correctly
        item = self._get_item(id)
        print(f"Before : {item}")
        # populate the respective wtform with the request.form data.
        form = self.validator(request.form, obj=item)
        print(f"After : {form}")
        # check for validation errors from the wtform.
        if not form.validate():
            errors = form.errors
            return jsonify(errors), 400
        # create sqlalchemy model instance and populate it with wtform data.
        model_instance = self.model()
        form.populate_obj(model_instance)
        # add and commit changes to the SQLite3 database.
        # TODO currently does not respect foreign key constraints.
        # db.session.add(model_instance)
        db.session.commit()
        return jsonify(model_instance.as_dict()), 200

        # errors = self.validator.validate(item, request.json)

        # if errors:
        #     return jsonify(errors), 400

        # item.update_from_json(request.json)
        # db.session.commit()
        # return jsonify(item.to_json())

    def delete(self, id):
        item = self._get_item(id)
        db.session.delete(item)
        db.session.commit()
        return "", 204

class GroupAPI(MethodView):
    """_summary_

    _extended_summary_

    Parameters
    ----------
    MethodView : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    init_every_request = False

    def __init__(self, model):
        self.model = model
        self.validator = generate_validator(model, create=True)

    def get(self):
        items = self.model.query.all()
        return jsonify([item.as_dict() for item in items])

    def post(self):
        # populate the respective wtform with the request.form data.
        form = self.validator(request.form)
        # check for validation errors from the wtform.
        if not form.validate():
            errors = form.errors
            return jsonify(errors), 400
        # create sqlalchemy model instance and populate it with wtform data.
        model_instance = self.model()
        form.populate_obj(model_instance)
        # add and commit changes to the SQLite3 database.
        # TODO currently does not respect foreign key constraints.
        db.session.add(model_instance)
        db.session.commit()
        return jsonify(model_instance.as_dict()), 201

def register_api(app, model, name):
    item = ItemAPI.as_view(f"{name}-item", model)
    group = GroupAPI.as_view(f"{name}-group", model)
    app.add_url_rule(f"/{name}/<int:id>", view_func=item)
    app.add_url_rule(f"/{name}/", view_func=group)