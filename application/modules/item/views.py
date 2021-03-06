"""
File Path: application/modules/item/views.py
Description: Item routes/paths for App - Define Item routes/paths
Copyright (c) 2019. This Application has been developed by OR73.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

# Methods
from ..item import (ItemMethod, ValidateCreateUpdateForm)
# DB
# from setup import db
from application.setup import db

item_bp = Blueprint('item_bp', __name__)


@item_bp.route('/item/<string:item_name>/')
def show_item(item_name):
    """Public route - shows Item detailed information"""
    print('---------------- Item - show_item')
    # Validate if the Item provided exists in DB
    item = ItemMethod.get_item_by_name(item_name)
    if item:
        print('The Item %s exist' % item_name)
        # Get all categories of an Item
        categories = ItemMethod.catalog_method_get_all_categories_name_of_item_id(item.get_id())
        # categories = ItemMethod.catalog_method_get_all_categories_id_of_item_id(item.get_id())

        return render_template('item/show_item.html',
                               title=item_name,
                               subtitle='Item Details',
                               item=item,
                               categories=categories)
    else:
        flash('Required Item (%s) doesn\'t exist')
        return redirect(url_for('catalog_bp.index'))


@item_bp.route('/item/new/', methods=['GET', 'POST'])
@login_required
def create():
    print('---------------- Item - create_item - %s' % request.method)
    if request.method == 'GET':
        categories = ItemMethod.category_method_get_all_categories_order_by_name('asc')
        return render_template('item/create_item.html', categories=categories)
    elif request.method == 'POST':
        validate_create_item = ValidateCreateUpdateForm(request.form)
        if validate_create_item.validate():
            # name = request.form.get('name')
            # description = request.form.get('description')
            # price = request.form.get('price')
            name = validate_create_item.name.data
            description = validate_create_item.description.data
            price = validate_create_item.price.data
            categories_selected = request.form.getlist('category_list')
            print('name: ', name)
            print('description: ', description)
            print('price: ', price)
            print('categories_selected: ', categories_selected)

            # Create new item
            ItemMethod.create_item(name=name,
                                   description=description,
                                   price=price,
                                   owner=ItemMethod.auth_method_get_current_user_id())
            # Add items to Category
            for category in categories_selected:
                new_catalog = ItemMethod.catalog_method_create_catalog(
                    category_id=ItemMethod.category_method_get_id_by_name(category),
                    item_id=ItemMethod.get_id_by_name(name))
                # new_catalog = Catalog(category_id=CategoryMethodCRUD.get_id_by_name(category),
                #                      item_id=ItemMethod.get_id_by_name(name))
                print('type(new_catalog): ', type(new_catalog))
                print('new_catalog: ', new_catalog)

            flash('New Item (%s) has been created successfully' % name)
        return redirect(url_for('catalog_bp.index'))

    flash('Required operation is not authorized')
    return redirect(url_for('catalog_bp.index'))


@item_bp.route('/item/edit/<string:item_name>', methods=['GET', 'POST'])
@login_required
def edit(item_name):
    print('----------------- Category - edit - %s' % request.method)
    item = ItemMethod.get_item_by_name(item_name)

    """ Validate if current_user is the owner of item_name """
    item_owner_db_id = ItemMethod.get_owner_by_name(item_name)
    current_session_user_id = ItemMethod.auth_method_get_current_user_id()

    if item_owner_db_id == current_session_user_id:
        """ Load item to be edited """
        item_categories = ItemMethod.catalog_method_get_all_categories_name_of_item_id(item.get_id())
        # item_categories = ItemMethod.catalog_method_get_all_categories_id_of_item_id(item.get_id())
        print('item_categories: ', item_categories)
        """ Retrieve all categories associated with current Item """
        categories = ItemMethod.category_method_get_all_categories_order_by_name('asc')
        print('categories: ', categories)
        """ Retrieve all Items in DB """

        if request.method == 'GET':
            return render_template('item/edit_item.html',
                                   item=item,
                                   item_categories=item_categories,
                                   categories=categories,
                                   title='Edit Item - %s' % item_name)
        elif request.method == 'POST':
            validate_create_item = ValidateCreateUpdateForm(request.form)
            if validate_create_item.validate():
                # new_name = request.form.get('name')
                # new_description = request.form.get('description')
                # new_price = request.form.get('price')
                new_name = validate_create_item.name.data
                new_description = validate_create_item.description.data
                new_price = validate_create_item.price.data
                new_categories_selected = request.form.getlist('item_list')

                item_id = ItemMethod.get_id_by_name(item_name)
                # Update new Item
                ItemMethod.update_item(item_id=item_id,
                                       new_name=new_name,
                                       new_description=new_description,
                                       new_price=new_price,
                                       new_categories=new_categories_selected)
                """ update_item """

                flash('New Item (%s) has been created successfully' % new_name)
            return redirect(url_for('catalog_bp.index'))
    else:
        flash('Current user is not owner of selected Item...')
        return redirect(url_for('catalog_bp.index'))


@item_bp.route('/item/delete/<string:item_name>/confirmation', methods=['GET'])
@login_required
def delete_confirmation(item_name):
    print('----------------- Item - delete_confirmation - %s' % request.method)
    return render_template('item/confirm_delete_item.html',
                           title='Confirm Item Delete',
                           subtitle='CRUD Operation',
                           item_name=item_name)


@item_bp.route('/item/delete/<string:item_name>', methods=['GET'])
@login_required
def delete(item_name):
    print('----------------- Item - delete - %s' % request.method)

    """ Validate if current_user is the owner of item_name """
    item_owner_db_id = ItemMethod.get_owner_by_name(item_name)
    current_session_user_id = ItemMethod.auth_method_get_current_user_id()

    if item_owner_db_id == current_session_user_id:
        """ Load item to be edited """
        print('Item - delete - GET')
        item_id = ItemMethod.get_id_by_name(item_name)
        """ item_id by provided item_name """
        categories_id_of_item = ItemMethod.catalog_method_get_all_categories_id_of_item_id(item_id)
        """ All categories_id of a item_id """
        ItemMethod.delete_by_id(item_id)
        """ Delete Item """
        ItemMethod.catalog_method_delete_list_of_item_categories(item_id, categories_id_of_item)
        """ Delete all links of items with a specified item_id """
        return redirect(url_for('catalog_bp.index'))
    else:
        flash('Current user is not owner of selected Item...')
        return redirect(url_for('catalog_bp.index'))

# ------------- Falta validar las operaciones cuando 'Category', 'Item', 'Catalog' y 'Auth' ya existen en la BD
