"""
File Path: application/modules/category/views.py
Description: Category routes/paths for App - Define Category routes/paths
Copyright (c) 2019. This Application has been developed by OR73.
"""
from flask import Blueprint, flash, json, jsonify, redirect, render_template, request, url_for
from flask_login import login_required

# from setup import db
from application.setup import db

# Methods
from ..category import (CategoryMethod, ValidateCreateUpdateForm)

category_bp = Blueprint('category_bp', __name__)


@category_bp.route('/category/<string:category_name>/')
def show_category(category_name):
    """Public route - shows Category detailed information"""
    print('--------------- Category - show_category')
    # Validate if the category provided exists in DB
    category = CategoryMethod.get_category_by_name(category_name)
    if category:
        print('The Category %s exist' % category_name)
        # Get all items of category
        items = CategoryMethod.catalog_method_get_all_items_name_by_provided_category_id(category.get_id())
        # items = CategoryMethod.catalog_method_get_all_items_id_of_category_id(category.get_id())
        return render_template('category/show_category.html',
                               title=category_name,
                               subtitle='Category Details',
                               category=category,
                               items=items)
    else:
        flash('Required category (%s) doesn\'t exist')
        return redirect(url_for('catalog_bp.index'))


@category_bp.route('/category/new/', methods=['GET', 'POST'])
@login_required
def create():
    print('---------------- Category - create_category - %s' % request.method)
    if request.method == 'GET':
        items = CategoryMethod.item_method_get_all_items_order_by_name('asc')
        return render_template('category/create_category.html', items=items)

    elif request.method == 'POST':
        validate_create_form = ValidateCreateUpdateForm(request.form)
        if validate_create_form.validate():
            # name = request.form.get('name')
            # description = request.form.get('description')
            # items_selected = request.form.getlist('item_list')
            name = validate_create_form.name.data
            description = validate_create_form.description.data
            items_selected = request.form.getlist('item_list')
            print('name: ', name)
            print('description: ', description)

            print('items_selected: ', items_selected)
            print('request.form.getlist(item_list): ', request.form.getlist('item_list'))

            # Create new category
            CategoryMethod.create_category(name=name,
                                           description=description,
                                           owner=CategoryMethod.auth_method_get_current_user_id())
            # Add items to Category
            for item in items_selected:
                CategoryMethod.catalog_method_create_catalog(
                    category_id=CategoryMethod.get_id_by_name(name),
                    item_id=CategoryMethod.item_method_get_id_by_name(item))

                # db.session.add(new_catalog)
                # db.session.commit()
            flash('New Category (%s) has been created successfully' % name)
            return redirect(url_for('catalog_bp.index'))

    flash('Required operation is not authorized')
    return redirect(url_for('catalog_bp.index'))


@category_bp.route('/category/edit/<string:category_name>', methods=['GET', 'POST'])
@login_required
def edit(category_name):
    print('----------------- Category - edit - %s' % request.method)
    category = CategoryMethod.get_category_by_name(category_name)

    """ Validate if current_user is the owner of category_name """
    category_owner_db_id = CategoryMethod.get_owner_by_name(category_name)
    current_session_user_id = CategoryMethod.auth_method_get_current_user_id()

    if category_owner_db_id == current_session_user_id:
        """ Load category to be edited """
        category_items = CategoryMethod.catalog_method_get_all_items_name_by_provided_category_id(category.get_id())
        # category_items = CategoryMethod.catalog_method_get_all_items_id_of_category_id(category.get_id())
        print('category_items: ', category_items)
        """ Retrieve all items associated with current Category """
        items = CategoryMethod.item_method_get_all_items_order_by_name('asc')
        print('items: ', items)
        """ Retrieve all Items in DB """

        if request.method == 'GET':
            return render_template('category/edit_category.html',
                                   category=category,
                                   category_items=category_items,
                                   items=items,
                                   title='Edit Category - %s' % category_name)
        elif request.method == 'POST':
            validate_create_form = ValidateCreateUpdateForm(request.form)
            if validate_create_form.validate():
                # new_name = request.form.get('name')
                # new_description = request.form.get('description')
                new_name = validate_create_form.name.data
                new_description = validate_create_form.description.data
                new_items_selected = request.form.getlist('item_list')

                category_id = CategoryMethod.get_id_by_name(category_name)
                print('-------------*********** category_id: ', category_id)
                # Update new category
                CategoryMethod.update_category(category_id=category_id,
                                               new_name=new_name,
                                               new_description=new_description,
                                               new_items=new_items_selected)
                """ update_category """

                flash('New Category (%s) has been created successfully' % new_name)
            return redirect(url_for('catalog_bp.index'))
    else:
        flash('Current user is not owner of selected Category...')
        return redirect(url_for('catalog_bp.index'))


@category_bp.route('/category/delete/<string:category_name>/confirmation', methods=['GET'])
@login_required
def delete_confirmation(category_name):
    print('----------------- Category - delete_confirmation - %s' % request.method)
    return render_template('category/confirm_delete_category.html',
                           title='Confirm Category Delete',
                           subtitle='CRUD Operation',
                           category_name=category_name)


@category_bp.route('/category/delete/<string:category_name>', methods=['GET', 'POST'])
@login_required
def delete(category_name):
    print('----------------- Category - delete - %s' % request.method)

    """ Validate if current_user is the owner of category_name """
    category_owner_db_id = CategoryMethod.get_owner_by_name(category_name)
    current_session_user_id = CategoryMethod.auth_method_get_current_user_id()

    if category_owner_db_id == current_session_user_id:
        """ Load category to be edited """
        print('Category - delete - GET')
        category_id = CategoryMethod.get_id_by_name(category_name)
        """ category_id by provided category_name """
        items_id_of_category = CategoryMethod.catalog_method_get_all_items_id_of_category_id(category_id)
        """ All items_id of a category_id """
        CategoryMethod.delete_by_id(category_id)
        """ Delete Category """
        CategoryMethod.catalog_method_delete_list_of_category_items(category_id, items_id_of_category)
        """ Delete all links of items with a specified category_id """
        return redirect(url_for('catalog_bp.index'))
    else:
        flash('Current user is not owner of selected Category...')
        return redirect(url_for('catalog_bp.index'))
