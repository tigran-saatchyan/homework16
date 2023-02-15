from datetime import datetime

from app import app, db


def commit_updated_data(data, table):
    """
    Update data and commit
    :param data:    - data for update
    :param table:   - table to be updated
    """
    with app.app_context():
        for k, v in data.items():
            setattr(table, k, v)
            db.session.add(table)
            db.session.commit()


def delete_row(row_data):
    with app.app_context():
        db.session.delete(row_data)
        db.session.commit()


def convert_date_format(data):
    result = []

    for dict_element in data:
        temp_dict = {}
        for k, v in dict_element.items():
            if k not in ('start_date', 'end_date'):
                temp_dict[k] = v
            else:
                temp_dict[k] = datetime.strptime(v, '%m/%d/%Y').date()
        result.append(temp_dict)
    return result
