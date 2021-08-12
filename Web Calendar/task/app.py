import datetime

from flask import Flask
from flask_restful import Api, Resource, reqparse, inputs, marshal_with, fields, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import sys

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.sqlite'

class DateFormat(fields.Raw):
    def format(self, value):
        return value.strftime('%Y-%m-%d')

resource_fields = {
    'id':       fields.Integer,
    'event':    fields.String,
    'date':     DateFormat
}

class EventModel(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)

class Event(Resource):

    @marshal_with(resource_fields)
    def get(self):
        args = get_event_parser.parse_args()

        if not args['start_time'] and not args['end_time']:
            query = EventModel.query.all()
            return query

        query = EventModel.query.filter(EventModel.date.between(args['start_time'], args['end_time'])).all()
        return query


    def post(self):
        args = event_parser.parse_args()
        query = EventModel(event=args['event'], date=args['date'])
        db.session.add(query)
        db.session.commit()
        response = {
            "message": "The event has been added!",
            "event": args['event'],
            "date": str(args['date'].date())
        }
        return response


class EventByID(Resource):
    @marshal_with(resource_fields)
    def get(self, event_id):
        result = EventModel.query.filter_by(id=event_id).first()
        if not result:
            abort(404, message="The event doesn't exist!")
        return result

    def delete(self, event_id):
        result = EventModel.query.filter_by(id=event_id).first()

        if not result:
           abort(404, message="The event doesn't exist!")

        db.session.delete(result)
        db.session.commit()
        response = {
            "message": "The event has been deleted!"
        }
        return response


class EventToday(Resource):
    @marshal_with(resource_fields)
    def get(self):
        today = date.today()
        query = EventModel.query.filter_by(date=today).all()
        return query

event_parser = reqparse.RequestParser()
event_parser.add_argument('event', type=str, help="The event name is required!", required=True)
event_parser.add_argument('date', type=inputs.date, required=True,
                    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!")

get_event_parser = reqparse.RequestParser()
get_event_parser.add_argument('start_time', type=inputs.date)
get_event_parser.add_argument('end_time', type=inputs.date)

db.create_all()
api.add_resource(Event, '/event')
api.add_resource(EventByID, '/event/<int:event_id>')
api.add_resource(EventToday, '/event/today')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
