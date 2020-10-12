# coding: utf-8
from sqlalchemy import Column, Float, ForeignKey, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Cell(db.Model):
    __tablename__ = 'cells'
    __table_args__ = (
        db.UniqueConstraint('shelf_pkey', 'cell_column'),
    )

    cell_pkey = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    shelf_pkey = db.Column(db.ForeignKey('shelves.shelf_pkey', ondelete='CASCADE'), nullable=False)
    design_pkey_master = db.Column(db.ForeignKey('designs.design_pkey', ondelete='SET NULL'))
    design_pkey_front = db.Column(db.ForeignKey('designs.design_pkey', ondelete='SET NULL'))
    cell_column = db.Column(db.SmallInteger, nullable=False)

    design = db.relationship('Design', primaryjoin='Cell.design_pkey_front == Design.design_pkey', backref='design_cells')
    design1 = db.relationship('Design', primaryjoin='Cell.design_pkey_master == Design.design_pkey', backref='design_cells_0')
    shelf = db.relationship('Shelf', primaryjoin='Cell.shelf_pkey == Shelf.shelf_pkey', backref='cells')



class Design(db.Model):
    __tablename__ = 'designs'

    design_pkey = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    goods_id = db.Column(db.ForeignKey('goods.goods_id'))
    design_type = db.Column(db.String(20))
    design_mean_weight = db.Column(db.Float(53))
    design_std_weight = db.Column(db.Float(53))
    design_infer_label = db.Column(db.String(50))
    design_img_url = db.Column(db.String(2048))

    goods = db.relationship('Good', primaryjoin='Design.goods_id == Good.goods_id', backref='designs')



class Device(db.Model):
    __tablename__ = 'devices'

    device_pkey = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    device_id = db.Column(db.String(10), nullable=False)
    store_id = db.Column(db.ForeignKey('stores.store_id', ondelete='CASCADE'))
    device_install_type = db.Column(db.String(1))
    device_storage_type = db.Column(db.String(2))

    store = db.relationship('Store', primaryjoin='Device.store_id == Store.store_id', backref='devices')



class Good(db.Model):
    __tablename__ = 'goods'

    goods_pkey = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    goods_id = db.Column(db.String(13), nullable=False, unique=True)
    goods_name = db.Column(db.String(50))



class Loadcell(db.Model):
    __tablename__ = 'loadcells'
    __table_args__ = (
        db.UniqueConstraint('shelf_pkey', 'cell_pkey', 'loadcell_column'),
    )

    loadcell_pkey = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    shelf_pkey = db.Column(db.ForeignKey('shelves.shelf_pkey', ondelete='CASCADE'))
    cell_pkey = db.Column(db.ForeignKey('cells.cell_pkey', ondelete='SET NULL'))
    loadcell_column = db.Column(db.SmallInteger, nullable=False)

    cell = db.relationship('Cell', primaryjoin='Loadcell.cell_pkey == Cell.cell_pkey', backref='loadcells')
    shelf = db.relationship('Shelf', primaryjoin='Loadcell.shelf_pkey == Shelf.shelf_pkey', backref='loadcells')



class Shelf(db.Model):
    __tablename__ = 'shelves'
    __table_args__ = (
        db.UniqueConstraint('device_pkey', 'shelf_floor'),
    )

    shelf_pkey = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    device_pkey = db.Column(db.ForeignKey('devices.device_pkey', ondelete='CASCADE'), nullable=False)
    shelf_floor = db.Column(db.SmallInteger, nullable=False)

    device = db.relationship('Device', primaryjoin='Shelf.device_pkey == Device.device_pkey', backref='shelves')



class Stock(db.Model):
    __tablename__ = 'stocks'
    __table_args__ = (
        db.UniqueConstraint('cell_pkey', 'design_pkey'),
    )

    stock_pkey = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    cell_pkey = db.Column(db.ForeignKey('cells.cell_pkey', ondelete='CASCADE'), nullable=False)
    design_pkey = db.Column(db.ForeignKey('designs.design_pkey'), nullable=False)
    stock_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())

    cell = db.relationship('Cell', primaryjoin='Stock.cell_pkey == Cell.cell_pkey', backref='stocks')
    design = db.relationship('Design', primaryjoin='Stock.design_pkey == Design.design_pkey', backref='stocks')



class Store(db.Model):
    __tablename__ = 'stores'

    store_pkey = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    store_id = db.Column(db.String(10), nullable=False, unique=True)
    store_name = db.Column(db.String(50))
