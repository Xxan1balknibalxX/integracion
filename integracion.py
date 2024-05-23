from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DECIMAL, ForeignKeyConstraint, PrimaryKeyConstraint, text
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
api = Api(app)

# Configuración de la conexión a la base de datos MySQL utilizando SQLAlchemy
engine = create_engine('mysql+pymysql://root:snxUkOBUnbtmayZIIzHJhwnFrGoDEjex@roundhouse.proxy.rlwy.net:19951/railway', pool_pre_ping=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
metadata = MetaData()

# Define las tablas de la base de datos
herramienta = Table('Herramienta', metadata,
    Column('CodigoH', String(45), primary_key=True),
    Column('MarcaH', String(45), nullable=False),
    Column('NombreH', String(45), nullable=False)
)

precio_herramienta = Table('PrecioHerramienta', metadata,
    Column('CodigoH', String(45), nullable=False),
    Column('Valor', DECIMAL(10, 2), nullable=False),
    PrimaryKeyConstraint('CodigoH'),
    ForeignKeyConstraint(['CodigoH'], ['Herramienta.CodigoH'])
)

stock_herramienta = Table('StockHerramienta', metadata,
    Column('CodigoH', String(45), nullable=False),
    Column('Stock', Integer, nullable=False),
    PrimaryKeyConstraint('CodigoH'),
    ForeignKeyConstraint(['CodigoH'], ['Herramienta.CodigoH'])
)

# Crea todas las tablas definidas en el metadata en la base de datos
metadata.create_all(bind=engine)

# Definición de las clases de recursos
class HerramientaResource(Resource):
    def get(self):
        query = text("""
        SELECT h.CodigoH, h.MarcaH, h.NombreH, p.Valor AS Precio, s.Stock
        FROM Herramienta h
        LEFT JOIN PrecioHerramienta p ON h.CodigoH = p.CodigoH
        LEFT JOIN StockHerramienta s ON h.CodigoH = s.CodigoH;
        """)
        data = db_session.execute(query).fetchall()
        data_dict = [
            {
                'CodigoH': row.CodigoH,
                'MarcaH': row.MarcaH,
                'NombreH': row.NombreH,
                'Precio': row.Precio,
                'Stock': row.Stock
            } for row in data
        ]
        return jsonify(data_dict)

    def post(self):
        data = request.get_json()
        db_session.execute(herramienta.insert().values(CodigoH=data['CodigoH'], MarcaH=data['MarcaH'], NombreH=data['NombreH']))
        db_session.commit()
        return {'message': 'Herramienta creada satisfactoriamente'}, 201

    def put(self):
        data = request.get_json()
        db_session.execute(herramienta.update().where(herramienta.c.CodigoH == data['CodigoH']).values(MarcaH=data['MarcaH'], NombreH=data['NombreH']))
        db_session.commit()
        return {'message': 'Herramienta actualizada satisfactoriamente'}, 200

    def delete(self):
        data = request.get_json()
        db_session.execute(herramienta.delete().where(herramienta.c.CodigoH == data['CodigoH']))
        db_session.commit()
        return {'message': 'Herramienta eliminada satisfactoriamente'}, 200

# Rutas de la API
api.add_resource(HerramientaResource, '/herramientas')

if __name__ == '__main__':
    app.run(debug=True)
