import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES
@app.route('/drinks', methods=['GET'])
def getDrinks():
    
    drinks = Drink.query.all()
    shortedDrinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": shortedDrinks
        })
    




@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def getDrinksDetail(payload):
    drinks = Drink.query.all()
    longDrinks = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": longDrinks
        })

@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def addNewDrink(payload):
   getDrink = request.get_json()
#    if ('title' not in getDrink) or ('recipe' not in getDrink):
#         abort(400)
   try:
       addNewDrink = Drink(title = getDrink['title'], recipe = json.dumps(getDrink['recipe']))
       addNewDrink.insert()
       return jsonify({
           "success": True,
           "drinks": [addNewDrink.long()]
        })
   except BaseException:
        print(sys.exc_info())
        abort(500)
   



@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth("patch:drinks")
def updateDrink(payload, drink_id):
    try:
        drink = Drink.query.get(drink_id)

        getDrink = request.get_json()
        if 'title' in getDrink: 
            drink.title = getDrink['title']
        if 'recipe' in getDrink:  
            drink.recipe = json.dumps(getDrink['recipe'])

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except BaseException:
        print(sys.exc_info())
        abort(404)


@app.route('/drinks/<int:drink_id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def deleteDrink(payload, drink_id):
    try:
        selectedDrink = Drink.query.filter_by(id = drink_id).one_or_none()

        selectedDrink.delete()
        return jsonify({
            "success": True,
            "delete": drink_id
        })

    except BaseException:
        print(sys.exc_info())
        abort(404)




## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404



@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(AuthError)
def UnAuthoraized(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "UnAuthoraized"
                    }), 401

@app.errorhandler(400)
def badRequest(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "Bad Request"
                    }), 400