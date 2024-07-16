from .models import db, Flagged

def create_flag(type, type_id, reason):
    # Create flag
    flag = Flagged(type=type, type_id=type_id, reason=reason)
    db.session.add(flag)
    db.session.commit()
    return flag

def get_flag(type_id, type):
    # Get flag
    flag = Flagged.query.filter_by(type_id=type_id, type=type).first()
    return flag

def delete_flag(type, type_id):
    # Delete flag
    flag = get_flag(type_id, type)
    if flag.type != type: return None
    db.session.delete(flag)
    db.session.commit()
    return flag

def get_flags(page):
    # Get all flags
    if page == -1:
        flags = Flagged.query.all()
        return flags
    flags = Flagged.query.paginate(page=page, per_page=5, error_out=False)
    return flags