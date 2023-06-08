from datetime import datetime

from flask import Flask, jsonify, make_response, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import (
    SQLAlchemyAutoSchema,
)  # imports modules to serialize Python objects

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False
db = SQLAlchemy(app)


# creating tables in database


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(1500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Incomplete")

    def __repr__(self):
        return f"{self.description} , {self.title} | {self.due_date} | {self.status}"


class TaskSchema(SQLAlchemyAutoSchema):
    class Meta(SQLAlchemyAutoSchema.Meta):
        model = Task
        load_instance = True


ROWS_PER_PAGE = 5


class GetData(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)

        tasks = Task.query.paginate(page=page, per_page=ROWS_PER_PAGE)  # queries the database for Tasks
        schema = TaskSchema(many=True)
        data = schema.dump(tasks)

        return make_response(jsonify({"Tasks": data}))  # returns list of Tasks as JSON


class GetDataById(Resource):
    def get(self, id):
        task = Task.query.get(id)  # queries the database for Tasks
        schema = TaskSchema()
        data = schema.dump(task)

        return make_response(jsonify({"Task": data}))  # returns list of Tasks as JSON


class PostData(Resource):
    def post(self):
        if request.is_json:
            data = request.get_json()  # gets data from request body
            title = data["title"]
            description = data["description"]
            due_date = data["due_date"]
            status = data["status"]

            new = Task(
                description=description, title=title, due_date=due_date, status=status
            )

            db.session.add(new)  # adds task to database
            db.session.commit()  # commits changes to database

            schema = TaskSchema()
            data = schema.dump(new)

            return make_response(jsonify({"New Task": data}), 201)
        else:
            return {"error": "Request not JSON"}, 400


class UpdateData(Resource):
    def put(self, id):
        if request.is_json:
            data = request.get_json()  # gets data from request body
            task = Task.query.get(id)  # queries the database by given id
            if task is None:
                return {"error": "Not found"}, 404
            else:
                task.title = data["title"]
                task.description = data["description"]
                task.due_date = data["due_date"]
                task.status = data["status"]  # updates Task data with new data

                db.session.commit()  # commits changes to database
                return "Updated", 200
        else:
            return {"error": "Request is not JSON"}, 400


class DeleteData(Resource):
    def delete(self, id):
        task = Task.query.get(id)  # queries the database by given id
        if task is None:
            return {"error": "Not found"}, 404
        else:
            db.session.delete(task)
            db.session.commit()  # commits changes to database
            return "Task is deleted", 200


api.add_resource(GetData, "/")
api.add_resource(GetDataById, "/<int:id>")
api.add_resource(PostData, "/add/")
api.add_resource(UpdateData, "/update/<int:id>/")
api.add_resource(DeleteData, "/delete/<int:id>/")


if __name__ == "__main__":
    app.run(debug=True)
