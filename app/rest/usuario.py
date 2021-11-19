from flask import jsonify, make_response, request
from flask_pymongo import PyMongo, ObjectId
from regex import Regex
from ..app import app
from .trayecto import actualizar_conductor

mongo = PyMongo(app)
usuario = mongo.db.usuario
trayecto = mongo.db.trayecto



# ---- ENDPOINTS -------------------------------------------------------------------------


@app.route("/api/v1/usuarios", methods=["POST"])
def create_usuario():
    if request.is_json:
        datos = request.get_json()
        try:
            res = usuario.insert_one({
                "nombre": str(datos["nombre"]),
                "apellidos": str(datos["apellidos"]),
                "email": str(datos["email"]),
                "telefono": str(datos["telefono"]),
                "contrasenia": str(datos["contrasenia"]),
                "link_paypal": str(datos["link_paypal"]),
                "url_foto_perfil": str(datos["url_foto_perfil"]),
                "rol": int(datos["rol"])
            })
            return jsonify(msg="Usuario creado", new_id=str(res.inserted_id))

        except:
            respuesta = jsonify(msg="Petición no válida, faltan campos o no son del tipo correcto")
            return make_response(respuesta, 400)

    else:
        respuesta = jsonify(msg="Petición no válida, se requiere JSON")
        return make_response(respuesta, 400)

@app.route("/api/v1/usuarios", methods=["GET"])
def get_usuarios():

    cursor = None
    search = request.args.get("search")
    if search is not None:
        regex = {
            "$regex": search.replace("\\", "\\\\"),
            "$options": "i"
            }
        cursor = usuario.find({"$or":
        [
            {"nombre": regex},
            {"apellidos": regex}
        ]})
    else:
        cursor = usuario.find()


    resultado = []
    for u in cursor:
        u["_id"] = str(u["_id"])
        resultado.append(u)
    return jsonify(resultado)

@app.route("/api/v1/usuarios/<id>", methods=["GET"])
def get_usuario(id):
    resultado = usuario.find_one({"_id" : ObjectId(id)})
    if resultado is not None:
        resultado["_id"] = str(resultado["_id"])
        return jsonify(resultado)
    else:
        respuesta = jsonify(msg="No existe ningún usuario con id = %s" % id)
        return make_response(respuesta, 404)

@app.route("/api/v1/usuarios/<id>", methods=["PUT"])
def update_usuario(id):
    oid = ObjectId(id)
    resultado = usuario.find_one({"_id" : oid})
    if resultado is not None:
        if request.is_json:
            datos = request.get_json()
            nuevos_valores = {}
            try:
                if "nombre" in datos:
                    nuevos_valores["nombre"] = str(datos["nombre"])
                if "apellidos" in datos:
                    nuevos_valores["apellidos"] = str(datos["apellidos"])
                if "email" in datos:
                    nuevos_valores["email"] = str(datos["email"])
                if "telefono" in datos:
                    nuevos_valores["telefono"] = str(datos["telefono"])
                if "contrasenia" in datos:
                    nuevos_valores["contrasenia"] = str(datos["contrasenia"])
                if "link_paypal" in datos:
                    nuevos_valores["link_paypal"] = str(datos["link_paypal"])
                if "url_foto_perfil" in datos:
                    nuevos_valores["url_foto_perfil"] = str(datos["url_foto_perfil"])
                if "rol" in datos:
                    nuevos_valores["rol"] = int(datos["rol"])
            except Exception:
                respuesta = jsonify(msg="Petición no válida, hay campos que no son del tipo correcto")
                return make_response(respuesta, 400)

            usuario.update_one({"_id": oid}, {"$set": nuevos_valores})

            # Actualizar datos redundantes
            actualizar_conductor(oid)

            return jsonify(msg='Usuario actualizado')

        else:
            respuesta = jsonify(msg="Petición no válida, se requiere JSON")
            return make_response(respuesta, 400)
    else:
        respuesta = jsonify(msg="No existe ningún usuario con id = %s" % id)
        return make_response(respuesta, 404)

@app.route("/api/v1/usuarios/<id>", methods=["DELETE"])
def delete_usuario(id):
    oid = ObjectId(id)
    resultado = usuario.find_one({"_id" : oid})
    if resultado is not None:
        usuario.delete_one({"_id": oid})

        # Cascada
        trayecto.delete_many({"conductor._id": oid})

        return jsonify(msg='Usuario borrado')
    else:
        respuesta = jsonify(msg="No existe ningún usuario con id = %s" % id)
        return make_response(respuesta, 404)
